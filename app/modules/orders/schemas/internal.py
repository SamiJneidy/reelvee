from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict

from app.core.enums import DeliveryStatus, OrderStatus, RecordSource
from app.modules.orders.models import PaymentDetails
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin

from .base import OrderBase


class OrderInternal(OrderBase, BaseModelWithId, TimeMixin):
    model_config = ConfigDict(from_attributes=True)


class OrderUpdateInternal(BaseModel):
    item_id: PydanticObjectId | None = None
    item_price: float | None = None
    quantity: int | None = None
    total: float | None = None
    total_cost: float | None = None
    payment: PaymentDetails | None = None
    source: RecordSource | None = None
    status: OrderStatus | None = None
    is_read: bool | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    owner_notes: str | None = None
