from datetime import date, time, datetime

import pytest
from django.utils import timezone

from core.models import Employee, Device
from time_tracking.models import WorkSchedule, TimeEvent
from time_tracking.services.report_service import build_attendance_report


@pytest.mark.django_db
class TestAttendanceReport:

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

    def test_work_day_with_worked_time(self, employee, device):
        d = date(2025, 12, 14)

        WorkSchedule.objects.create(
            employee=employee,
            date=d,
            day_type=WorkSchedule.WORK,
            planned_start=time(8, 0),
            planned_end=time(16, 0),
        )

        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.CHECK_IN,
            timestamp=timezone.make_aware(datetime(2025, 12, 14, 8, 0)),
        )

        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.CHECK_OUT,
            timestamp=timezone.make_aware(datetime(2025, 12, 14, 16, 0)),
        )

        report = build_attendance_report(
            date_from=d,
            date_to=d,
            employee_id=employee.id,
        )

        day = report["employees"][0]["days"][0]

        assert day["planned"]["minutes"] == 480
        assert day["actual"]["worked_minutes"] == 480
        assert day["absence"] is False

    def test_no_schedule_day_with_work(self, employee, device):
        d = date(2025, 12, 15)

        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.CHECK_IN,
            timestamp=timezone.make_aware(datetime(2025, 12, 15, 9, 0)),
        )

        TimeEvent.objects.create(
            employee=employee,
            device=device,
            event_type=TimeEvent.CHECK_OUT,
            timestamp=timezone.make_aware(datetime(2025, 12, 15, 17, 0)),
        )

        report = build_attendance_report(
            date_from=d,
            date_to=d,
            employee_id=employee.id,
        )

        day = report["employees"][0]["days"][0]

        assert day["day_type"] == "NO_SCHEDULE"
        assert day["actual"]["worked_minutes"] == 480
        assert day["absence"] is False

    def test_absence_on_work_day(self, employee):
        d = date(2025, 12, 16)

        WorkSchedule.objects.create(
            employee=employee,
            date=d,
            day_type=WorkSchedule.WORK,
            planned_start=time(8, 0),
            planned_end=time(16, 0),
        )

        report = build_attendance_report(
            date_from=d,
            date_to=d,
            employee_id=employee.id,
        )

        day = report["employees"][0]["days"][0]

        assert day["absence"] is True
        assert day["actual"]["worked_minutes"] == 0
