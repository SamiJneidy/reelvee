from beanie import PydanticObjectId

from app.core.context import SessionContext
from app.modules.expenses.exceptions import ExpenseNotFoundException
from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.schemas import (
    ExpenseCreate,
    ExpenseFilters,
    ExpenseResponse,
    ExpenseSummaryResponse,
    ExpenseUpdate,
)


class ExpenseService:
    def __init__(self, expense_repo: ExpenseRepository) -> None:
        self._repo = expense_repo

    def _to_response(self, expense) -> ExpenseResponse:
        return ExpenseResponse.model_validate(expense)

    async def get_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId
    ) -> ExpenseResponse:
        expense = await self._repo.get_by_id(current_user.user.id, id)
        if not expense:
            raise ExpenseNotFoundException()
        return self._to_response(expense)

    async def get_own_list(
        self,
        current_user: SessionContext,
        skip: int = 0,
        limit: int = 10,
        filters: ExpenseFilters | None = None,
    ) -> tuple[int, list[ExpenseResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, expenses = await self._repo.get_list(
            user_id=current_user.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [self._to_response(e) for e in expenses]

    async def create(
        self, current_user: SessionContext, payload: ExpenseCreate, session=None
    ) -> ExpenseResponse:
        data = payload.model_dump()
        data["user_id"] = current_user.user.id
        expense = await self._repo.create(data, session=session)
        return self._to_response(expense)

    async def update_own_by_id(
        self,
        current_user: SessionContext,
        id: PydanticObjectId,
        payload: ExpenseUpdate,
        session=None,
    ) -> ExpenseResponse:
        expense = await self._repo.get_by_id(current_user.user.id, id)
        if not expense:
            raise ExpenseNotFoundException()
        update_data = payload.model_dump(exclude_none=True)
        updated = await self._repo.update_by_id(
            current_user.user.id,
            id,
            update_data,
            session=session,
        )
        return self._to_response(updated)

    async def delete_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId, session=None
    ) -> None:
        expense = await self._repo.get_by_id(current_user.user.id, id)
        if not expense:
            raise ExpenseNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)

    async def get_own_summary(
        self,
        current_user: SessionContext,
        filters: ExpenseFilters | None = None,
    ) -> ExpenseSummaryResponse:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        summary = await self._repo.get_summary(current_user.user.id, filters=filter_dict)
        return ExpenseSummaryResponse.model_validate(summary)
