import argparse
import asyncio
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

from beanie import PydanticObjectId

# Make script runnable from any working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import client, init_db
from app.core.enums import OSType
from app.modules.analytics.models import ItemDailyStat, StoreDailyCountry, StoreDailyOS, StoreDailyStat
from app.modules.items.models import Item
from app.modules.store.models import Store


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed simple analytics test data for charts.")
    parser.add_argument("--store-id", default=None, help="Store ObjectId. If omitted, first store is used.")
    parser.add_argument("--days", type=int, default=10, help="How many days to seed. Default: 10")
    parser.add_argument("--clear", action="store_true", help="Delete existing analytics data in this range first.")
    return parser.parse_args()

def _day_dt(days_ago: int) -> datetime:
    day = datetime.now(timezone.utc).date() - timedelta(days=days_ago)
    return datetime.combine(day, time.min, tzinfo=timezone.utc)


async def _resolve_store(store_id_raw: str | None) -> Store:
    if store_id_raw:
        store = await Store.get(PydanticObjectId(store_id_raw))
        if not store:
            raise ValueError(f"Store not found: {store_id_raw}")
        return store

    store = await Store.find_all().limit(1).first_or_none()
    if not store:
        raise ValueError("No stores found. Create at least one store first.")
    return store


async def seed() -> None:
    print("Seeding analytics data...")
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be >= 1")

    await init_db()
    
    print("Database initialized.")

    store = await _resolve_store(args.store_id)
    store_id = store.id
    if not store_id:
        raise ValueError("Resolved store has no id.")

    items = await Item.find(Item.user_id == store.user_id).limit(5).to_list()
    item_ids = [item.id for item in items if item.id is not None]

    start_dt = _day_dt(args.days - 1)
    end_dt = _day_dt(0)

    if args.clear:
        await StoreDailyStat.find(StoreDailyStat.store_id == store_id, StoreDailyStat.date >= start_dt, StoreDailyStat.date <= end_dt).delete()
        await StoreDailyCountry.find(StoreDailyCountry.store_id == store_id, StoreDailyCountry.date >= start_dt, StoreDailyCountry.date <= end_dt).delete()
        await StoreDailyOS.find(StoreDailyOS.store_id == store_id, StoreDailyOS.date >= start_dt, StoreDailyOS.date <= end_dt).delete()
        await ItemDailyStat.find(ItemDailyStat.store_id == store_id, ItemDailyStat.date >= start_dt, ItemDailyStat.date <= end_dt).delete()

    for i in range(args.days):
        dt = _day_dt(args.days - 1 - i)

        # simple predictable values with slight variation
        store_views = 60 + (i * 7)
        item_views = 120 + (i * 11)

        await StoreDailyStat.find_one(StoreDailyStat.store_id == store_id, StoreDailyStat.date == dt).upsert(
            {"$set": {"store_views": store_views, "item_views": item_views}},
            on_insert=StoreDailyStat(store_id=store_id, date=dt, store_views=store_views, item_views=item_views),
        )

        await StoreDailyCountry.find_one(
            StoreDailyCountry.store_id == store_id,
            StoreDailyCountry.date == dt,
            StoreDailyCountry.country_code == "EG",
        ).upsert(
            {"$set": {"visits": int(store_views * 0.5)}},
            on_insert=StoreDailyCountry(store_id=store_id, date=dt, country_code="EG", visits=int(store_views * 0.5)),
        )
        await StoreDailyCountry.find_one(
            StoreDailyCountry.store_id == store_id,
            StoreDailyCountry.date == dt,
            StoreDailyCountry.country_code == "SA",
        ).upsert(
            {"$set": {"visits": int(store_views * 0.3)}},
            on_insert=StoreDailyCountry(store_id=store_id, date=dt, country_code="SA", visits=int(store_views * 0.3)),
        )
        await StoreDailyCountry.find_one(
            StoreDailyCountry.store_id == store_id,
            StoreDailyCountry.date == dt,
            StoreDailyCountry.country_code == "US",
        ).upsert(
            {"$set": {"visits": int(store_views * 0.2)}},
            on_insert=StoreDailyCountry(store_id=store_id, date=dt, country_code="US", visits=int(store_views * 0.2)),
        )

        await StoreDailyOS.find_one(StoreDailyOS.store_id == store_id, StoreDailyOS.date == dt, StoreDailyOS.os_type == OSType.android).upsert(
            {"$set": {"visits": int(store_views * 0.6)}},
            on_insert=StoreDailyOS(store_id=store_id, date=dt, os_type=OSType.android, visits=int(store_views * 0.6)),
        )
        await StoreDailyOS.find_one(StoreDailyOS.store_id == store_id, StoreDailyOS.date == dt, StoreDailyOS.os_type == OSType.ios).upsert(
            {"$set": {"visits": int(store_views * 0.3)}},
            on_insert=StoreDailyOS(store_id=store_id, date=dt, os_type=OSType.ios, visits=int(store_views * 0.3)),
        )
        await StoreDailyOS.find_one(StoreDailyOS.store_id == store_id, StoreDailyOS.date == dt, StoreDailyOS.os_type == OSType.windows).upsert(
            {"$set": {"visits": int(store_views * 0.1)}},
            on_insert=StoreDailyOS(store_id=store_id, date=dt, os_type=OSType.windows, visits=int(store_views * 0.1)),
        )

        if item_ids:
            for idx, item_id in enumerate(item_ids):
                views = int(item_views * (0.4 if idx == 0 else 0.15))
                await ItemDailyStat.find_one(
                    ItemDailyStat.item_id == item_id,
                    ItemDailyStat.store_id == store_id,
                    ItemDailyStat.date == dt,
                ).upsert(
                    {"$set": {"views": views}},
                    on_insert=ItemDailyStat(item_id=item_id, store_id=store_id, date=dt, views=views),
                )

    print(f"Seeded analytics data for store={store_id} ({args.days} days).")


async def _main() -> None:
    try:
        await seed()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(_main())
