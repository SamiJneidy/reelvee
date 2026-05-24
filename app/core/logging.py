import logging
import sys

import structlog
from structlog.types import Processor


def _dev_cleanup(logger: object, method: str, event_dict: dict) -> dict:
    """
    Dev-only display processor — trims verbose context fields so the
    console stays readable.  Runs only on the rendered output; the full
    values remain in structlog contextvars for the audit service.
    """
    if "request_id" in event_dict:
        event_dict["request_id"] = event_dict["request_id"][:8]
    event_dict.pop("user_agent", None)
    return event_dict


def configure_logging(is_dev: bool = False) -> None:
    """
    Configure structlog with stdlib integration.

    Uses an allowlist for log levels — third-party libraries stay at INFO
    on the root logger, so their DEBUG output (pymongo heartbeats, botocore
    requests, etc.) is never emitted.  Only the application namespace
    (``app.*``) gets DEBUG in development.

    - Dev:  DEBUG for app code + pretty ConsoleRenderer
    - Prod: INFO everywhere + JSONRenderer
    """
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if is_dev:
        renderer: Processor = structlog.dev.ConsoleRenderer(
            colors=True, pad_level=False, pad_event=0
        )
        render_chain: list[Processor] = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            _dev_cleanup,
            renderer,
        ]
    else:
        renderer = structlog.processors.JSONRenderer()
        render_chain = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ]

    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=render_chain,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Allowlist: only application code gets DEBUG in dev.
    # All third-party loggers inherit INFO from root and stay quiet.
    logging.getLogger("app").setLevel(logging.DEBUG if is_dev else logging.INFO)

    # uvicorn.access duplicates our LoggingMiddleware — suppress it.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
