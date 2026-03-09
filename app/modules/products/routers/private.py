import math
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.core.context import RequestContext
from app.core.database import get_session
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import Pagination, PaginatedResponse
from app.modules.auth.auth.dependencies import get_request_context
from app.modules.products.dependencies import ProductService, get_product_service
from app.modules.products.schemas import (
    ProductCreate,
    ProductFilters,
    ProductResponse,
    ProductUpdate,
)
from app.modules.products.docs import ProductDocs

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "/{product_id}",
    response_model=SingleResponse[ProductResponse],
    summary=ProductDocs.GetOwnProduct.summary,
    description=ProductDocs.GetOwnProduct.description,
    responses=ProductDocs.GetOwnProduct.responses,
)
async def get_product_by_id(
    product_id: PydanticObjectId,
    product_service: ProductService = Depends(get_product_service),
    ctx: RequestContext = Depends(get_request_context),
) -> SingleResponse[ProductResponse]:
    product = await product_service.get_own_by_id(ctx, product_id)
    return SingleResponse[ProductResponse](data=product)


@router.get(
    "",
    response_model=PaginatedResponse[ProductResponse],
    summary=ProductDocs.ListOwnProducts.summary,
    description=ProductDocs.ListOwnProducts.description,
    responses=ProductDocs.ListOwnProducts.responses,
)
async def list_products(
    pagination: Pagination = Depends(),
    filters: ProductFilters = Depends(),
    ctx: RequestContext = Depends(get_request_context),
    product_service: ProductService = Depends(get_product_service),
) -> PaginatedResponse[ProductResponse]:
    total, products = await product_service.get_own_list(
        ctx=ctx,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[ProductResponse](
        data=products,
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
    response_model=SingleResponse[ProductResponse],
    summary=ProductDocs.CreateProduct.summary,
    description=ProductDocs.CreateProduct.description,
    responses=ProductDocs.CreateProduct.responses,
)
async def create_product(
    body: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> SingleResponse[ProductResponse]:
    product = await product_service.create(ctx, body, session)
    return SingleResponse[ProductResponse](data=product)


# ---------------------------------------------------------------------
# PATCH
# ---------------------------------------------------------------------
@router.patch(
    "/{product_id}",
    response_model=SingleResponse[ProductResponse],
    summary=ProductDocs.UpdateOwnProduct.summary,
    description=ProductDocs.UpdateOwnProduct.description,
    responses=ProductDocs.UpdateOwnProduct.responses,
)
async def update_product(
    product_id: PydanticObjectId,
    body: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> SingleResponse[ProductResponse]:
    product = await product_service.update_own_by_id(
        ctx,
        product_id,
        body,
        session,
    )
    return SingleResponse[ProductResponse](data=product)


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=ProductDocs.DeleteOwnProduct.summary,
    description=ProductDocs.DeleteOwnProduct.description,
    responses=ProductDocs.DeleteOwnProduct.responses,
)
async def delete_product(
    product_id: PydanticObjectId,
    product_service: ProductService = Depends(get_product_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> None:
    await product_service.delete_own_by_id(ctx, product_id, session)
