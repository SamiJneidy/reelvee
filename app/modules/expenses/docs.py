"""OpenAPI documentation for expense endpoints."""

from typing import Any

from fastapi import status

from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.expenses.exceptions import ExpenseNotFoundException
from app.shared.utils.docs import error_response


class ExpenseDocs:
    class ListOwnExpenses:
        summary = "List my expenses"
        description = (
            "Returns a paginated list of expenses for the authenticated store, "
            "sorted by expense date in descending order. "
            "Optional filters: category, payment_method, date_from, date_to."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class GetOwnExpense:
        summary = "Get my expense by ID"
        description = (
            "Returns a single expense by ID. "
            "Only expenses belonging to the authenticated store."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ExpenseNotFoundException),
        }

    class CreateExpense:
        summary = "Create expense"
        description = "Creates a new expense for the authenticated store."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class UpdateOwnExpense:
        summary = "Update my expense"
        description = (
            "Updates an existing expense by ID. "
            "Only provided fields are updated."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ExpenseNotFoundException),
        }

    class DeleteOwnExpense:
        summary = "Delete my expense"
        description = "Deletes an expense by ID."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ExpenseNotFoundException),
        }

    class GetOwnExpenseSummary:
        summary = "Get my expenses summary"
        description = (
            "Returns expense totals for the authenticated store, "
            "including overall total and grouped totals by category."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }
