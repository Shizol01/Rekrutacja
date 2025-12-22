import json
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse


SPA_ENTRY = Path(settings.BASE_DIR) / "frontend" / "my-vue-app" / "dist" / "index.html"


def spa_entrypoint(_request, *_args, **_kwargs):
    if not SPA_ENTRY.exists():
        raise Http404("SPA bundle not found. Build frontend assets.")

    return FileResponse(SPA_ENTRY.open("rb"), content_type="text/html")


def tablet_debug(_request, *_args, **_kwargs):
    if not settings.DEBUG:
        raise Http404()
    payload = {
        "device_id": settings.TABLET_DEVICE_ID,
        "device_token_set": bool(settings.TABLET_DEVICE_TOKEN),
        "device_token_preview": (settings.TABLET_DEVICE_TOKEN[:4] + "…") if settings.TABLET_DEVICE_TOKEN else "",
    }
    return HttpResponse(json.dumps(payload, indent=2), content_type="application/json")
