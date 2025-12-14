from django.utils import timezone
from django.db import transaction

from core.models import Employee, Device
from time_tracking.models import TimeEvent


class EventLogicError(Exception):
    """Błąd logiki zdarzeń (do zwrócenia jako 400 w API)."""
    pass


@transaction.atomic
def register_event(*, employee: Employee, device: Device, event_type: str) -> TimeEvent:
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_events = TimeEvent.objects.filter(
        employee=employee,
        timestamp__gte=today_start,
    ).order_by("timestamp")

    last_event = today_events.last()

    is_anomaly = False
    anomaly_reason = ""

    # --- LOGIKA ---
    if event_type == TimeEvent.CHECK_IN:
        if last_event and last_event.event_type == TimeEvent.CHECK_IN:
            is_anomaly = True
            anomaly_reason = "Multiple CHECK_IN in the same day"

    elif event_type == TimeEvent.CHECK_OUT:
        if not last_event or last_event.event_type != TimeEvent.CHECK_IN:
            raise EventLogicError("CHECK_OUT without CHECK_IN")

    elif event_type == TimeEvent.BREAK_START:
        if not last_event or last_event.event_type != TimeEvent.CHECK_IN:
            raise EventLogicError("BREAK_START without active CHECK_IN")

    elif event_type == TimeEvent.BREAK_END:
        if not last_event or last_event.event_type != TimeEvent.BREAK_START:
            raise EventLogicError("BREAK_END without BREAK_START")

    # --- ZAPIS ---
    return TimeEvent.objects.create(
        employee=employee,
        device=device,
        event_type=event_type,
        timestamp=now,
        is_anomaly=is_anomaly,
        anomaly_reason=anomaly_reason,
    )
