from app.modules.storage.schemas import FileResponse
from app.shared.schemas.base import BaseModelWithId
from .base import StoreBase, ThemeConfigBase, PageConfigBase, ProfileConfigBase


class ThemeConfigResponse(ThemeConfigBase):
    pass


class ProfileConfigResponse(ProfileConfigBase):
    pass


class PageConfigResponse(PageConfigBase):
    pass


class StoreResponse(StoreBase, BaseModelWithId):
    qr_code: FileResponse | None = None

