import datetime
from pydantic import BaseModel, Field

from app.core.enums import ExpenseCategory, ExpensePaymentMethod


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    category: ExpenseCategory
    payment_method: ExpensePaymentMethod
    date: datetime.date
    notes: str | None = Field(default=None, max_length=1000)


class ExpenseUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    amount: float | None = Field(None, gt=0)
    category: ExpenseCategory | None = None
    payment_method: ExpensePaymentMethod | None = None
    date: datetime.date | None = None
    notes: str | None = Field(default=None, max_length=1000)
