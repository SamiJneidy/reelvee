import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from .exceptions import BaseAppException

logger = structlog.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        logger.warning(
            "http.exception",
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(BaseAppException)
    async def base_exception_handler(
        request: Request, exc: BaseAppException
    ) -> JSONResponse:
        log_fn = logger.error if exc.status_code >= 500 else logger.warning
        log_fn(
            "app.exception",
            exc_type=type(exc).__name__,
            status_code=exc.status_code,
            **{k: v for k, v in exc.__dict__.items() if k != "status_code"},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={k: v for k, v in exc.__dict__.items() if k != "status_code"},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.critical(
            "unhandled.exception",
            exc_type=type(exc).__name__,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."},
        )
