from typing import Any

from beanie import PydanticObjectId

from app.modules.store.models import Store


class StoreRepository:
    async def get_by_user_id(self, user_id: PydanticObjectId, session=None) -> Store | None:
        return await Store.find_one(Store.user_id == user_id, session=session)

    async def get_by_store_url(self, store_url: str, session=None) -> Store | None:
        return await Store.find_one(Store.store_url == store_url.lower().strip(), session=session)

    async def create(self, data: dict[str, Any], session=None) -> Store:
        store = Store(**data)
        await store.insert(session=session)
        return store

    async def update_by_user_id(
        self, user_id: PydanticObjectId, data: dict[str, Any], session=None
    ) -> Store | None:
        store = await self.get_by_user_id(user_id, session=session)
        if store is None:
            return None
        for key, value in data.items():
            if hasattr(Store, key):
                setattr(store, key, value)
        await store.save(session=session)
        return store

    async def delete_by_user_id(self, user_id: PydanticObjectId, session=None) -> None:
        store = await self.get_by_user_id(user_id, session=session)
        if store is not None:
            await store.delete(session=session)
