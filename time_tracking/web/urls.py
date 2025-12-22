from django.conf import settings
from django.urls import path

from time_tracking.web.admin_views import admin_panel_spa
from time_tracking.web.tablet_views import spa_entrypoint, tablet_debug

urlpatterns = [
    # TABLET – SPA entry
    path("tablet/", spa_entrypoint, name="tablet-home"),

    # ADMIN PANEL – SPA entry
    path("admin-panel/", admin_panel_spa, name="admin-panel-home"),
]

if settings.DEBUG:
    urlpatterns.append(
        path("tablet/debug/", tablet_debug, name="tablet-debug"),
    )

urlpatterns += [
    path("tablet/<path:_subpath>/", spa_entrypoint, name="tablet-spa-fallback"),
    path("admin-panel/<path:_subpath>/", admin_panel_spa, name="admin-panel-spa-fallback"),
]
