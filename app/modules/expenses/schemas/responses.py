from pydantic import BaseModel
from pydantic import ConfigDict

from app.core.enums import ExpenseCategory
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TenantMixin, TimeMixin

from .base import ExpenseBase


class ExpenseResponse(ExpenseBase, BaseModelWithId, TimeMixin, TenantMixin):
    model_config = ConfigDict(from_attributes=True)


class ExpenseSummaryResponse(BaseModel):
    total: float
    by_category: dict[ExpenseCategory, float]
