from django.utils import timezone
from time_tracking.models import TimeEvent
from time_tracking.services.tablet_state import get_employee_state


def register_event(employee, event_type, device):
    state = get_employee_state(employee)
    now = timezone.now()

    last_check_in = (
        TimeEvent.objects.filter(employee=employee, event_type=TimeEvent.CHECK_IN)
        .order_by("-timestamp", "-id")
        .first()
    )
    if last_check_in:
        has_checkout_after = TimeEvent.objects.filter(
            employee=employee,
            event_type=TimeEvent.CHECK_OUT,
            timestamp__gt=last_check_in.timestamp,
        ).exists()
        if not has_checkout_after and last_check_in.timestamp.date() < now.date():
            last_check_in.is_anomaly = True
            last_check_in.anomaly_reason = "Brak CHECK_OUT z poprzedniego dnia"
            last_check_in.save(update_fields=["is_anomaly", "anomaly_reason"])
            return None, "Brak zakończenia poprzedniej zmiany"

    if device is None:
        return None, "Nieznane urządzenie"

    if not device.is_active:
        return None, "Nieaktywne urządzenie"

    # ===== CHECK IN =====
    if event_type == TimeEvent.CHECK_IN:
        if TimeEvent.objects.filter(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            timestamp__date=now.date(),
        ).exists():
            return None, "Praca już rozpoczęta dzisiaj"

        if state.state != "OFF_DUTY":
            return None, "Praca już rozpoczęta"

        return TimeEvent.objects.create(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            device=device,
            timestamp=now,
        ), "Rozpoczęto pracę"

    # ===== BREAK START /  =====
    if event_type == TimeEvent.BREAK_START:
        if state.state != "WORKING":
            return None, "Nie można rozpocząć przerwy"

        return TimeEvent.objects.create(
            employee=employee,
            event_type=TimeEvent.BREAK_START,
            device=device,
            timestamp=now,
        ), "Rozpoczęto przerwę"

    # ===== BREAK END =====
    if event_type == TimeEvent.BREAK_END:
        if state.state != "ON_BREAK":
            return None, "Nie ma aktywnej przerwy"

        return TimeEvent.objects.create(
            employee=employee,
            event_type=TimeEvent.BREAK_END,
            device=device,
            timestamp=now,
        ), "Zakończono przerwę"

    # ===== CHECK OUT =====
    if event_type == TimeEvent.CHECK_OUT:
        if state.state not in ["WORKING", "ON_BREAK"]:
            return None, "Nie pracujesz"

        return TimeEvent.objects.create(
            employee=employee,
            event_type=TimeEvent.CHECK_OUT,
            device=device,
            timestamp=now,
        ), "Zakończono pracę"

    # ===== TOILET =====
    if event_type == TimeEvent.TOILET:
        is_anomaly = state.state != "WORKING"
        anomaly_reason = ""
        if is_anomaly:
            anomaly_reason = "Wyjście do toalety poza czasem pracy"

        event = TimeEvent.objects.create(
            employee=employee,
            event_type=TimeEvent.TOILET,
            device=device,
            timestamp=now,
            is_anomaly=is_anomaly,
            anomaly_reason=anomaly_reason,
        )
        if is_anomaly:
            return event, "Zarejestrowano wyjście do toalety (anomalia)"
        return event, "Zarejestrowano wyjście do toalety"

    return None, "Nieznany typ zdarzenia"
