import json
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseNotFound


SPA_ENTRY = Path(settings.BASE_DIR) / "frontend" / "my-vue-app" / "dist" / "index.html"


def _inject_config(html: str) -> str:
    config_payload = json.dumps({
        "deviceId": settings.TABLET_DEVICE_ID,
        "deviceToken": settings.TABLET_DEVICE_TOKEN,
    })
    script = (
        "<script>"
        "const __tabletConfig = Object.freeze("
        f"{config_payload}"
        ");"
        "window.APP_CONFIG = Object.freeze(Object.assign({}, window.APP_CONFIG || {}, __tabletConfig));"
        "</script>"
    )
    if "</head>" in html:
        return html.replace("</head>", f"{script}\n</head>", 1)
    return f"{script}\n{html}"


def tablet_spa(_request, *_args, **_kwargs):
    if not SPA_ENTRY.exists():
        return HttpResponseNotFound("Tablet SPA bundle not found. Build frontend assets.")
    html = SPA_ENTRY.read_text(encoding="utf-8")
    return HttpResponse(_inject_config(html))


def tablet_debug(_request, *_args, **_kwargs):
    if not settings.DEBUG:
        raise Http404()
    payload = {
        "device_id": settings.TABLET_DEVICE_ID,
        "device_token_set": bool(settings.TABLET_DEVICE_TOKEN),
        "device_token_preview": (settings.TABLET_DEVICE_TOKEN[:4] + "…") if settings.TABLET_DEVICE_TOKEN else "",
    }
    return HttpResponse(json.dumps(payload, indent=2), content_type="application/json")
