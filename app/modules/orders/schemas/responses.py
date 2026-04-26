from pydantic import BaseModel, ConfigDict, computed_field

from app.core.enums import DeliveryStatus, ItemType, OrderStatus, RecordSource
from app.modules.orders.models import PaymentDetails
from app.modules.orders.schemas.base import OrderBase
from app.modules.storage.schemas import FileResponse
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin
from beanie import PydanticObjectId


class OrderCustomerResponse(BaseModel):
    id: PydanticObjectId
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OrderItemResponse(BaseModel):
    id: PydanticObjectId
    name: str
    price: float
    quantity: int
    subtotal: float
    type: ItemType
    thumbnail: FileResponse | None = None
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(OrderBase, BaseModelWithId, TimeMixin):
    order_number: str | None = None
    customer: OrderCustomerResponse
    items: list[OrderItemResponse]
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
