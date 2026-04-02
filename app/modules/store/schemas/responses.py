from pydantic import ConfigDict

from app.modules.storage.schemas import FileResponse
from app.shared.schemas.base import BaseModelWithId
from .base import StoreBase


class StoreResponse(StoreBase, BaseModelWithId):
    qr_code: FileResponse | None = None
    model_config = ConfigDict(from_attributes=True)
