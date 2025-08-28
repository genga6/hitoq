import re

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.logging_config import get_logger
from src.service.token_service import TokenService

logger = get_logger(__name__)

CSRF_HEADER_NAME = "X-CSRFToken"
CSRF_COOKIE_NAME = "csrf_token"


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_methods=None, exempt_paths=None):
        super().__init__(app)
        self.protected_methods = protected_methods or {"POST", "PUT", "DELETE", "PATCH"}
        self.exempt_paths = exempt_paths or {
            "/health",
            "/",
            "/auth/login/twitter",
            "/auth/callback/twitter",
            "/auth/refresh-token",
            "/auth/csrf-token",
        }
        # Compile regex patterns for dynamic path matching
        self.exempt_patterns = [
            re.compile(r"^/users/[^/]+/visit$"),  # /users/{user_id}/visit
        ]

    def _is_exempt_path(self, path: str) -> bool:
        if path in self.exempt_paths:
            return True

        for pattern in self.exempt_patterns:
            if pattern.match(path):
                return True

        return False

    async def dispatch(self, request: Request, call_next):
        # Static files and exempt paths
        if (
            request.url.path.startswith("/static/")
            or self._is_exempt_path(request.url.path)
            or request.method == "GET"
            or request.method == "HEAD"
            or request.method == "OPTIONS"
        ):
            response = await call_next(request)
            return response

        # CSRF token validation for protected methods
        if request.method in self.protected_methods:
            csrf_token = request.headers.get(CSRF_HEADER_NAME)
            cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

            if not csrf_token or not cookie_token:
                logger.warning(
                    f"CSRF token missing for {request.method} {request.url.path}",
                    client_ip=request.client.host if request.client else "unknown",
                )
                raise HTTPException(status_code=403, detail="CSRF token missing")

            if csrf_token != cookie_token:
                logger.warning(
                    f"CSRF token mismatch for {request.method} {request.url.path}",
                    client_ip=request.client.host if request.client else "unknown",
                )
                raise HTTPException(status_code=403, detail="CSRF token mismatch")

            if not TokenService.verify_csrf_token(csrf_token):
                logger.warning(
                    f"Invalid CSRF token for {request.method} {request.url.path}",
                    client_ip=request.client.host if request.client else "unknown",
                )
                raise HTTPException(status_code=403, detail="Invalid CSRF token")

        response = await call_next(request)
        return response
