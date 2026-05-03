from typing import Any

from beanie import PydanticObjectId

from app.modules.expenses.models import Expense


class ExpenseRepository:
    def _build_filters(self, filters: dict[str, Any] | None = None) -> list:
        filters = filters or {}
        filters_list = []
        if filters.get("category") is not None:
            filters_list.append(Expense.category == filters["category"])
        if filters.get("payment_method") is not None:
            filters_list.append(Expense.payment_method == filters["payment_method"])
        if filters.get("date_from") is not None:
            filters_list.append(Expense.date >= filters["date_from"])
        if filters.get("date_to") is not None:
            filters_list.append(Expense.date <= filters["date_to"])
        return filters_list

    async def get_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> Expense | None:
        return await Expense.find_one(
            Expense.user_id == user_id,
            Expense.id == id,
            session=session,
        )

    async def get_list(
        self,
        user_id: PydanticObjectId,
        skip: int = 0,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Expense]]:
        filters_list = self._build_filters(filters)
        filters_list.append(Expense.user_id == user_id)
        query = Expense.find(*filters_list, session=session)
        total = await query.count()
        expenses = await query.sort(-Expense.date).skip(skip).limit(limit).to_list()
        return total, expenses

    async def create(self, data: dict[str, Any], session=None) -> Expense:
        expense = Expense(**data)
        await expense.insert(session=session)
        return expense

    async def update_by_id(
        self,
        user_id: PydanticObjectId,
        id: PydanticObjectId,
        data: dict[str, Any],
        session=None,
    ) -> Expense | None:
        expense = await Expense.find_one(
            Expense.user_id == user_id,
            Expense.id == id,
            session=session,
        )
        if expense is None:
            return None
        for key, value in data.items():
            if hasattr(Expense, key):
                setattr(expense, key, value)
        await expense.save(session=session)
        return expense

    async def delete_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> None:
        expense = await Expense.find_one(
            Expense.user_id == user_id,
            Expense.id == id,
            session=session,
        )
        if expense is not None:
            await expense.delete(session=session)

    async def get_summary(
        self,
        user_id: PydanticObjectId,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> dict[str, Any]:
        filters_list = self._build_filters(filters)
        filters_list.append(Expense.user_id == user_id)
        expenses = await Expense.find(*filters_list, session=session).to_list()
        by_category: dict[str, float] = {}
        total = 0.0
        for expense in expenses:
            total += expense.amount
            key = expense.category.value
            by_category[key] = by_category.get(key, 0.0) + expense.amount
        return {
            "total": total,
            "by_category": by_category,
        }
