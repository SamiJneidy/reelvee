from pydantic import ConfigDict

from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin

from .base import CategoryBase


class CategoryResponse(CategoryBase, BaseModelWithId, TimeMixin):
    model_config = ConfigDict(from_attributes=True)
