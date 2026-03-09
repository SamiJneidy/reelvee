from beanie import Document, before_event
from beanie.odm.actions import Insert, Replace
from datetime import datetime, timezone
from pydantic import Field


class BaseDocument(Document):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Insert)
    def set_created(self):
        now = datetime.now(timezone.utc)
        self.created_at = now
        self.updated_at = now

    @before_event(Replace)
    def set_updated(self):
        self.updated_at = datetime.now(timezone.utc)