from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import TempFileUploadPath


class PresignedURLRequest(BaseModel):
    filename: str
    path: TempFileUploadPath
    content_type: str | None = None


class PresignedURLResponse(BaseModel):
    id: str
    key: str
    upload_url: str


class FileInput(BaseModel):
    id: str
    key: str
    url: str | None = Field(
        None,
        description="The public URL of the file. Omit in case of new file upload. Keep for existing files.",
    )


class FileResponse(BaseModel):
    id: str
    key: str
    url: str
    model_config = ConfigDict(from_attributes=True)
