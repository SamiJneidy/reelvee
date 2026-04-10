import math

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.core.context import SessionContext
from app.core.database import get_session
from app.modules.auth.dependencies import get_current_session
from app.modules.orders.dependencies import OrderService, get_order_service
from app.modules.orders.docs import OrderDocs
from app.modules.orders.schemas import (
    OrderCreate,
    OrderFilters,
    OrderResponse,
    OrderUpdate,
)
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import Pagination, PaginatedResponse
from app.shared.schemas.responses import SuccessResponse

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "",
    response_model=PaginatedResponse[OrderResponse],
    summary=OrderDocs.ListOwnOrders.summary,
    description=OrderDocs.ListOwnOrders.description,
    responses=OrderDocs.ListOwnOrders.responses,
)
async def list_orders(
    pagination: Pagination = Depends(),
    filters: OrderFilters = Depends(),
    current_user: SessionContext = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> PaginatedResponse[OrderResponse]:
    total, orders = await order_service.get_own_list(
        current_user=current_user,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[OrderResponse](
        data=orders,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/unread-count",
    response_model=SingleResponse[int],
    summary=OrderDocs.GetUnreadCount.summary,
    description=OrderDocs.GetUnreadCount.description,
    responses=OrderDocs.GetUnreadCount.responses,
)
async def get_unread_count(
    current_user: SessionContext = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> SingleResponse[int]:
    count = await order_service.get_unread_count(current_user)
    return SingleResponse[int](data=count)


@router.get(
    "/{order_id}",
    response_model=SingleResponse[OrderResponse],
    summary=OrderDocs.GetOwnOrder.summary,
    description=OrderDocs.GetOwnOrder.description,
    responses=OrderDocs.GetOwnOrder.responses,
)
async def get_order(
    order_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> SingleResponse[OrderResponse]:
    order = await order_service.get_own_by_id(current_user, order_id)
    return SingleResponse[OrderResponse](data=order)


# ---------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------
@router.post(
    "",
    response_model=SingleResponse[OrderResponse],
    status_code=status.HTTP_201_CREATED,
    summary=OrderDocs.CreateOrder.summary,
    description=OrderDocs.CreateOrder.description,
    responses=OrderDocs.CreateOrder.responses,
)
async def create_order(
    body: OrderCreate,
    current_user: SessionContext = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
    session=Depends(get_session),
) -> SingleResponse[OrderResponse]:
    order = await order_service.create(current_user, body, session)
    return SingleResponse[OrderResponse](data=order)


# ---------------------------------------------------------------------
# PATCH
# ---------------------------------------------------------------------
@router.patch(
    "/{order_id}",
    response_model=SingleResponse[OrderResponse],
    summary=OrderDocs.UpdateOwnOrder.summary,
    description=OrderDocs.UpdateOwnOrder.description,
    responses=OrderDocs.UpdateOwnOrder.responses,
)
async def update_order(
    order_id: PydanticObjectId,
    body: OrderUpdate,
    current_user: SessionContext = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
    session=Depends(get_session),
) -> SingleResponse[OrderResponse]:
    order = await order_service.update_own_by_id(current_user, order_id, body, session)
    return SingleResponse[OrderResponse](data=order)


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=OrderDocs.DeleteOwnOrder.summary,
    description=OrderDocs.DeleteOwnOrder.description,
    responses=OrderDocs.DeleteOwnOrder.responses,
)
async def delete_order(
    order_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
    session=Depends(get_session),
) -> None:
    await order_service.delete_own_by_id(current_user, order_id, session)
