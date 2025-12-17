import os
from datetime import date, time, datetime, timedelta

import django
from django.utils import timezone

from core.models import Employee, Device
from time_tracking.models import WorkSchedule, TimeEvent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rekrutacja.settings")
django.setup()


def aware(d, t):
    return timezone.make_aware(datetime.combine(d, t))


def run():
    print("🚀 Populating database with realistic demo data...")

    # --- CLEAN ---
    TimeEvent.objects.all().delete()
    WorkSchedule.objects.all().delete()
    Employee.objects.all().delete()
    Device.objects.all().delete()

    # --- EMPLOYEES ---
    jan = Employee.objects.create(first_name="Jan", last_name="Kowalski")
    anna = Employee.objects.create(first_name="Anna", last_name="Nowak")

    # --- DEVICES ---
    tablet = Device.objects.create(name="Tablet Front Desk", device_id="tablet-01")

    today = date.today()

    # ======================================================
    # 📅 SCHEDULES (last 7 days)
    # ======================================================

    for i in range(7):
        d = today - timedelta(days=i)

        # Jan – pracuje 5 dni, 1 OFF, 1 LEAVE
        if i == 5:
            WorkSchedule.objects.create(employee=jan, date=d, day_type=WorkSchedule.OFF)
        elif i == 6:
            WorkSchedule.objects.create(employee=jan, date=d, day_type=WorkSchedule.LEAVE)
        else:
            WorkSchedule.objects.create(
                employee=jan,
                date=d,
                day_type=WorkSchedule.WORK,
                planned_start=time(8, 0),
                planned_end=time(16, 0),
            )

        # Anna – tylko 3 dni grafiku
        if i in (1, 3, 4):
            WorkSchedule.objects.create(
                employee=anna,
                date=d,
                day_type=WorkSchedule.WORK,
                planned_start=time(9, 0),
                planned_end=time(17, 0),
            )

    # ======================================================
    # ⏱️ EVENTS – JAN
    # ======================================================

    # 2 dni temu – normalny dzień + przerwa
    d = today - timedelta(days=2)
    TimeEvent.objects.create(employee=jan, device=tablet, event_type=TimeEvent.CHECK_IN,
                             timestamp=aware(d, time(8, 0)))
    TimeEvent.objects.create(employee=jan, device=tablet, event_type=TimeEvent.BREAK_START,
                             timestamp=aware(d, time(12, 0)))
    TimeEvent.objects.create(employee=jan, device=tablet, event_type=TimeEvent.BREAK_END,
                             timestamp=aware(d, time(12, 30)))
    TimeEvent.objects.create(employee=jan, device=tablet, event_type=TimeEvent.CHECK_OUT,
                             timestamp=aware(d, time(16, 0)))

    # 3 dni temu – spóźnienie
    d = today - timedelta(days=3)
    TimeEvent.objects.create(employee=jan, device=tablet, event_type=TimeEvent.CHECK_IN,
                             timestamp=aware(d, time(8, 20)))
    TimeEvent.objects.create(employee=jan, device=tablet, event_type=TimeEvent.CHECK_OUT,
                             timestamp=aware(d, time(16, 0)))

    # 4 dni temu – brak CHECK_OUT (anomalia)
    d = today - timedelta(days=4)
    TimeEvent.objects.create(
        employee=jan,
        device=tablet,
        event_type=TimeEvent.CHECK_IN,
        timestamp=aware(d, time(8, 0)),
        is_anomaly=True,
        anomaly_reason="Missing CHECK_OUT",
    )

    # ======================================================
    # ⏱️ EVENTS – ANNA
    # ======================================================

    # 1 dzień temu – praca bez grafiku (NO_SCHEDULE)
    d = today - timedelta(days=1)
    TimeEvent.objects.create(employee=anna, device=tablet, event_type=TimeEvent.CHECK_IN,
                             timestamp=aware(d, time(10, 0)))
    TimeEvent.objects.create(employee=anna, device=tablet, event_type=TimeEvent.CHECK_OUT,
                             timestamp=aware(d, time(13, 30)))

    # 3 dni temu – brak CHECK_IN, tylko CHECK_OUT (anomalia)
    d = today - timedelta(days=3)
    TimeEvent.objects.create(
        employee=anna,
        device=tablet,
        event_type=TimeEvent.CHECK_OUT,
        timestamp=aware(d, time(17, 0)),
        is_anomaly=True,
        anomaly_reason="CHECK_OUT without CHECK_IN",
    )

    print("✅ Database populated with realistic demo data!")


if __name__ == "__main__":
    run()
