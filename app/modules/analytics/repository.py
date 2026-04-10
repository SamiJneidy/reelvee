import asyncio
from datetime import datetime, date

from beanie import PydanticObjectId
from beanie.operators import Inc
from app.modules.orders.models import Order
from app.core.enums import OSType
from app.modules.analytics.models import (
    ItemDailyStat,
    StoreDailyCountry,
    StoreDailyOS,
    StoreDailyStat,
)
from app.modules.analytics.schemas.internal import (
    OrderDailyTrendBucket,
    OrderDailyTrendByDate,
    StoreDailyViewTrendBucket,
    StoreDailyViewTrendByDate,
)
from app.modules.analytics.schemas.responses import (
    BreakdownItem,
    TopItem,
)

class AnalyticsRepository:

    # ------------------------------------------------------------------
    # Write — event upserts
    # ------------------------------------------------------------------

    async def record_store_view(
        self,
        store_id: PydanticObjectId,
        date: datetime,
        country_code: str,
        os_type: OSType,
    ) -> None:
        await asyncio.gather(
            StoreDailyStat.find_one(
                StoreDailyStat.store_id == store_id,
                StoreDailyStat.date == date,
            ).upsert(
                Inc({StoreDailyStat.store_views: 1}),
                on_insert=StoreDailyStat(store_id=store_id, date=date, store_views=1),
            ),
            StoreDailyCountry.find_one(
                StoreDailyCountry.store_id == store_id,
                StoreDailyCountry.date == date,
                StoreDailyCountry.country_code == country_code,
            ).upsert(
                Inc({StoreDailyCountry.visits: 1}),
                on_insert=StoreDailyCountry(store_id=store_id, date=date, country_code=country_code, visits=1),
            ),
            StoreDailyOS.find_one(
                StoreDailyOS.store_id == store_id,
                StoreDailyOS.date == date,
                StoreDailyOS.os_type == os_type,
            ).upsert(
                Inc({StoreDailyOS.visits: 1}),
                on_insert=StoreDailyOS(store_id=store_id, date=date, os_type=os_type, visits=1),
            ),
        )

    async def record_item_view(
        self,
        store_id: PydanticObjectId,
        item_id: PydanticObjectId,
        date: datetime,
    ) -> None:
        await asyncio.gather(
            StoreDailyStat.find_one(
                StoreDailyStat.store_id == store_id,
                StoreDailyStat.date == date,
            ).upsert(
                Inc({StoreDailyStat.item_views: 1}),
                on_insert=StoreDailyStat(store_id=store_id, date=date, item_views=1),
            ),
            ItemDailyStat.find_one(
                ItemDailyStat.item_id == item_id,
                ItemDailyStat.store_id == store_id,
                ItemDailyStat.date == date,
            ).upsert(
                Inc({ItemDailyStat.views: 1}),
                on_insert=ItemDailyStat(item_id=item_id, store_id=store_id, date=date, views=1),
            ),
        )

    # ------------------------------------------------------------------
    # Read — store analytics
    # ------------------------------------------------------------------

    async def get_store_overview(
        self,
        store_id: PydanticObjectId,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> tuple[int, int]:
        """Returns (store_views, item_views)."""

        pipeline = [
            {"$match": {"store_id": store_id, "date": {"$gte": from_date, "$lte": to_date}}},
            {"$group": {
                "_id": None,
                "store_views": {"$sum": "$store_views"},
                "item_views": {"$sum": "$item_views"},
            }},
        ]
        cursor = StoreDailyStat.get_pymongo_collection().aggregate(pipeline)
        result = await cursor.to_list(length=1)
        row = result[0] if result else {}
        return row.get("store_views", 0), row.get("item_views", 0)

    async def get_country_breakdown(
        self,
        store_id: PydanticObjectId,
        start: datetime,
        end: datetime,
    ) -> list[BreakdownItem]:
        pipeline = [
            {"$match": {"store_id": store_id, "date": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": "$country_code", "total": {"$sum": "$visits"}}},
            {"$sort": {"total": -1}},
        ]
        cursor = StoreDailyCountry.get_pymongo_collection().aggregate(pipeline)
        rows = await cursor.to_list(length=None)
        grand_total = sum(r["total"] for r in rows)
        return [
            BreakdownItem(
                key=r["_id"],
                count=r["total"],
                percentage=round(r["total"] / grand_total * 100, 1) if grand_total else 0.0,
            )
            for r in rows
        ]

    async def get_os_breakdown(
        self,
        store_id: PydanticObjectId,
        start: datetime,
        end: datetime,
    ) -> list[BreakdownItem]:
        pipeline = [
            {"$match": {"store_id": store_id, "date": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": "$os_type", "total": {"$sum": "$visits"}}},
            {"$sort": {"total": -1}},
        ]
        cursor = StoreDailyOS.get_pymongo_collection().aggregate(pipeline)
        rows = await cursor.to_list(length=None)
        grand_total = sum(r["total"] for r in rows)
        return [
            BreakdownItem(
                key=r["_id"],
                count=r["total"],
                percentage=round(r["total"] / grand_total * 100, 1) if grand_total else 0.0,
            )
            for r in rows
        ]

    async def get_store_daily_trend(
        self,
        store_id: PydanticObjectId,
        start: datetime,
        end: datetime,
    ) -> StoreDailyViewTrendByDate:
        """Per calendar day: nested {store_views, item_views}. Keys are UTC dates for daily stat buckets."""
        pipeline = [
            {"$match": {"store_id": store_id, "date": {"$gte": start, "$lte": end}}},
            {"$group": {
                "_id": "$date",
                "store_views": {"$sum": "$store_views"},
                "item_views": {"$sum": "$item_views"},
            }},
            {"$sort": {"_id": 1}},
        ]
        cursor = StoreDailyStat.get_pymongo_collection().aggregate(pipeline)
        rows = await cursor.to_list(length=None)
        return {
            row["_id"].date(): StoreDailyViewTrendBucket(
                store_views=row["store_views"],
                item_views=row["item_views"],
            )
            for row in rows
        }

    async def get_top_items(
        self,
        store_id: PydanticObjectId,
        start: datetime,
        end: datetime,
        limit: int = 10,
    ) -> list[TopItem]:
        pipeline = [
            {"$match": {"store_id": store_id, "date": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": "$item_id", "views": {"$sum": "$views"}}},
            {"$sort": {"views": -1}},
            {"$limit": limit},
            {"$lookup": {
                "from": "items",
                "localField": "_id",
                "foreignField": "_id",
                "as": "item",
            }},
            {"$unwind": {"path": "$item", "preserveNullAndEmptyArrays": True}},
        ]
        cursor = ItemDailyStat.get_pymongo_collection().aggregate(pipeline)
        rows = await cursor.to_list(length=None)
        return [
            TopItem(
                item_id=str(row["_id"]),
                name=row.get("item", {}).get("name", "Unknown"),
                views=row["views"],
            )
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Read — order stats (shared by store overview + per-item analytics)
    # ------------------------------------------------------------------

    async def get_order_stats(
        self,
        user_id: PydanticObjectId,
        start: datetime,
        end: datetime,
        item_id: PydanticObjectId | None = None,
    ) -> tuple[int, float, float, int]:
        """Returns (total_orders, revenue, total_cost, units_sold)."""
        match: dict = {
            "user_id": user_id,
            "created_at": {"$gte": start, "$lte": end},
        }
        if item_id:
            match["item_id"] = item_id

        pipeline = [
            {"$match": match},
            {"$group": {
                "_id": None,
                "total_orders": {"$sum": 1},
                "revenue": {"$sum": {"$ifNull": ["$total", 0]}},
                "total_cost": {"$sum": {"$ifNull": ["$total_cost", 0]}},
                "units_sold": {"$sum": {"$ifNull": ["$quantity", 0]}},
            }},
        ]
        
        cursor = Order.get_pymongo_collection().aggregate(pipeline)
        result = await cursor.to_list(length=1)
        row = result[0] if result else {}
        return (
            row.get("total_orders", 0),
            round(row.get("revenue", 0.0), 2),
            round(row.get("total_cost", 0.0), 2),
            row.get("units_sold", 0),
        )

    async def get_order_daily_trend(
        self,
        user_id: PydanticObjectId,
        start: datetime,
        end: datetime,
        item_id: PydanticObjectId | None = None,
    ) -> OrderDailyTrendByDate:
        """Per calendar day: nested {orders, revenue}."""
        match: dict = {
            "user_id": user_id,
            "created_at": {"$gte": start, "$lte": end},
        }
        if item_id:
            match["item_id"] = item_id

        pipeline = [
            {"$match": match},
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$created_at", "unit": "day"}},
                "orders": {"$sum": 1},
                "revenue": {"$sum": {"$ifNull": ["$total", 0]}},
            }},
            {"$sort": {"_id": 1}},
        ]

        cursor = Order.get_pymongo_collection().aggregate(pipeline)
        rows = await cursor.to_list(length=None)
        return {
            row["_id"].date(): OrderDailyTrendBucket(
                orders=row["orders"],
                revenue=round(row["revenue"], 2),
            )
            for row in rows
        }

    # ------------------------------------------------------------------
    # Read — per-item analytics
    # ------------------------------------------------------------------

    async def get_item_views(
        self,
        item_id: PydanticObjectId,
        store_id: PydanticObjectId,
        start: datetime,
        end: datetime,
    ) -> int:
        pipeline = [
            {"$match": {"item_id": item_id, "store_id": store_id, "date": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": None, "views": {"$sum": "$views"}}},
        ]
        cursor = ItemDailyStat.get_pymongo_collection().aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0].get("views", 0) if result else 0

    async def get_item_daily_views(
        self,
        item_id: PydanticObjectId,
        store_id: PydanticObjectId,
        start: datetime,
        end: datetime,
    ) -> dict[date, int]:
        pipeline = [
            {"$match": {"item_id": item_id, "store_id": store_id, "date": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": "$date", "views": {"$sum": "$views"}}},
            {"$sort": {"_id": 1}},
        ]
        cursor = ItemDailyStat.get_pymongo_collection().aggregate(pipeline)
        rows = await cursor.to_list(length=None)
        return {row["_id"].date(): row["views"] for row in rows}

