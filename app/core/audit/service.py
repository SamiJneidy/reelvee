from typing import Any, Literal

import structlog
from beanie import PydanticObjectId

from app.core.audit.enums import AuditEventType, AuditResourceType
from app.core.audit.models import AuditLog

logger = structlog.get_logger(__name__)


async def log_event(
    event_type: AuditEventType,
    *,
    user_id: PydanticObjectId | None = None,
    store_id: PydanticObjectId | None = None,
    resource_type: AuditResourceType | None = None,
    resource_id: str | None = None,
    status: Literal["success", "failure"] = "success",
    details: dict[str, Any] | None = None,
) -> None:
    """
    Persist a structured audit event to MongoDB.

    Request-scoped fields (request_id, client_ip, user_agent) are read
    automatically from the structlog contextvars bound by LoggingMiddleware,
    so callers only need to supply business-level fields.

    This function never raises — a failure to write the audit record is
    logged at WARNING level and silently swallowed to avoid disrupting the
    caller's main flow.
    """
    ctx = structlog.contextvars.get_contextvars()

    try:
        await AuditLog(
            event_type=event_type,
            user_id=user_id,
            store_id=store_id,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details or {},
            ip_address=ctx.get("client_ip"),
            user_agent=ctx.get("user_agent"),
            request_id=ctx.get("request_id"),
        ).insert()
    except Exception:
        logger.warning(
            "audit.write_failed",
            event_type=event_type,
            exc_info=True,
        )
