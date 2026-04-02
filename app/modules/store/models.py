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
    primary: str = "#22c55e"
    background_type: BackgroundType = BackgroundType.COLOR
    background: str = "#0a0a0a"
    background_image: str = ""
    text: str = "#ffffff"
    font: Font = Font.INTER


class ProfileConfig(BaseModel):
    title: str = ""
    bio: str = ""


class PageConfig(BaseModel):
    layout: Layout = Layout.LIST
    button_variant: ButtonVariant = ButtonVariant.OUTLINE
    button_shape: ButtonShape = ButtonShape.ROUNDED
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    profile: ProfileConfig = Field(default_factory=ProfileConfig)


class Store(BaseDocument):
    user_id: PydanticObjectId
    store_url: Indexed(str, unique=True)
    logo: File | None = None
    qr_code: FileResponse | None = None
    links: list[Link] = Field(default_factory=list)
    template_id: TemplateId = TemplateId.TEMPLATE_A
    config: PageConfig = Field(default_factory=PageConfig)
    is_published: bool = False

    class Settings:
        name = "stores"
        indexes = [
            IndexModel([("user_id", ASCENDING)], unique=True),
        ]
