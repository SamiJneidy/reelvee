from pydantic import BaseModel, ConfigDict

from app.core.enums import DeliveryStatus, OrderStatus, RecordSource
from app.modules.orders.models import OrderCustomer, OrderItem, PaymentDetails
from app.modules.orders.schemas.base import OrderBase
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin


class OrderInternal(OrderBase, BaseModelWithId, TimeMixin):
    customer: OrderCustomer
    items: list[OrderItem]
    is_read: bool
    source: RecordSource
    status: OrderStatus
    model_config = ConfigDict(from_attributes=True)


class OrderUpdateInternal(BaseModel):
    items: list[OrderItem] | None = None
    total: float | None = None
    total_cost: float | None = None
    payment: PaymentDetails | None = None
    source: RecordSource | None = None
    status: OrderStatus | None = None
    is_read: bool | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
