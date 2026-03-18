import math
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.core.context import RequestContext
from app.core.database import get_session
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import Pagination, PaginatedResponse
from app.modules.auth.dependencies import get_request_context
from app.modules.items.dependencies import ItemService, get_item_service
from app.modules.items.schemas import (
    ItemCreate,
    ItemFilters,
    ItemResponse,
    ItemUpdate,
)
from app.modules.items.docs import ItemDocs

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "/{item_id}",
    response_model=SingleResponse[ItemResponse],
    summary=ItemDocs.GetOwnItem.summary,
    description=ItemDocs.GetOwnItem.description,
    responses=ItemDocs.GetOwnItem.responses,
)
async def get_item_by_id(
    item_id: PydanticObjectId,
    item_service: ItemService = Depends(get_item_service),
    ctx: RequestContext = Depends(get_request_context),
) -> SingleResponse[ItemResponse]:
    item = await item_service.get_own_by_id(ctx, item_id)
    return SingleResponse[ItemResponse](data=item)


@router.get(
    "",
    response_model=PaginatedResponse[ItemResponse],
    summary=ItemDocs.ListOwnItems.summary,
    description=ItemDocs.ListOwnItems.description,
    responses=ItemDocs.ListOwnItems.responses,
)
async def list_items(
    pagination: Pagination = Depends(),
    filters: ItemFilters = Depends(),
    ctx: RequestContext = Depends(get_request_context),
    item_service: ItemService = Depends(get_item_service),
) -> PaginatedResponse[ItemResponse]:
    total, items = await item_service.get_own_list(
        ctx=ctx,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[ItemResponse](
        data=items,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


# ---------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------
@router.post(
    "",
    response_model=SingleResponse[ItemResponse],
    summary=ItemDocs.CreateItem.summary,
    description=ItemDocs.CreateItem.description,
    responses=ItemDocs.CreateItem.responses,
)
async def create_item(
    body: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> SingleResponse[ItemResponse]:
    item = await item_service.create(ctx, body, session)
    return SingleResponse[ItemResponse](data=item)


# ---------------------------------------------------------------------
# PATCH
# ---------------------------------------------------------------------
@router.patch(
    "/{item_id}",
    response_model=SingleResponse[ItemResponse],
    summary=ItemDocs.UpdateOwnItem.summary,
    description=ItemDocs.UpdateOwnItem.description,
    responses=ItemDocs.UpdateOwnItem.responses,
)
async def update_item(
    item_id: PydanticObjectId,
    body: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> SingleResponse[ItemResponse]:
    item = await item_service.update_own_by_id(
        ctx,
        item_id,
        body,
        session,
    )
    return SingleResponse[ItemResponse](data=item)


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=ItemDocs.DeleteOwnItem.summary,
    description=ItemDocs.DeleteOwnItem.description,
    responses=ItemDocs.DeleteOwnItem.responses,
)
async def delete_item(
    item_id: PydanticObjectId,
    item_service: ItemService = Depends(get_item_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> None:
    await item_service.delete_own_by_id(ctx, item_id, session)


@router.delete(
    "/{item_id}/thumbnail",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=ItemDocs.DeleteOwnThumbnail.summary,
    description=ItemDocs.DeleteOwnThumbnail.description,
    responses=ItemDocs.DeleteOwnThumbnail.responses,
)
async def delete_thumbnail(
    item_id: PydanticObjectId,
    item_service: ItemService = Depends(get_item_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> None:
    await item_service.delete_thumbnail(ctx, item_id, session)