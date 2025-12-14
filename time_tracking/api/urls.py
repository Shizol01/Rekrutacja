from django.urls import path
from time_tracking.api.views import (
    TabletEventView,
    AttendanceReportView,
    AttendanceReportCSVView,
    WorkScheduleListView
)

urlpatterns = [
    path("tablet/events/", TabletEventView.as_view(), name="tablet-events"),
    path("admin/reports/attendance/", AttendanceReportView.as_view(), name="attendance-report"),
    path("admin/reports/attendance.csv/", AttendanceReportCSVView.as_view(), name="attendance-report-csv"),
    path("admin/schedules/", WorkScheduleListView.as_view(), name="work-schedules"),

]
