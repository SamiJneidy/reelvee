import asyncio
from datetime import date, datetime, timedelta, timezone

from beanie import PydanticObjectId

from app.core.enums import AnalyticsEventType
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schemas import AnalyticsEventCreate
from app.modules.analytics.schemas.internal import (
    OrderDailyTrendBucket,
    OrderDailyTrendByDate,
    StoreDailyViewTrendBucket,
    StoreDailyViewTrendByDate,
)
from app.modules.analytics.schemas.responses import (
    DailyTrendPoint,
    ItemAnalyticsResponse,
    ItemDailyTrendPoint,
    StoreAnalyticsOverview,
    StoreAnalyticsResponse,
)
from app.shared.client_metadata import ClientRequestMetadata
from app.shared.schemas.common import PeriodInfo
from app.shared.utils.time_helper import resolve_period, today_utc

class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository) -> None:
        self._repo = repo

    # ------------------------------------------------------------------
    # Event recording
    # ------------------------------------------------------------------

    async def record_event(
        self,
        store_id: PydanticObjectId,
        payload: AnalyticsEventCreate,
        client: ClientRequestMetadata,
    ) -> None:
        if client.is_bot:
            return

        today = today_utc()

        if payload.event_type == AnalyticsEventType.store_view:
            await self._repo.record_store_view(
                store_id=store_id,
                date=today,
                country_code=client.country_code,
                os_type=client.os_type,
            )

        elif payload.event_type == AnalyticsEventType.item_view:
            await self._repo.record_item_view(
                store_id=store_id,
                item_id=payload.item_id,
                date=today,
            )

    # ------------------------------------------------------------------
    # Store analytics
    # ------------------------------------------------------------------

    async def get_store_analytics(
        self,
        user_id: PydanticObjectId,
        store_id: PydanticObjectId,
        days: int | None,
        from_date: date | None,
        to_date: date | None,
    ) -> StoreAnalyticsResponse:

        start, end = resolve_period(days, from_date, to_date)

        store_views, item_views = await self._repo.get_store_overview(store_id, start, end)
        total_orders, revenue, total_cost, units_sold = await self._repo.get_order_stats(user_id, start, end)
        countries = await self._repo.get_country_breakdown(store_id, start, end)
        os_breakdown = await self._repo.get_os_breakdown(store_id, start, end)
        view_trend = await self._repo.get_store_daily_trend(store_id, start, end)
        order_trend = await self._repo.get_order_daily_trend(user_id, start, end)
        top_items = await self._repo.get_top_items(store_id, start, end)

        daily_trend = _merge_daily_trend(view_trend, order_trend, start, end)

        return StoreAnalyticsResponse(
            overview=StoreAnalyticsOverview(
                period=PeriodInfo(from_date=start.date(), to_date=end.date()),
                store_views=store_views,
                item_views=item_views,
                total_orders=total_orders,
                revenue=revenue,
                total_cost=total_cost,
                units_sold=units_sold,
            ),
            countries=countries,
            os_breakdown=os_breakdown,
            daily_trend=daily_trend,
            top_items=top_items,
        )

    # ------------------------------------------------------------------
    # Per-item analytics
    # ------------------------------------------------------------------

    async def get_item_analytics(
        self,
        user_id: PydanticObjectId,
        item_id: PydanticObjectId,
        store_id: PydanticObjectId,
        days: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> ItemAnalyticsResponse:
        start, end = resolve_period(days, from_date, to_date)

        views = await self._repo.get_item_views(item_id, store_id, start, end)
        total_orders, revenue, total_cost, units_sold = await self._repo.get_order_stats(user_id, start, end, item_id=item_id)
        daily_views = await self._repo.get_item_daily_views(item_id, store_id, start, end)
        order_trend = await self._repo.get_order_daily_trend(user_id, start, end, item_id=item_id)
        daily_trend = _merge_item_daily_trend(daily_views, order_trend, start, end)
        conversion_rate = round(total_orders / views * 100, 2) if views else 0.0

        return ItemAnalyticsResponse(
            item_id=str(item_id),
            period=PeriodInfo(from_date=start.date(), to_date=end.date()),
            views=views,
            orders=total_orders,
            revenue=revenue,
            total_cost=total_cost,
            units_sold=units_sold,
            conversion_rate=conversion_rate,
            daily_trend=daily_trend,
        )


def _merge_daily_trend(
    views_by_day: StoreDailyViewTrendByDate,
    orders_by_day: OrderDailyTrendByDate,
    start: datetime,
    end: datetime,
) -> list[DailyTrendPoint]:
    """Join store view buckets per day with order counts/revenue per day."""
    result: list[DailyTrendPoint] = []
    current = start.date()
    end_date = end.date()
    while current <= end_date:
        view_bucket = views_by_day.get(current) or {"store_views": 0, "item_views": 0}
        order_bucket = orders_by_day.get(current) or {"orders": 0, "revenue": 0.0}
        result.append(
            DailyTrendPoint(
                date=current,
                store_views=view_bucket["store_views"],
                item_views=view_bucket["item_views"],
                orders=order_bucket["orders"],
                revenue=order_bucket["revenue"],
            )
        )
        current += timedelta(days=1)
    return result


def _merge_item_daily_trend(
    views_by_day: dict[date, int],
    orders_by_day: OrderDailyTrendByDate,
    start: datetime,
    end: datetime,
) -> list[ItemDailyTrendPoint]:
    result: list[ItemDailyTrendPoint] = []
    current = start.date()
    end_date = end.date()
    while current <= end_date:
        day_views = views_by_day.get(current, 0)
        order_bucket = orders_by_day.get(current) or {"orders": 0, "revenue": 0.0}
        result.append(
            ItemDailyTrendPoint(
                date=current,
                views=day_views,
                orders=order_bucket["orders"],
            )
        )
        current += timedelta(days=1)
    return result
