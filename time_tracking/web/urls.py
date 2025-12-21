from django.urls import path
from time_tracking.web.tablet_views import tablet_spa
from time_tracking.web.admin_views import (
    live_panel_view,
    employee_report_view,
    custom_report_view,
)

urlpatterns = [
    # TABLET – SPA entry
    path("tablet/", tablet_spa, name="tablet-home"),
    path("tablet/scan/", tablet_spa, name="tablet-scan"),
    path("tablet/status-ui/", tablet_spa, name="tablet-status-ui"),
    path("tablet/<path:_subpath>/", tablet_spa, name="tablet-spa-fallback"),

    # ADMIN PANEL – HTML
    path("admin-panel/live/", live_panel_view, name="admin-live-panel"),
    path("admin-panel/reports/", employee_report_view, name="employee-report"),
    path("admin-panel/reports/custom/", custom_report_view, name="custom-report"),
]
