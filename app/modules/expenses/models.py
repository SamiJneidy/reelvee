from datetime import date
from pymongo import ASCENDING, DESCENDING, IndexModel

from beanie import PydanticObjectId

from app.core.enums import ExpenseCategory, ExpensePaymentMethod

from app.shared.models.base import BaseDocument


class Expense(BaseDocument):
    user_id: PydanticObjectId
    title: str
    amount: float
    category: ExpenseCategory
    payment_method: ExpensePaymentMethod
    date: date
    notes: str | None = None

    class Settings:
        name = "expenses"
        indexes = [
            IndexModel([("user_id", ASCENDING), ("date", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("category", ASCENDING)]),
        ]
