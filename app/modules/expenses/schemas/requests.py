import datetime
from pydantic import BaseModel, Field

from app.core.enums import ExpenseCategory, ExpensePaymentMethod


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    category: ExpenseCategory = Field(...)
    payment_method: ExpensePaymentMethod = Field(...)
    date: datetime.date = Field(...)
    notes: str | None = Field(None, max_length=1000)


class ExpenseUpdate(BaseModel):
    title: str = Field(None, min_length=1, max_length=200)
    amount: float = Field(None, gt=0)
    category: ExpenseCategory = Field(None)
    payment_method: ExpensePaymentMethod = Field(None)
    date: datetime.date = Field(None)
    notes: str | None = Field(None, max_length=1000)
