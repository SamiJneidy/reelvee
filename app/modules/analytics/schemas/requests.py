from datetime import date

from fastapi import Query
from pydantic import BaseModel, model_validator

from app.core.enums import AnalyticsEventType


class AnalyticsEventCreate(BaseModel):
    event_type: AnalyticsEventType
    store_url: str
    item_id: str | None = None    # required when event_type == item_view
    utm_source: str | None = None   # optional, sent by frontend from URL params

    @model_validator(mode="after")
    def validate_item_slug(self) -> "AnalyticsEventCreate":
        if self.event_type == AnalyticsEventType.item_view and not self.item_id:
            raise ValueError("item_id is required for item_view events")
        return self


class AnalyticsPeriodQuery(BaseModel):
    days: int | None = Query(None, ge=1, le=365, description="Last N days (default 30)"),
    from_date: date | None = Query(None, description="Start date (inclusive), e.g. 2026-01-01"),
    to_date: date | None = Query(None, description="End date (inclusive), e.g. 2026-04-07"),

    @model_validator(mode="after")
    def validate_dates(self) -> "AnalyticsPeriodQuery":
        if (self.from_date is None) != (self.to_date is None):
            raise ValueError("Both from_date and to_date must be provided together")
        return self
