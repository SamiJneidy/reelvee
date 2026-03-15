from datetime import datetime, timezone
from pydantic import Field
from beanie import Document
from pymongo import IndexModel, ASCENDING


class RefreshTokenRecord(Document):
    token_id: str
    family_id: str
    user_id: str
    is_revoked: bool = False
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "refresh_tokens"
        indexes = [
            IndexModel([("token_id", ASCENDING)], unique=True),
            IndexModel([("family_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),
        ]
