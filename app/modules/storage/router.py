from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.context import RequestContext
from app.core.enums import TempFileUploadPath
from app.modules.auth.dependencies import get_request_context
from app.modules.storage.dependencies import StorageService, get_storage_service
from app.modules.storage.docs import StorageDocs
from app.modules.storage.schemas import FileInput, PresignedURLRequest, PresignedURLResponse
from app.shared.schemas import SingleResponse


router = APIRouter(
    prefix="/storage",
    tags=["Storage"],
)


@router.post(
    "/upload",
    response_model=SingleResponse[PresignedURLResponse],
    summary=StorageDocs.UploadFile.summary,
    description=StorageDocs.UploadFile.description,
    responses=StorageDocs.UploadFile.responses,
)
async def upload_file(
    body: PresignedURLRequest,
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    # ctx: RequestContext = Depends(get_request_context),
) -> SingleResponse[PresignedURLResponse]:
    data = await storage_service.generate_upload_url(
        path=body.path.value,
        filename=body.filename,
        content_type=body.content_type,
    )
    return SingleResponse[PresignedURLResponse](data=data)

@router.post(
    "/upload/simulate-frontend",
    response_model=SingleResponse[FileInput],
    summary="Simulate frontend upload using presigned URL",
)
async def upload_file_simulated(
    file: Annotated[UploadFile, File()],
    presigned_id: Annotated[str, Form()],
    presigned_key: Annotated[str, Form()],
    presigned_url: Annotated[str, Form()],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> SingleResponse[FileInput]:

    content = await file.read()

    presigned_response = {
        "id": presigned_id,
        "key": presigned_key,
        "upload_url": presigned_url,
    }

    data = await storage_service.upload_file(
        presigned_response=presigned_response,
        content=content,
        filename=file.filename,
        content_type=file.content_type,
    )

    return SingleResponse[FileInput](data=data)

