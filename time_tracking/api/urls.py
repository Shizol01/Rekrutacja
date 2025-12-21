from django.urls import path, include
from rest_framework.routers import DefaultRouter
from time_tracking.api.views import (
    TabletEventView,
    AttendanceReportView,
    AttendanceReportCSVView,
    TabletStatusView,
    WorkScheduleViewSet,
)

router = DefaultRouter()
router.register("admin/schedules", WorkScheduleViewSet, basename="work-schedule")

urlpatterns = [
    # TABLET – API
    path("tablet/events/", TabletEventView.as_view(), name="tablet-events"),
    path("tablet/status/", TabletStatusView.as_view(), name="tablet-status"),

    # ADMIN – API
    path("", include(router.urls)),
    path("admin/reports/attendance/", AttendanceReportView.as_view(), name="attendance-report"),
    path("admin/reports/attendance.csv/", AttendanceReportCSVView.as_view(), name="attendance-report-csv"),
]
