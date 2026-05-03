import math

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.core.context import SessionContext
from app.core.database import get_session
from app.modules.auth.dependencies import get_current_session
from app.modules.expenses.dependencies import ExpenseService, get_expense_service
from app.modules.expenses.docs import ExpenseDocs
from app.modules.expenses.schemas import (
    ExpenseCreate,
    ExpenseFilters,
    ExpenseResponse,
    ExpenseSummaryResponse,
    ExpenseUpdate,
)
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import PaginatedResponse, Pagination

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.get(
    "",
    response_model=PaginatedResponse[ExpenseResponse],
    summary=ExpenseDocs.ListOwnExpenses.summary,
    description=ExpenseDocs.ListOwnExpenses.description,
    responses=ExpenseDocs.ListOwnExpenses.responses,
)
async def list_expenses(
    pagination: Pagination = Depends(),
    filters: ExpenseFilters = Depends(),
    current_user: SessionContext = Depends(get_current_session),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> PaginatedResponse[ExpenseResponse]:
    total, expenses = await expense_service.get_own_list(
        current_user=current_user,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[ExpenseResponse](
        data=expenses,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/summary",
    response_model=SingleResponse[ExpenseSummaryResponse],
    summary=ExpenseDocs.GetOwnExpenseSummary.summary,
    description=ExpenseDocs.GetOwnExpenseSummary.description,
    responses=ExpenseDocs.GetOwnExpenseSummary.responses,
)
async def get_expenses_summary(
    filters: ExpenseFilters = Depends(),
    current_user: SessionContext = Depends(get_current_session),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> SingleResponse[ExpenseSummaryResponse]:
    summary = await expense_service.get_own_summary(current_user, filters)
    return SingleResponse[ExpenseSummaryResponse](data=summary)


@router.get(
    "/{expense_id}",
    response_model=SingleResponse[ExpenseResponse],
    summary=ExpenseDocs.GetOwnExpense.summary,
    description=ExpenseDocs.GetOwnExpense.description,
    responses=ExpenseDocs.GetOwnExpense.responses,
)
async def get_expense(
    expense_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> SingleResponse[ExpenseResponse]:
    expense = await expense_service.get_own_by_id(current_user, expense_id)
    return SingleResponse[ExpenseResponse](data=expense)


@router.post(
    "",
    response_model=SingleResponse[ExpenseResponse],
    status_code=status.HTTP_201_CREATED,
    summary=ExpenseDocs.CreateExpense.summary,
    description=ExpenseDocs.CreateExpense.description,
    responses=ExpenseDocs.CreateExpense.responses,
)
async def create_expense(
    body: ExpenseCreate,
    current_user: SessionContext = Depends(get_current_session),
    expense_service: ExpenseService = Depends(get_expense_service),
    session=Depends(get_session),
) -> SingleResponse[ExpenseResponse]:
    expense = await expense_service.create(current_user, body, session)
    return SingleResponse[ExpenseResponse](data=expense)


@router.patch(
    "/{expense_id}",
    response_model=SingleResponse[ExpenseResponse],
    summary=ExpenseDocs.UpdateOwnExpense.summary,
    description=ExpenseDocs.UpdateOwnExpense.description,
    responses=ExpenseDocs.UpdateOwnExpense.responses,
)
async def update_expense(
    expense_id: PydanticObjectId,
    body: ExpenseUpdate,
    current_user: SessionContext = Depends(get_current_session),
    expense_service: ExpenseService = Depends(get_expense_service),
    session=Depends(get_session),
) -> SingleResponse[ExpenseResponse]:
    expense = await expense_service.update_own_by_id(
        current_user,
        expense_id,
        body,
        session,
    )
    return SingleResponse[ExpenseResponse](data=expense)


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=ExpenseDocs.DeleteOwnExpense.summary,
    description=ExpenseDocs.DeleteOwnExpense.description,
    responses=ExpenseDocs.DeleteOwnExpense.responses,
)
async def delete_expense(
    expense_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    expense_service: ExpenseService = Depends(get_expense_service),
    session=Depends(get_session),
) -> None:
    await expense_service.delete_own_by_id(current_user, expense_id, session)
