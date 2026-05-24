import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)

_SKIP_PATHS = frozenset({"/docs", "/redoc", "/openapi.json", "/favicon.ico"})


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Per-request structured logging middleware.

    Responsibilities:
    - Assigns a unique request_id (honours X-Request-ID header if provided).
    - Binds request_id, method, path, client_ip, user_agent to structlog
      contextvars so every log call within the request carries them automatically.
    - Logs the incoming request at INFO.
    - Logs the outgoing response with status_code and duration_ms.
      Level is INFO for 2xx/3xx, WARNING for 4xx, ERROR for 5xx.
    - Echoes request_id back in the X-Request-ID response header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        structlog.contextvars.clear_contextvars()

        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        path = request.url.path

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        if path not in _SKIP_PATHS:
            logger.info("http.request")

        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                "http.error",
                duration_ms=duration_ms,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        status_code = response.status_code

        if path not in _SKIP_PATHS:
            log_fn = logger.info
            if status_code >= 500:
                log_fn = logger.error
            elif status_code >= 400:
                log_fn = logger.warning

            log_fn("http.response", status_code=status_code, duration_ms=duration_ms)

        response.headers["X-Request-ID"] = request_id
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
