from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import BackgroundType, ButtonShape, ButtonVariant, Font, Layout, TemplateId
from app.modules.storage.schemas import FileInput
from app.shared.schemas.common import Link

_BG_IMG_EX = [{"id": "temp-uuid", "key": "temp/backgrounds/abc.jpg", "url": None}]


class ThemeConfigRequest(BaseModel):
    primary: str = Field(..., examples=["#22c55e"])
    background_type: BackgroundType = Field(..., examples=[BackgroundType.COLOR])
    background: str = Field(..., examples=["#0a0a0a"])
    background_image: FileInput | None = Field(..., examples=_BG_IMG_EX)
    text: str = Field(..., examples=["#ffffff"])
    font: Font = Field(..., examples=[Font.INTER])
    model_config = ConfigDict(from_attributes=True)


class ProfileConfigRequest(BaseModel):
    title: str = Field(..., examples=["My Page"])
    bio: str = Field(..., examples=["Short bio shown on the store."])
    model_config = ConfigDict(from_attributes=True)


class PageConfigRequest(BaseModel):
    layout: Layout = Field(..., examples=[Layout.LIST])
    button_variant: ButtonVariant = Field(..., examples=[ButtonVariant.OUTLINE])
    button_shape: ButtonShape = Field(..., examples=[ButtonShape.ROUNDED])
    theme: ThemeConfigRequest = Field(...)
    profile: ProfileConfigRequest = Field(...)
    model_config = ConfigDict(from_attributes=True)


_STORE_UPDATE_EXAMPLE = {
    "logo": None,
    "links": [{"name": "Site", "url": "https://example.com"}],
    "template_id": "TEMPLATE_A",
    "config": {
        "layout": "LIST",
        "button_variant": "OUTLINE",
        "button_shape": "ROUNDED",
        "theme": {"primary": "#22c55e", "background_type": "COLOR", "background": "#0a0a0a", "background_image": None, "text": "#ffffff", "font": "INTER"},
        "profile": {"title": "My Page", "bio": ""},
    },
}


class StoreUpdate(BaseModel):
    logo: FileInput | None = Field(...)
    links: list[Link] = Field(...)
    template_id: TemplateId = Field(..., examples=[TemplateId.TEMPLATE_A])
    config: PageConfigRequest = Field(...)
    model_config = ConfigDict(from_attributes=True)

