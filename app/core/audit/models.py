from datetime import datetime, timezone
from typing import Any, Literal

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


class AuditLog(Document):
    """
    Immutable audit trail record stored in MongoDB.

    Captures who did what, when, from where.  The TTL index on created_at
    automatically expires records after 90 days.  request_id, client_ip,
    and user_agent are filled automatically from structlog contextvars by
    app.core.audit.service.log_event — callers only supply business fields.
    """

    event_type: str
    user_id: PydanticObjectId | None = None
    store_id: PydanticObjectId | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None
    status: Literal["success", "failure"] = "success"
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "audit_logs"
        indexes = [
            # TTL: expire records after 90 days
            IndexModel([("created_at", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("event_type", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("resource_type", ASCENDING), ("resource_id", ASCENDING)]),
        ]
