from app.modules.storage.schemas import FileResponse
from app.shared.schemas.base import BaseModelWithId
from .base import StoreBase, ThemeConfigBase, PageConfigBase, ProfileConfigBase
from beanie import PydanticObjectId


class ThemeConfigResponse(ThemeConfigBase):
    pass


class ProfileConfigResponse(ProfileConfigBase):
    pass


class PageConfigResponse(PageConfigBase):
    pass


class StoreResponse(StoreBase, BaseModelWithId):
    user_id: PydanticObjectId
    qr_code: FileResponse | None = None

class StorePublicResponse(StoreBase):
    qr_code: FileResponse | None = None
