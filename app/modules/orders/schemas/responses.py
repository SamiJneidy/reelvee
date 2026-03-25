from pydantic import ConfigDict, computed_field

from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin

from .base import OrderBase


class OrderResponse(OrderBase, BaseModelWithId, TimeMixin):
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def profit(self) -> float | None:
        if self.total is not None and self.total_cost is not None:
            return self.total - self.total_cost
        return None
