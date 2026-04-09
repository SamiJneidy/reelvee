from datetime import date
from typing import TypedDict


class StoreDailyViewTrendBucket(TypedDict):
    store_views: int
    item_views: int


StoreDailyViewTrendByDate = dict[date, StoreDailyViewTrendBucket]


class OrderDailyTrendBucket(TypedDict):
    orders: int
    revenue: float


OrderDailyTrendByDate = dict[date, OrderDailyTrendBucket]
