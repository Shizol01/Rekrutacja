from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from core.models import Employee, Device
from time_tracking.models import TimeEvent
from time_tracking.services.event_service import register_event


@pytest.mark.django_db
class TestEventService:
    @pytest.fixture
    def employee(self):
        return Employee.objects.create(
            first_name="Jan",
            last_name="Kowalski",
        )

    @pytest.fixture
    def device(self):
        return Device.objects.create(
            name="Tablet 1",
            device_id="tablet-1",
        )

    def test_toilet_event_requires_working_state(self, employee, device, monkeypatch):
        start = timezone.make_aware(datetime(2025, 2, 1, 9, 0))
        toilet_time = timezone.make_aware(datetime(2025, 2, 1, 9, 10))

        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: start,
        )
        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: start,
        )

        register_event(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            device=device,
        )

        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: toilet_time,
        )
        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: toilet_time,
        )

        event, message = register_event(
            employee=employee,
            event_type=TimeEvent.TOILET,
            device=device,
        )

        assert event is not None
        assert event.is_anomaly is False
        assert message == "Zarejestrowano wyjście do toalety"

    def test_toilet_event_on_break_marks_anomaly(self, employee, device, monkeypatch):
        start = timezone.make_aware(datetime(2025, 2, 2, 9, 0))
        break_start = timezone.make_aware(datetime(2025, 2, 2, 10, 0))
        toilet_time = timezone.make_aware(datetime(2025, 2, 2, 10, 5))

        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: start,
        )
        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: start,
        )
        register_event(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            device=device,
        )

        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: break_start,
        )
        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: break_start,
        )
        register_event(
            employee=employee,
            event_type=TimeEvent.BREAK_START,
            device=device,
        )

        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: toilet_time,
        )
        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: toilet_time,
        )

        event, message = register_event(
            employee=employee,
            event_type=TimeEvent.TOILET,
            device=device,
        )

        assert event is not None
        assert event.is_anomaly is True
        assert event.anomaly_reason == "Wyjście do toalety poza czasem pracy"
        assert "anomalia" in message

    def test_overnight_check_in_blocks_new_check_in(self, employee, device, monkeypatch):
        day_one = timezone.make_aware(datetime(2025, 2, 3, 9, 0))
        next_morning = day_one + timedelta(days=1)

        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: day_one,
        )
        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: day_one,
        )

        first_event, first_message = register_event(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            device=device,
        )
        assert first_event is not None
        assert first_message == "Rozpoczęto pracę"

        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: next_morning,
        )
        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: next_morning,
        )

        second_event, second_message = register_event(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            device=device,
        )

        refreshed_check_in = TimeEvent.objects.get(id=first_event.id)

        assert second_event is None
        assert second_message == "Brak zakończenia poprzedniej zmiany"
        assert refreshed_check_in.is_anomaly is True
        assert "Brak CHECK_OUT" in refreshed_check_in.anomaly_reason
