import math
from fastapi import APIRouter, Depends
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import Pagination, PaginatedResponse
from app.modules.items.dependencies import ItemService, get_item_service
from app.modules.store.dependencies import StoreService, get_store_service
from app.modules.items.schemas import (
    ItemFilters,
    ItemPublicResponse,
)
from app.modules.items.docs import ItemPublicDocs

router = APIRouter(
    prefix="/{store_url}",
    tags=["Items"],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "/items",
    response_model=PaginatedResponse[ItemPublicResponse],
    summary=ItemPublicDocs.ListStoreItems.summary,
    description=ItemPublicDocs.ListStoreItems.description,
    responses=ItemPublicDocs.ListStoreItems.responses,
)
async def list_items(
    store_url: str,
    pagination: Pagination = Depends(),
    filters: ItemFilters = Depends(),
    store_service: StoreService = Depends(get_store_service),
    item_service: ItemService = Depends(get_item_service),
) -> PaginatedResponse[ItemPublicResponse]:
    store = await store_service.get_by_store_url(store_url)
    total, items = await item_service.get_list(
        user_id=store.user_id,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[ItemPublicResponse](
        data=items,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/items/{slug}",
    response_model=SingleResponse[ItemPublicResponse],
    summary=ItemPublicDocs.GetStoreItemBySlug.summary,
    description=ItemPublicDocs.GetStoreItemBySlug.description,
    responses=ItemPublicDocs.GetStoreItemBySlug.responses,
)
async def get_item_by_slug(
    store_url: str,
    slug: str,
    store_service: StoreService = Depends(get_store_service),
    item_service: ItemService = Depends(get_item_service),
) -> SingleResponse[ItemPublicResponse]:
    store = await store_service.get_by_store_url(store_url)
    item = await item_service.get_by_slug(store.user_id, slug)
    return SingleResponse[ItemPublicResponse](data=item)
