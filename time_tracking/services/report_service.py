from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Optional

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from core.models import Employee
from time_tracking.models import TimeEvent, WorkSchedule


def _get_late_threshold_minutes() -> int:
    # Możesz ustawić w settings.py: LATE_THRESHOLD_MINUTES = 5
    return int(getattr(settings, "LATE_THRESHOLD_MINUTES", 5))


def _daterange(d_from: date, d_to: date):
    cur = d_from
    while cur <= d_to:
        yield cur
        cur += timedelta(days=1)


def _day_start_end(d: date):
    start = datetime.combine(d, time.min)
    end = datetime.combine(d, time.max)
    # Uwaga: dla SQLite i MVP zostawiamy naiwne datetimes; jeśli masz USE_TZ=True,
    # Django i tak trzyma timezone-aware w DB. Najprościej filtrować po dacie:
    return start, end


def _pair_breaks(events: list[TimeEvent]) -> tuple[int, list[dict[str, Any]]]:
    """
    Zwraca (break_minutes, anomalies_for_breaks)
    Liczymy tylko kompletne pary BREAK_START->BREAK_END.
    """
    break_minutes = 0
    anomalies: list[dict[str, Any]] = []

    open_break_start: Optional[TimeEvent] = None
    for ev in events:
        if ev.event_type == TimeEvent.BREAK_START:
            if open_break_start is not None:
                anomalies.append({"type": "BREAK_START_WHILE_BREAK_OPEN", "detail": "Break already started"})
            else:
                open_break_start = ev

        elif ev.event_type == TimeEvent.BREAK_END:
            if open_break_start is None:
                anomalies.append({"type": "BREAK_END_WITHOUT_START", "detail": "Break end without break start"})
            else:
                delta = ev.timestamp - open_break_start.timestamp
                mins = int(delta.total_seconds() // 60)
                if mins > 0:
                    break_minutes += mins
                open_break_start = None

    if open_break_start is not None:
        anomalies.append({"type": "BREAK_WITHOUT_END", "detail": "Break started but not ended"})

    return break_minutes, anomalies


def _detect_event_anomalies(day_events: list[TimeEvent]) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []

    # to, co już zapisujesz w zdarzeniu:
    for ev in day_events:
        if ev.is_anomaly:
            anomalies.append({"type": "EVENT_ANOMALY", "detail": ev.anomaly_reason or "Unknown anomaly"})

    check_ins = [e for e in day_events if e.event_type == TimeEvent.CHECK_IN]
    check_outs = [e for e in day_events if e.event_type == TimeEvent.CHECK_OUT]

    if len(check_ins) > 1:
        anomalies.append({"type": "MULTIPLE_CHECK_IN", "detail": "More than one CHECK_IN in the same day"})
    if len(check_outs) > 1:
        anomalies.append({"type": "MULTIPLE_CHECK_OUT", "detail": "More than one CHECK_OUT in the same day"})

    if check_outs and not check_ins:
        anomalies.append({"type": "CHECK_OUT_WITHOUT_CHECK_IN", "detail": "Check out exists but no check in"})

    if check_ins and not check_outs:
        anomalies.append({"type": "MISSING_CHECK_OUT", "detail": "Check in exists but no check out"})

    return anomalies


def build_attendance_report(*, date_from: date, date_to: date, employee_id: int | None = None) -> dict[str, Any]:
    employees: QuerySet[Employee] = Employee.objects.filter(is_active=True).order_by("last_name", "first_name")
    if employee_id is not None:
        employees = employees.filter(id=employee_id)

    threshold = _get_late_threshold_minutes()

    report: dict[str, Any] = {
        "range": {"from": str(date_from), "to": str(date_to)},
        "late_threshold_minutes": threshold,
        "employees": [],
    }

    for emp in employees:
        # Grafik w zakresie
        schedules = {
            s.date: s
            for s in WorkSchedule.objects.filter(employee=emp, date__gte=date_from, date__lte=date_to)
        }

        # Zdarzenia w zakresie (po timestamp)
        events_qs = TimeEvent.objects.filter(
            employee=emp,
            timestamp__date__gte=date_from,
            timestamp__date__lte=date_to,
        ).order_by("timestamp")

        # grupowanie per dzień
        events_by_day: dict[date, list[TimeEvent]] = {}
        for ev in events_qs:
            d = ev.timestamp.date()
            events_by_day.setdefault(d, []).append(ev)

        emp_days: list[dict[str, Any]] = []
        totals = {
            "planned_minutes": 0,
            "worked_minutes": 0,
            "break_minutes": 0,
            "late_minutes": 0,
            "absences": 0,
            "leave_days": 0,
            "anomaly_days": 0,
        }

        for d in _daterange(date_from, date_to):
            schedule = schedules.get(d)
            day_events = events_by_day.get(d, [])

            day_type = schedule.day_type if schedule else "NO_SCHEDULE"
            planned_minutes = 0
            planned_start = None
            planned_end = None

            if schedule and schedule.day_type == WorkSchedule.WORK:
                planned_start = schedule.planned_start
                planned_end = schedule.planned_end
                planned_minutes = int(
                    (
                            datetime.combine(d, planned_end) - datetime.combine(d, planned_start)
                    ).total_seconds()
                    // 60
                )
                totals["planned_minutes"] += planned_minutes

            if schedule and schedule.day_type == WorkSchedule.LEAVE:
                totals["leave_days"] += 1

            # Faktyczne
            check_in = next((e for e in day_events if e.event_type == TimeEvent.CHECK_IN), None)
            check_out = next((e for e in reversed(day_events) if e.event_type == TimeEvent.CHECK_OUT), None)

            worked_minutes = 0
            break_minutes = 0
            lateness_minutes = 0

            anomalies = _detect_event_anomalies(day_events)

            if check_in and check_out and check_out.timestamp > check_in.timestamp:
                span_minutes = int((check_out.timestamp - check_in.timestamp).total_seconds() // 60)
                break_minutes, break_anoms = _pair_breaks(day_events)
                anomalies.extend(break_anoms)
                worked_minutes = max(0, span_minutes - break_minutes)
                totals["worked_minutes"] += worked_minutes
                totals["break_minutes"] += break_minutes

            # Spóźnienie
            if schedule and schedule.day_type == WorkSchedule.WORK and check_in and planned_start:
                planned_dt = datetime.combine(d, planned_start)
                # jeśli USE_TZ=True, check_in.timestamp jest aware -> ujednolicamy:
                if timezone.is_aware(check_in.timestamp) and timezone.is_naive(planned_dt):
                    planned_dt = timezone.make_aware(planned_dt, timezone.get_current_timezone())

                diff = int((check_in.timestamp - planned_dt).total_seconds() // 60)
                if diff > threshold:
                    lateness_minutes = diff
                    totals["late_minutes"] += lateness_minutes

            # Absencja
            is_absence = False
            if schedule and schedule.day_type == WorkSchedule.WORK and not check_in:
                is_absence = True
                totals["absences"] += 1

            if anomalies:
                totals["anomaly_days"] += 1

            emp_days.append(
                {
                    "date": str(d),
                    "day_type": day_type,
                    "planned": {
                        "start": str(planned_start) if planned_start else None,
                        "end": str(planned_end) if planned_end else None,
                        "minutes": planned_minutes,
                    },
                    "actual": {
                        "check_in": check_in.timestamp.isoformat() if check_in else None,
                        "check_out": check_out.timestamp.isoformat() if check_out else None,
                        "worked_minutes": worked_minutes,
                        "break_minutes": break_minutes,
                    },
                    "lateness_minutes": lateness_minutes,
                    "absence": is_absence,
                    "anomalies": anomalies,
                }
            )

        report["employees"].append(
            {
                "employee": {"id": emp.id, "name": str(emp)},
                "totals": totals,
                "days": emp_days,
            }
        )

    return report
