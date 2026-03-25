from beanie import PydanticObjectId
from pymongo import IndexModel, ASCENDING

from app.core.enums import CustomerStatus, RecordSource
from app.shared.models.base import BaseDocument


class Customer(BaseDocument):
    user_id: PydanticObjectId
    name: str
    country_code: str
    phone: str
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    source: RecordSource
    is_favourite: bool = False
    status: CustomerStatus = CustomerStatus.ACTIVE

    class Settings:
        name = "customers"
        indexes = [
            IndexModel([("user_id", ASCENDING), ("phone", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING), ("is_favourite", ASCENDING)]),
        ]
