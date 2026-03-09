import math
from fastapi import APIRouter, Depends
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import Pagination, PaginatedResponse
from app.modules.products.dependencies import ProductService, get_product_service
from app.modules.users.dependencies import UserService, get_user_service
from app.modules.products.schemas import (
    ProductFilters,
    ProductPublicResponse,
)
from app.modules.products.docs import ProductPublicDocs

router = APIRouter(
    prefix="/{store_url}",
    tags=["Products"],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "/products",
    response_model=PaginatedResponse[ProductPublicResponse],
    summary=ProductPublicDocs.ListStoreProducts.summary,
    description=ProductPublicDocs.ListStoreProducts.description,
    responses=ProductPublicDocs.ListStoreProducts.responses,
)
async def list_products(
    store_url: str,
    pagination: Pagination = Depends(),
    filters: ProductFilters = Depends(),
    user_service: UserService = Depends(get_user_service),
    product_service: ProductService = Depends(get_product_service),
) -> PaginatedResponse[ProductPublicResponse]:
    user = await user_service.get_by_store_url(store_url)
    total, products = await product_service.get_list(
        user_id=user.id,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[ProductPublicResponse](
        data=products,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/products/{slug}",
    response_model=SingleResponse[ProductPublicResponse],
    summary=ProductPublicDocs.GetStoreProductBySlug.summary,
    description=ProductPublicDocs.GetStoreProductBySlug.description,
    responses=ProductPublicDocs.GetStoreProductBySlug.responses,
)
async def get_product_by_slug(
    store_url: str,
    slug: str,
    user_service: UserService = Depends(get_user_service),
    product_service: ProductService = Depends(get_product_service),
) -> SingleResponse[ProductPublicResponse]:
    user = await user_service.get_by_store_url(store_url)
    product = await product_service.get_by_slug(user.id, slug)
    return SingleResponse[ProductPublicResponse](data=product)
