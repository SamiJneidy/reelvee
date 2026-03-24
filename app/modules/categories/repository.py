from beanie import PydanticObjectId

from app.modules.categories.models import Category


class CategoryRepository:
    async def get_by_id(self, id: PydanticObjectId, session=None) -> Category | None:
        return await Category.get(id, session=session)

    async def get_by_name(self, name: str, session=None) -> Category | None:
        return await Category.find_one(Category.name == name.strip().lower(), session=session)

    async def get_categories(
        self,
        skip: int = 0,
        limit: int = 20,
        session=None,
    ) -> tuple[int, list[Category]]:
        query = Category.find(session=session)
        total = await query.count()
        categories = await query.sort(Category.name).skip(skip).limit(limit).to_list()
        return total, categories

    async def create(self, data: dict, session=None) -> Category:
        category = Category(**data)
        await category.insert(session=session)
        return category

    async def update_by_id(self, id: PydanticObjectId, data: dict, session=None) -> Category | None:
        category = await Category.get(id, session=session)
        if category is None:
            return None
        for key, value in data.items():
            if hasattr(Category, key):
                setattr(category, key, value)
        await category.save(session=session)
        return category

    async def delete_by_id(self, id: PydanticObjectId, session=None) -> None:
        category = await Category.get(id, session=session)
        if category is not None:
            await category.delete(session=session)
