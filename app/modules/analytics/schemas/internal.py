from datetime import date
from typing import TypedDict

from pydantic import BaseModel


class BreakdownRow(BaseModel):
    """Aggregate breakdown row from analytics repository queries (e.g. country/OS)."""

    key: str
    count: int
    percentage: float


class TopItemRow(BaseModel):
    """Top items by views from repository aggregation + item lookup."""

    item_id: str
    name: str
    views: int


class StoreDailyViewTrendBucket(TypedDict):
    store_views: int
    item_views: int


StoreDailyViewTrendByDate = dict[date, StoreDailyViewTrendBucket]


class OrderDailyTrendBucket(TypedDict):
    orders: int
    revenue: float


OrderDailyTrendByDate = dict[date, OrderDailyTrendBucket]
