from dataclasses import dataclass

from django.utils import timezone

from time_tracking.models import TimeEvent


@dataclass(frozen=True)
class EmployeeState:
    state: str  # OFF_DUTY | WORKING | ON_BREAK
    started_at: str | None  # "HH:MM"
    work_minutes: int | None
    break_minutes: int | None
    break_started_at: str | None
    minutes_on_break: int | None
    last_event_type: str | None
    last_action: str | None
    last_event_timestamp: str | None
    minutes_since_start: int | None
    last_was_toilet: bool


def _fmt_hm(dt):
    if not dt:
        return None
    local_dt = timezone.localtime(dt)
    return local_dt.strftime("%H:%M")


def _get_last_action(event):
    actions = {
        TimeEvent.CHECK_IN: "Rozpoczęto pracę",
        TimeEvent.BREAK_START: "Rozpoczęcie przerwy",
        TimeEvent.BREAK_END: "Zakończenie przerwy",
        TimeEvent.CHECK_OUT: "Zakończenie pracy",
        TimeEvent.TOILET: "Wyjście do toalety",
    }
    return actions.get(event.event_type, "Brak akcji")


def get_employee_state(employee, day=None):
    if day is None:
        day = timezone.localdate()

    events = list(
        TimeEvent.objects
        .filter(employee=employee, timestamp__date=day)
        .order_by("timestamp", "id")
    )

    if not events:
        return EmployeeState(
            "OFF_DUTY", None, None, None, None, None, None, None, None, None, False
        )

    last_event = events[-1]

    last_check_in = None
    for e in reversed(events):
        if e.event_type == TimeEvent.CHECK_IN:
            last_check_in = e
            break

    if not last_check_in:
        return EmployeeState(
            "OFF_DUTY", None, None, None, None, None, None, None, None, None, False
        )

    end_time = timezone.now()
    if last_event.event_type == TimeEvent.CHECK_OUT:
        end_time = last_event.timestamp

    # czas pracy w minutach
    total_minutes = int(
        (end_time - last_check_in.timestamp).total_seconds() // 60
    )

    # sprawdzenie przerwy
    break_start = None
    break_minutes = 0
    for e in events:
        if e.timestamp < last_check_in.timestamp:
            continue
        if e.event_type == TimeEvent.BREAK_START:
            break_start = e
        elif e.event_type == TimeEvent.BREAK_END:
            if break_start:
                break_minutes += int(
                    (min(e.timestamp, end_time) - break_start.timestamp)
                    .total_seconds() // 60
                )
            break_start = None

    minutes_on_break = None
    if break_start and break_start.timestamp < end_time:
        minutes_on_break = int(
            (end_time - break_start.timestamp).total_seconds() // 60
        )
        break_minutes += minutes_on_break

    if last_event.event_type == TimeEvent.CHECK_OUT:
        state = "OFF_DUTY"
    elif break_start:
        state = "ON_BREAK"
    else:
        state = "WORKING"

    return EmployeeState(
        state=state,
        started_at=_fmt_hm(last_check_in.timestamp),
        work_minutes=max(total_minutes - break_minutes, 0),
        break_minutes=break_minutes if break_minutes else 0,
        break_started_at=_fmt_hm(break_start.timestamp) if state == "ON_BREAK" else None,
        minutes_on_break=minutes_on_break if state == "ON_BREAK" else None,
        last_event_type=last_event.event_type,
        last_action=_get_last_action(last_event),
        last_event_timestamp=timezone.localtime(last_event.timestamp).isoformat(),
        minutes_since_start=total_minutes,
        last_was_toilet=last_event.event_type == TimeEvent.TOILET,
    )
