from django.urls import path

from time_tracking.api.tablet_views import TabletStatusView
from time_tracking.api.views import (
    TabletEventView,
    AttendanceReportView,
    AttendanceReportCSVView,
    WorkScheduleListView
)
from time_tracking.views_admin import live_panel_view, employee_report_view, custom_report_view
from time_tracking.views_tablet_ui import (
    tablet_home,
    tablet_scan,
    tablet_message,
    tablet_status,
)

urlpatterns = [
    path("tablet/events/", TabletEventView.as_view(), name="tablet-events"),
    path("admin/reports/attendance/", AttendanceReportView.as_view(), name="attendance-report"),
    path("admin/reports/attendance.csv/", AttendanceReportCSVView.as_view(), name="attendance-report-csv"),
    path("admin/schedules/", WorkScheduleListView.as_view(), name="work-schedules"),
    path("tablet/status/", TabletStatusView.as_view(), name="tablet-status"),
    path("tablet/", tablet_home),
    path("tablet/scan/", tablet_scan),
    path("tablet/message/", tablet_message),
    path("tablet/status-ui/", tablet_status),
    path("admin-panel/live/", live_panel_view, name="admin-live-panel"),
    path(
        "admin-panel/reports/",
        employee_report_view,
        name="employee-report",
    ),
path(
    "admin-panel/reports/custom/",
    custom_report_view,
    name="custom-report",
),

]
