from pydantic import BaseModel, Field

from app.core.enums import TemplateId
from app.modules.storage.schemas import FileInput
from app.modules.store.schemas.base import PageConfig
from app.shared.schemas.common import Link


class StoreUpdate(BaseModel):
    logo: FileInput | None = None
    links: list[Link] | None = None
    template_id: TemplateId | None = None
    config: PageConfig | None = None
    is_published: bool | None = None
