from datetime import date

from django.utils import timezone

from core.models import Employee
from time_tracking.models import TimeEvent, WorkSchedule
from time_tracking.services.tablet_state import get_employee_state

STATUS_LABELS = {
    "WORKING": "Pracuje",
    "ON_BREAK": "Przerwa",
    "OFF_DUTY": "Poza pracą",
    "ABSENT": "Nieobecny",
}



def _fmt_hm(dt):
    if not dt:
        return None
    return timezone.localtime(dt).strftime("%H:%M")


def get_live_dashboard(day: date | None = None):
    """
    Zwraca listę słowników – po jednym na pracownika – ze stanem DZISIAJ
    """
    if day is None:
        day = timezone.localdate()

    now = timezone.now()
    rows = []

    employees = Employee.objects.all().order_by("last_name", "first_name")

    for employee in employees:
        # ===== GRAFIK =====
        schedule = WorkSchedule.objects.filter(
            employee=employee,
            date=day
        ).first()

        # ===== EVENTY =====
        events = list(
            TimeEvent.objects.filter(
                employee=employee,
                timestamp__date=day
            ).order_by("timestamp", "id")
        )

        state = get_employee_state(employee, day)

        # ===== STATUS =====
        if schedule and schedule.day_type == WorkSchedule.WORK and not events:
            status = "ABSENT"
        else:
            status = state.state

        # ===== GODZINY =====
        check_in = next(
            (e for e in reversed(events) if e.event_type == TimeEvent.CHECK_IN),
            None
        )

        check_out = next(
            (e for e in reversed(events) if e.event_type == TimeEvent.CHECK_OUT),
            None
        )

        in_time = _fmt_hm(check_in.timestamp) if check_in else None
        out_time = _fmt_hm(check_out.timestamp) if check_out else None

        # ===== CZAS OD WEJŚCIA =====
        total_minutes = 0
        if check_in:
            total_minutes = int(
                (now - check_in.timestamp).total_seconds() // 60
            )

        # ===== CZAS PRZERW =====
        break_minutes = 0
        open_break = None

        for e in events:
            if e.event_type == TimeEvent.BREAK_START:
                open_break = e
            elif e.event_type == TimeEvent.BREAK_END and open_break:
                break_minutes += int(
                    (e.timestamp - open_break.timestamp).total_seconds() // 60
                )
                open_break = None

        # jeśli przerwa otwarta – licz do teraz
        if open_break:
            break_minutes += int(
                (now - open_break.timestamp).total_seconds() // 60
            )

        # ===== CZAS PRACY NETTO =====
        work_minutes = max(total_minutes - break_minutes, 0)

        # ===== ANOMALIE =====
        anomalies = []

        if check_in and not check_out:
            ANOMALY_LABELS = {
                "BRAK_CHECK_OUT": "Brak zakończenia pracy",
                "OTWARTA_PRZERWA": "Niezakończona przerwa",
                "EVENT_BEZ_CHECK_IN": "Zdarzenie bez rozpoczęcia pracy",
            }

            anomalies.append(ANOMALY_LABELS["BRAK_CHECK_OUT"])

        if open_break:
            anomalies.append("OTWARTA_PRZERWA")

        if not check_in and events:
            anomalies.append("EVENT_BEZ_CHECK_IN")

        # ===== OSTATNIA AKCJA =====
        last_event = events[-1] if events else None
        ACTION_LABELS = {
            TimeEvent.CHECK_IN: "Rozpoczęcie pracy",
            TimeEvent.CHECK_OUT: "Zakończenie pracy",
            TimeEvent.BREAK_START: "Rozpoczęcie przerwy",
            TimeEvent.BREAK_END: "Zakończenie przerwy",
        }

        last_action = ACTION_LABELS.get(
            last_event.event_type,
            last_event.event_type
        ) if last_event else None

        rows.append({
            "employee_id": employee.id,
            "employee": str(employee),
            "in_time": in_time,
            "out_time": out_time,
            "total_minutes": total_minutes,
            "work_minutes": work_minutes,
            "break_minutes": break_minutes,
            "last_action": last_action,
            "anomalies": anomalies,
            "status": status,
            "status_label": STATUS_LABELS.get(status, status),
        })

    return rows
