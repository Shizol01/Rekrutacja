from datetime import datetime

import pytest
from django.utils import timezone

from core.models import Employee, Device
from time_tracking.models import TimeEvent
from time_tracking.services.event_service import register_event
from time_tracking.services.tablet_state import get_employee_state


@pytest.mark.django_db
class TestTabletState:
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

    def test_prevent_multiple_check_in_same_day(self, employee, device, monkeypatch):
        now = timezone.make_aware(datetime(2025, 1, 1, 9, 0))
        monkeypatch.setattr(
            "time_tracking.services.event_service.timezone.now",
            lambda: now,
        )

        first_event, first_msg = register_event(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            device_id=device.device_id,
        )

        second_event, second_msg = register_event(
            employee=employee,
            event_type=TimeEvent.CHECK_IN,
            device_id=device.device_id,
        )

        assert first_event is not None
        assert first_msg == "Rozpoczęto pracę"
        assert second_event is None
        assert second_msg == "Praca już rozpoczęta dzisiaj"
        assert TimeEvent.objects.filter(employee=employee).count() == 1

    def test_work_and_break_time_after_check_out_stops_growing(
        self, employee, device, monkeypatch
    ):
        check_in = timezone.make_aware(datetime(2025, 1, 2, 8, 0))
        check_out = timezone.make_aware(datetime(2025, 1, 2, 16, 0))
        now_after = timezone.make_aware(datetime(2025, 1, 2, 18, 0))

        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.CHECK_IN,
            timestamp=check_in,
        )
        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.CHECK_OUT,
            timestamp=check_out,
        )

        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: now_after,
        )

        state = get_employee_state(employee, day=check_in.date())

        assert state.state == "OFF_DUTY"
        assert state.work_minutes == 480
        assert state.break_minutes == 0
        assert state.break_started_at is None
        assert state.minutes_on_break is None

    def test_open_break_without_check_out(self, employee, device, monkeypatch):
        check_in = timezone.make_aware(datetime(2025, 1, 3, 9, 0))
        break_start = timezone.make_aware(datetime(2025, 1, 3, 10, 0))
        now_on_break = timezone.make_aware(datetime(2025, 1, 3, 10, 30))

        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.CHECK_IN,
            timestamp=check_in,
        )
        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.BREAK_START,
            timestamp=break_start,
        )

        monkeypatch.setattr(
            "time_tracking.services.tablet_state.timezone.now",
            lambda: now_on_break,
        )

        state = get_employee_state(employee, day=check_in.date())

        assert state.state == "ON_BREAK"
        assert state.work_minutes == 60
        assert state.break_minutes == 30
        assert state.break_started_at == "10:00"
        assert state.minutes_on_break == 30
