from dataclasses import dataclass
from datetime import date
from django.utils import timezone

from time_tracking.models import TimeEvent


@dataclass(frozen=True)
class EmployeeState:
    state: str                  # OFF_DUTY | WORKING | ON_BREAK
    started_at: str | None      # "HH:MM"
    work_minutes: int | None
    last_event_type: str | None
    last_action: str | None


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
        return EmployeeState("OFF_DUTY", None, None, None, None)

    last_event = events[-1]

    last_check_in = None
    for e in reversed(events):
        if e.event_type == TimeEvent.CHECK_IN:
            last_check_in = e
            break

    if not last_check_in:
        return EmployeeState("OFF_DUTY", None, None, None, None)

    # czas pracy w minutach
    total_minutes = int(
        (timezone.now() - last_check_in.timestamp).total_seconds() // 60
    )

    # sprawdzenie przerwy
    break_start = None
    for e in events:
        if e.timestamp < last_check_in.timestamp:
            continue
        if e.event_type == TimeEvent.BREAK_START:
            break_start = e
        elif e.event_type == TimeEvent.BREAK_END:
            break_start = None

    if last_event.event_type == TimeEvent.CHECK_OUT:
        state = "OFF_DUTY"
    elif break_start:
        state = "ON_BREAK"
    else:
        state = "WORKING"

    return EmployeeState(
        state=state,
        started_at=_fmt_hm(last_check_in.timestamp),
        work_minutes=total_minutes,
        last_event_type=last_event.event_type,
        last_action=_get_last_action(last_event),
    )

