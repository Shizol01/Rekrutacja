from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound


SPA_ENTRY = Path(settings.BASE_DIR) / "frontend" / "dist" / "index.html"


def tablet_spa(_request, *_args, **_kwargs):
    if not SPA_ENTRY.exists():
        return HttpResponseNotFound("Tablet SPA bundle not found. Build frontend assets.")
    return FileResponse(SPA_ENTRY.open("rb"))
