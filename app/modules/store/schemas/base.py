from pydantic import BaseModel, Field

from app.core.enums import (
    BackgroundType,
    ButtonShape,
    ButtonVariant,
    Font,
    Layout,
    TemplateId,
)
from app.modules.storage.schemas import FileResponse
from app.shared.schemas.common import Link


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


class StoreBase(BaseModel):
    store_url: str | None = None
    logo: FileResponse | None = None
    links: list[Link] = Field(default_factory=list)
    template_id: TemplateId = TemplateId.TEMPLATE_A
    config: PageConfig = Field(default_factory=PageConfig)
    is_published: bool = False
