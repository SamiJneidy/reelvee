from beanie import PydanticObjectId
from pydantic import BaseModel

from app.core.enums import DeliveryStatus, OrderStatus, RecordSource


class OrderFilters(BaseModel):
    order_number: str | None = None
    status: OrderStatus | None = None
    is_read: bool | None = None
    source: RecordSource | None = None
    customer_id: PydanticObjectId | None = None
    item_id: PydanticObjectId | None = None
    delivery_status: DeliveryStatus | None = None
