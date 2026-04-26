from fastapi import APIRouter, Depends, status

from app.core.database import get_session
from app.modules.orders.dependencies import OrderService, get_order_service
from app.modules.orders.docs import OrderPublicDocs
from app.modules.orders.schemas import OrderCreatePublic
from app.modules.store.dependencies import StoreService, get_store_service
from app.shared.schemas.responses import SuccessResponse

router = APIRouter(
    prefix="/{store_url}",
    tags=["Orders"],
)


@router.post(
    "/orders",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary=OrderPublicDocs.CreatePublicOrder.summary,
    description=OrderPublicDocs.CreatePublicOrder.description,
    responses=OrderPublicDocs.CreatePublicOrder.responses,
)
async def create_public_order(
    store_url: str,
    body: OrderCreatePublic,
    store_service: StoreService = Depends(get_store_service),
    order_service: OrderService = Depends(get_order_service),
    session=Depends(get_session),
) -> SuccessResponse:
    store = await store_service.get_by_store_url(store_url)
    await order_service.create_public_order(store.user_id, body, session)
    return SuccessResponse(detail="Order submitted successfully")
