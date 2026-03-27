from pydantic import ConfigDict

from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin, TenantMixin

from .base import CustomerBase


class CustomerResponse(CustomerBase, BaseModelWithId, TimeMixin, TenantMixin):
    is_favourite: bool
    model_config = ConfigDict(from_attributes=True)
