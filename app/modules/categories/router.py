import math

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.core.database import get_session
from app.modules.categories.dependencies import CategoryService, get_category_service
from app.modules.categories.docs import CategoryDocs
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryFilters,
    CategoryResponse,
    CategoryUpdate,
)
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import Pagination, PaginatedResponse
from app.shared.schemas.responses import SuccessResponse


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=PaginatedResponse[CategoryResponse],
    summary=CategoryDocs.ListCategories.summary,
    description=CategoryDocs.ListCategories.description,
)
async def list_categories(
    pagination: Pagination = Depends(),
    filters: CategoryFilters = Depends(),
    category_service: CategoryService = Depends(get_category_service),
) -> PaginatedResponse[CategoryResponse]:
    total, data = await category_service.get_categories(
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[CategoryResponse](
        data=data,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/{category_id}",
    response_model=SingleResponse[CategoryResponse],
    summary=CategoryDocs.GetCategory.summary,
    description=CategoryDocs.GetCategory.description,
    responses=CategoryDocs.GetCategory.responses,
)
async def get_category_by_id(
    category_id: PydanticObjectId,
    category_service: CategoryService = Depends(get_category_service),
) -> SingleResponse[CategoryResponse]:
    data = await category_service.get_by_id(category_id)
    return SingleResponse[CategoryResponse](data=CategoryResponse.model_validate(data))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleResponse[CategoryResponse],
    summary=CategoryDocs.CreateCategory.summary,
    description=CategoryDocs.CreateCategory.description,
    responses=CategoryDocs.CreateCategory.responses,
)
async def create_category(
    body: CategoryCreate,
    session=Depends(get_session),
    category_service: CategoryService = Depends(get_category_service),
) -> SingleResponse[CategoryResponse]:
    data = await category_service.create(body, session=session)
    return SingleResponse[CategoryResponse](data=CategoryResponse.model_validate(data))


@router.patch(
    "/{category_id}",
    response_model=SingleResponse[CategoryResponse],
    summary=CategoryDocs.UpdateCategory.summary,
    description=CategoryDocs.UpdateCategory.description,
    responses=CategoryDocs.UpdateCategory.responses,
)
async def update_category(
    category_id: PydanticObjectId,
    body: CategoryUpdate,
    session=Depends(get_session),
    category_service: CategoryService = Depends(get_category_service),
) -> SingleResponse[CategoryResponse]:
    data = await category_service.update_by_id(category_id, body, session=session)
    return SingleResponse[CategoryResponse](data=CategoryResponse.model_validate(data))


@router.delete(
    "/{category_id}",
    response_model=SuccessResponse,
    summary=CategoryDocs.DeleteCategory.summary,
    description=CategoryDocs.DeleteCategory.description,
    responses=CategoryDocs.DeleteCategory.responses,
)
async def delete_category(
    category_id: PydanticObjectId,
    session=Depends(get_session),
    category_service: CategoryService = Depends(get_category_service),
) -> SuccessResponse:
    await category_service.delete_by_id(category_id, session=session)
    return SuccessResponse(detail="Category deleted successfully")
