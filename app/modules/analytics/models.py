from beanie import Document, PydanticObjectId
from datetime import datetime
from pymongo import ASCENDING, IndexModel

from app.core.enums import OSType


class StoreDailyStat(Document):
    store_id: PydanticObjectId
    date: datetime          # UTC midnight, e.g. 2026-04-07T00:00:00Z
    store_views: int = 0
    item_views: int = 0

    class Settings:
        name = "store_daily_stats"
        indexes = [
            IndexModel(
                [("store_id", ASCENDING), ("date", ASCENDING)],
                unique=True,
            ),
        ]


class StoreDailyCountry(Document):
    store_id: PydanticObjectId
    date: datetime
    country_code: str       # ISO 3166-1 alpha-2, e.g. "EG", "SA" — "unknown" as fallback
    visits: int = 0

    class Settings:
        name = "store_daily_countries"
        indexes = [
            IndexModel(
                [("store_id", ASCENDING), ("date", ASCENDING), ("country_code", ASCENDING)],
                unique=True,
            ),
        ]


class StoreDailyOS(Document):
    store_id: PydanticObjectId
    date: datetime
    os_type: OSType
    visits: int = 0

    class Settings:
        name = "store_daily_os"
        indexes = [
            IndexModel(
                [("store_id", ASCENDING), ("date", ASCENDING), ("os_type", ASCENDING)],
                unique=True,
            ),
        ]


class ItemDailyStat(Document):
    item_id: PydanticObjectId
    store_id: PydanticObjectId  # denormalized for store-level top-items queries
    date: datetime
    views: int = 0

    class Settings:
        name = "item_daily_stats"
        indexes = [
            IndexModel(
                [("item_id", ASCENDING), ("date", ASCENDING)],
                unique=True,
            ),
            IndexModel(
                [("store_id", ASCENDING), ("date", ASCENDING)],
            ),
        ]
