from pydantic import BaseModel, ConfigDict, Field

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


class ThemeConfigBase(BaseModel):
    primary: str = "#22c55e"
    background_type: BackgroundType = BackgroundType.COLOR
    background: str = "#0a0a0a"
    background_image: FileResponse | None = None
    text: str = "#ffffff"
    font: Font = Font.INTER

    model_config = ConfigDict(from_attributes=True)


class ProfileConfigBase(BaseModel):
    title: str = ""
    bio: str = ""

    model_config = ConfigDict(from_attributes=True)


class PageConfigBase(BaseModel):
    layout: Layout = Layout.LIST
    button_variant: ButtonVariant = ButtonVariant.OUTLINE
    button_shape: ButtonShape = ButtonShape.ROUNDED
    theme: ThemeConfigBase = Field(default_factory=ThemeConfigBase)
    profile: ProfileConfigBase = Field(default_factory=ProfileConfigBase)

    model_config = ConfigDict(from_attributes=True)


class StoreBase(BaseModel):
    store_url: str | None = None
    logo: FileResponse | None = None
    links: list[Link] = Field(default_factory=list)
    template_id: TemplateId = TemplateId.TEMPLATE_A
    config: PageConfigBase = Field(default_factory=PageConfigBase)

    model_config = ConfigDict(from_attributes=True)