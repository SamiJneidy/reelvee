from pydantic import ConfigDict, computed_field

from app.core.enums import DeliveryStatus, RecordSource, OrderStatus
from app.modules.items.schemas.responses import ItemMinimalResponse
from app.modules.orders.models import PaymentDetails
from app.modules.customers.schemas.responses import CustomerResponse
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin

from .base import OrderBase


class OrderResponse(OrderBase, BaseModelWithId, TimeMixin):
    item: ItemMinimalResponse
    customer: CustomerResponse
    item_price: float | None = None
    quantity: float | None = None
    total: float | None = None
    total_cost: float | None = None
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
    is_read: bool
    source: RecordSource
    status: OrderStatus
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def profit(self) -> float | None:
        if self.total is not None and self.total_cost is not None:
            return self.total - self.total_cost
        return None
