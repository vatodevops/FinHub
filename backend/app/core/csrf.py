from __future__ import annotations

from urllib.parse import urlparse

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import settings


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

# Paths que reciben redirect desde un tercero (Google) y por tanto pueden llegar sin
# Origin/Referer de nuestro frontend. No mutan datos sensibles por sí mismos.
EXEMPT_PATH_PREFIXES = (
    "/api/auth/google/callback",
)


def _allowed_origins() -> set[str]:
    allowed = set(settings.cors_origins or [])
    if settings.frontend_base_url:
        allowed.add(settings.frontend_base_url.rstrip("/"))
    return {o.rstrip("/") for o in allowed if o}


def _origin_of(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


class OriginCheckMiddleware(BaseHTTPMiddleware):
    """Defensa en profundidad frente a CSRF: exige que POST/PATCH/PUT/DELETE
    provengan de un Origin (o Referer como fallback) que pertenezca al frontend.

    No sustituye a SameSite=Lax sobre la cookie de sesión, lo complementa.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in SAFE_METHODS:
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(prefix) for prefix in EXEMPT_PATH_PREFIXES):
            return await call_next(request)

        allowed = _allowed_origins()
        if not allowed:
            return await call_next(request)

        origin = _origin_of(request.headers.get("origin")) or _origin_of(request.headers.get("referer"))

        if origin is None or origin not in allowed:
            return JSONResponse(
                status_code=403,
                content={"error_code": "origin_forbidden", "detail": "Origin no permitido"},
            )

        return await call_next(request)
