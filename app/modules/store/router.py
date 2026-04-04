from fastapi import APIRouter, Depends, status

from app.core.context import CurrentUser
from app.core.database import get_session
from app.modules.auth.dependencies import get_request_context
from app.modules.store.dependencies import StoreService, get_store_service
from app.modules.store.schemas import StoreResponse, StoreUpdate
from app.shared.schemas import SingleResponse

router = APIRouter(
    prefix="/store",
    tags=["Store"],
)


@router.get(
    "/me",
    response_model=SingleResponse[StoreResponse],
    summary="Get my store",
)
async def get_my_store(
    current_user: CurrentUser = Depends(get_request_context),
    store_service: StoreService = Depends(get_store_service),
) -> SingleResponse[StoreResponse]:
    data = await store_service.get_by_user_id(current_user.user.id)
    return SingleResponse[StoreResponse](data=data)


@router.get(
    "/{store_url}",
    response_model=SingleResponse[StoreResponse],
    summary="Get my store",
)
async def get_store_info(
    store_url: str,
    store_service: StoreService = Depends(get_store_service),
) -> SingleResponse[StoreResponse]:
    data = await store_service.get_by_store_url(store_url)
    return SingleResponse[StoreResponse](data=data)


@router.put(
    "/me",
    response_model=SingleResponse[StoreResponse],
    summary="Replace my store",
    description=(
        "Full replacement of editable store fields (logo, links, template, config). "
        "Send the complete body each time — not a partial patch."
    ),
)
async def update(
    body: StoreUpdate,
    current_user: CurrentUser = Depends(get_request_context),
    store_service: StoreService = Depends(get_store_service),
    session=Depends(get_session),
) -> SingleResponse[StoreResponse]:
    data = await store_service.update_by_user_id(current_user.user.id, body, session=session)
    return SingleResponse[StoreResponse](data=data)


@router.delete(
    "/me/logo",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete my store logo",
)
async def delete_store_logo(
    current_user: CurrentUser = Depends(get_request_context),
    store_service: StoreService = Depends(get_store_service),
    session=Depends(get_session),
) -> None:
    await store_service.delete_logo(current_user.user.id, session=session)
