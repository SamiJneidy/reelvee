from datetime import date

from pydantic import BaseModel

from app.core.enums import ExpenseCategory, ExpensePaymentMethod


class ExpenseBase(BaseModel):
    title: str
    amount: float
    category: ExpenseCategory
    payment_method: ExpensePaymentMethod
    date: date
    notes: str | None = None
