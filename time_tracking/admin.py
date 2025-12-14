from django.contrib import admin
from time_tracking.models import WorkSchedule, TimeEvent


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "day_type",
        "planned_start",
        "planned_end",
    )
    list_filter = ("day_type", "date")
    search_fields = (
        "employee__first_name",
        "employee__last_name",
    )
    ordering = ("date",)


@admin.register(TimeEvent)
class TimeEventAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "event_type",
        "timestamp",
        "device",
        "is_anomaly",
    )
    list_filter = (
        "event_type",
        "is_anomaly",
        "timestamp",
    )
    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "device__name",
        "device__device_id",
    )
    ordering = ("-timestamp",)
