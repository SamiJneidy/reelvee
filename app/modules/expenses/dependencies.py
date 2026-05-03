from typing import Annotated

from fastapi import Depends

from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.service import ExpenseService


def get_expense_repository() -> ExpenseRepository:
    return ExpenseRepository()


def get_expense_service(
    expense_repo: Annotated[ExpenseRepository, Depends(get_expense_repository)],
) -> ExpenseService:
    return ExpenseService(expense_repo)
