from pydantic import ConfigDict

from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin

from .base import CustomerBase


class CustomerResponse(CustomerBase, BaseModelWithId, TimeMixin):
    model_config = ConfigDict(from_attributes=True)
