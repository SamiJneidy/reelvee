from datetime import date

from pydantic import BaseModel

from app.core.enums import ExpenseCategory, ExpensePaymentMethod


class ExpenseFilters(BaseModel):
    category: ExpenseCategory | None = None
    payment_method: ExpensePaymentMethod | None = None
    date_from: date | None = None
    date_to: date | None = None
