from datetime import date, datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, computed_field

from app.shared.schemas.common import PeriodInfo


class BreakdownItem(BaseModel):
    key: str
    count: int
    percentage: float


class DailyTrendPoint(BaseModel):
    date: date
    store_views: int = 0
    item_views: int = 0
    orders: int = 0
    revenue: float = 0.0


class TopItem(BaseModel):
    item_id: str
    name: str
    views: int


class StoreAnalyticsOverview(BaseModel):
    period: PeriodInfo
    store_views: int
    item_views: int
    total_orders: int
    revenue: float
    total_cost: float
    units_sold: int

    @computed_field
    @property
    def profit(self) -> float:
        return round(self.revenue - self.total_cost, 2)


class StoreAnalyticsResponse(BaseModel):
    overview: StoreAnalyticsOverview
    countries: list[BreakdownItem]
    os_breakdown: list[BreakdownItem]
    daily_trend: list[DailyTrendPoint]
    top_items: list[TopItem]


class ItemDailyTrendPoint(BaseModel):
    date: date
    views: int = 0
    orders: int = 0


class ItemAnalyticsResponse(BaseModel):
    item_id: str
    period: PeriodInfo
    views: int
    orders: int
    revenue: float
    total_cost: float
    units_sold: int
    conversion_rate: float          # orders / views * 100, 0 if no views
    daily_trend: list[ItemDailyTrendPoint]
