import uvicorn
import structlog
import aioboto3
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware.logging import LoggingMiddleware
from app.core.exceptions.handlers import register_exception_handlers
from app.api.v1.routers import router as v1_router
from app.core.database import init_db
from app.shared.email.dependencies import init_ses_client
from app.shared.storage.dependencies import init_s3_client

configure_logging(
    is_dev=settings.environment.upper() in ("DEVELOPMENT", "DEV", "LOCAL"),
    renderer_mode=settings.log_renderer,
    compact_http_context=settings.log_compact_http_context,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "app.startup",
        environment=settings.environment,
        log_renderer=settings.log_renderer,
        mongo_query_logging_enabled=settings.mongo_query_logging_enabled,
        mongo_slow_query_ms=settings.mongo_slow_query_ms,
        mongo_log_all_queries=settings.mongo_log_all_queries,
    )
    await init_db()

    # One aioboto3 S3 client per process — entered here, closed on shutdown.
    boto3_session = aioboto3.Session()
    async with (
        boto3_session.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        ) as s3_client,
            boto3_session.client(
            "ses",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        ) as ses_client
    ):
        init_ses_client(ses_client)
        init_s3_client(s3_client)

        logger.info("app.ready")
        yield

    logger.info("app.shutdown")


app = FastAPI(
    title="reelvee - Backend API",
    description="""This is the backend API for reelvee platform. Here you can find the API endpoints and their documentation for reelvee.""",
    version="1.0.0",
    contact={
        "name": "reelvee Support",
        "email": "support@reelvee.com",
        "url": "https://reelvee.com",
    },
    lifespan=lifespan,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
        },
    },
)

app.include_router(v1_router)

register_exception_handlers(app)

# LoggingMiddleware must be added AFTER CORSMiddleware in the add_middleware
# call order — Starlette applies middleware in reverse registration order, so
# LoggingMiddleware ends up outermost (first to receive, last to respond).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
