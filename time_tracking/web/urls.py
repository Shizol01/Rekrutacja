from django.urls import path
from time_tracking.web.tablet_views import (
    tablet_home,
    tablet_scan,
    tablet_message,
    tablet_status,
)
from time_tracking.web.admin_views import (
    live_panel_view,
    employee_report_view,
    custom_report_view,
)

urlpatterns = [
    # TABLET – HTML
    path("tablet/", tablet_home, name="tablet-home"),
    path("tablet/scan/", tablet_scan, name="tablet-scan"),
    path("tablet/message/", tablet_message, name="tablet-message"),
    path("tablet/status-ui/", tablet_status, name="tablet-status-ui"),

    # ADMIN PANEL – HTML
    path("admin-panel/live/", live_panel_view, name="admin-live-panel"),
    path("admin-panel/reports/", employee_report_view, name="employee-report"),
    path("admin-panel/reports/custom/", custom_report_view, name="custom-report"),
]
