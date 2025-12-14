import os
import django
from datetime import date, time, datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rekrutacja.settings")
django.setup()

from django.utils import timezone

from core.models import Employee, Device
from time_tracking.models import WorkSchedule, TimeEvent


def run():
    print("🚀 Populating database...")

    # --- CLEAN (opcjonalne) ---
    TimeEvent.objects.all().delete()
    WorkSchedule.objects.all().delete()
    Employee.objects.all().delete()
    Device.objects.all().delete()

    # --- EMPLOYEES ---
    emp1 = Employee.objects.create(first_name="Jan", last_name="Kowalski")
    emp2 = Employee.objects.create(first_name="Anna", last_name="Nowak")

    print(f"👤 Employees: {emp1}, {emp2}")

    # --- DEVICES ---
    tablet1 = Device.objects.create(name="Tablet Front Desk", device_id="tablet-01")
    tablet2 = Device.objects.create(name="Tablet Warehouse", device_id="tablet-02")

    print(f"📱 Devices: {tablet1}, {tablet2}")

    today = date.today()

    # --- SCHEDULES ---
    WorkSchedule.objects.create(
        employee=emp1,
        date=today - timedelta(days=2),
        day_type=WorkSchedule.WORK,
        planned_start=time(8, 0),
        planned_end=time(16, 0),
    )

    WorkSchedule.objects.create(
        employee=emp1,
        date=today - timedelta(days=1),
        day_type=WorkSchedule.OFF,
    )

    WorkSchedule.objects.create(
        employee=emp2,
        date=today - timedelta(days=2),
        day_type=WorkSchedule.WORK,
        planned_start=time(9, 0),
        planned_end=time(17, 0),
    )

    WorkSchedule.objects.create(
        employee=emp2,
        date=today - timedelta(days=1),
        day_type=WorkSchedule.LEAVE,
    )

    print("📅 Schedules created")

    # --- EVENTS (EMPLOYEE 1) ---
    d = today - timedelta(days=2)

    TimeEvent.objects.create(
        employee=emp1,
        device=tablet1,
        event_type=TimeEvent.CHECK_IN,
        timestamp=timezone.make_aware(datetime.combine(d, time(8, 0))),
    )

    TimeEvent.objects.create(
        employee=emp1,
        device=tablet1,
        event_type=TimeEvent.BREAK_START,
        timestamp=timezone.make_aware(datetime.combine(d, time(12, 0))),
    )

    TimeEvent.objects.create(
        employee=emp1,
        device=tablet1,
        event_type=TimeEvent.BREAK_END,
        timestamp=timezone.make_aware(datetime.combine(d, time(12, 30))),
    )

    TimeEvent.objects.create(
        employee=emp1,
        device=tablet1,
        event_type=TimeEvent.CHECK_OUT,
        timestamp=timezone.make_aware(datetime.combine(d, time(16, 0))),
    )

    # --- EVENTS (EMPLOYEE 2 – anomaly: missing CHECK_OUT) ---
    TimeEvent.objects.create(
        employee=emp2,
        device=tablet2,
        event_type=TimeEvent.CHECK_IN,
        timestamp=timezone.make_aware(datetime.combine(d, time(9, 15))),
        is_anomaly=True,
        anomaly_reason="Missing CHECK_OUT",
    )

    print("⏱️ Time events created")
    print("✅ Database populated successfully!")


if __name__ == "__main__":
    run()
