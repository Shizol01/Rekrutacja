from time_tracking.web.tablet_views import spa_entrypoint


def admin_panel_spa(request, *_args, **_kwargs):
    return spa_entrypoint(request, *_args, **_kwargs)
