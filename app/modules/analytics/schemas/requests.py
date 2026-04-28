from datetime import date

from beanie import PydanticObjectId
from fastapi import Query
from pydantic import BaseModel, Field, model_validator

from app.core.enums import AnalyticsEventType


class AnalyticsEventCreate(BaseModel):
    event_type: AnalyticsEventType
    store_url: str
    item_id: PydanticObjectId | None = None    # required when event_type == item_view
    utm_source: str | None = None   # optional, sent by frontend from URL params

    @model_validator(mode="after")
    def validate_item_slug(self) -> "AnalyticsEventCreate":
        if self.event_type == AnalyticsEventType.item_view and not self.item_id:
            raise ValueError("item_id is required for item_view events")
        return self


class AnalyticsPeriodQuery(BaseModel):
    days: int | None = Field(None, description="Number of days to query, defaults to 30")
    from_date: date | None = Field(None, description="Start date (inclusive), e.g. 2026-01-01")
    to_date: date | None = Field(None, description="End date (inclusive), e.g. 2026-04-07")

    @model_validator(mode="after")
    def validate_dates(self) -> "AnalyticsPeriodQuery":
        if (self.from_date is None) != (self.to_date is None):
            raise ValueError("Both from_date and to_date must be provided together")
        if self.from_date is None and self.to_date is None and self.days is None:
            self.days = 30
        if self.days is not None and (self.days < 1 or self.days > 365):
            raise ValueError("days must be between 1 and 365")
        return self
