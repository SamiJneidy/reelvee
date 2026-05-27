import time

import structlog

logger = structlog.get_logger(__name__)


def log_dependency_timing(name: str, started_at: float, **fields) -> None:
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "di.dependency_resolved",
        dependency=name,
        duration_ms=duration_ms,
        **fields,
    )
