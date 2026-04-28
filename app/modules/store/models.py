from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import ASCENDING, IndexModel

from app.core.enums import (
    BackgroundType,
    ButtonShape,
    ButtonVariant,
    Font,
    Layout,
    TemplateId,
)
from app.shared.models.base import BaseDocument
from app.shared.schemas.common import Link
from app.modules.storage.models import File
from app.modules.storage.schemas import FileResponse


class ThemeConfig(BaseModel):
    primary: str
    background_type: BackgroundType
    background: str
    background_image: File | None
    text: str
    font: Font


class ProfileConfig(BaseModel):
    title: str
    bio: str


class PageConfig(BaseModel):
    layout: Layout
    button_variant: ButtonVariant
    button_shape: ButtonShape
    theme: ThemeConfig
    profile: ProfileConfig


class Store(BaseDocument):
    user_id: PydanticObjectId
    store_url: Indexed(str, unique=True)
    currency: str | None = None
    logo: File | None
    qr_code: FileResponse | None
    links: list[Link]
    template_id: TemplateId
    config: PageConfig

    class Settings:
        name = "stores"
        indexes = [
            IndexModel([("user_id", ASCENDING)], unique=True),
        ]
