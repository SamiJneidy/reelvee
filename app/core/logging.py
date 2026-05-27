import logging
import sys

import structlog
from structlog.types import Processor


def _compact_http_context(logger: object, method: str, event_dict: dict) -> dict:
    """
    Display-only processor that trims noisy HTTP context fields so console
    output is easier to read. This does NOT mutate contextvars, only the
    rendered output line.
    """
    if "request_id" in event_dict:
        event_dict["request_id"] = event_dict["request_id"][:8]
    event_dict.pop("user_agent", None)
    return event_dict


def configure_logging(
    *,
    is_dev: bool = False,
    renderer_mode: str = "json",
    compact_http_context: bool = True,
) -> None:
    """
    Configure structlog with stdlib integration.

    Uses an allowlist for log levels — third-party libraries stay at INFO
    on the root logger, so their DEBUG output (pymongo heartbeats, botocore
    requests, etc.) is never emitted.  Only ``app.*`` gets DEBUG in dev.

    Renderer modes:
    - ``json``    : machine-friendly JSON lines (default)
    - ``console`` : human-friendly colored console output
    """
    use_console_renderer = renderer_mode == "console"
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if use_console_renderer:
        renderer: Processor = structlog.dev.ConsoleRenderer(
            colors=True, pad_level=False, pad_event=0
        )
        render_chain: list[Processor] = [structlog.stdlib.ProcessorFormatter.remove_processors_meta]
        if compact_http_context:
            render_chain.append(_compact_http_context)
        render_chain.append(renderer)
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
