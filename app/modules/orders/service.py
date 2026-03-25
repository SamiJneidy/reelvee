from beanie import PydanticObjectId

from app.core.context import CurrentUser
from app.core.enums import RecordSource
from app.modules.orders.exceptions import OrderNotFoundException
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderCreate,
    OrderFilters,
    OrderInternal,
    OrderUpdate,
)
from app.modules.orders.schemas.responses import OrderResponse


class OrderService:
    def __init__(self, order_repo: OrderRepository) -> None:
        self._repo = order_repo

    def _to_response(self, order) -> OrderResponse:
        return OrderResponse.model_validate(order)

    def _to_internal(self, order) -> OrderInternal:
        return OrderInternal.model_validate(order)

    # -----------------------------------------------------------------
    # Owner-scoped
    # -----------------------------------------------------------------

    async def get_own_by_id(
        self, current_user: CurrentUser, id: PydanticObjectId
    ) -> OrderResponse:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        return self._to_response(order)

    async def get_own_list(
        self,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 10,
        filters: OrderFilters | None = None,
    ) -> tuple[int, list[OrderResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, orders = await self._repo.get_list(
            user_id=current_user.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [self._to_response(o) for o in orders]

    async def get_unread_count(self, current_user: CurrentUser) -> int:
        return await self._repo.count_unread(current_user.user.id)

    async def create(
        self, current_user: CurrentUser, payload: OrderCreate, session=None
    ) -> OrderResponse:
        data = payload.model_dump()
        data["user_id"] = current_user.user.id
        data["source"] = RecordSource.INTERNAL
        data["is_read"] = True  # owner created it, so it's already seen
        order = await self._repo.create(data, session=session)
        return self._to_response(order)

    async def update_own_by_id(
        self,
        current_user: CurrentUser,
        id: PydanticObjectId,
        payload: OrderUpdate,
        session=None,
    ) -> OrderResponse:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        update_data = payload.model_dump(exclude_none=True)
        if "payment" in update_data:
            update_data["payment"] = payload.payment
        updated = await self._repo.update_by_id(
            current_user.user.id, id, update_data, session=session
        )
        return self._to_response(updated)

    async def delete_own_by_id(
        self, current_user: CurrentUser, id: PydanticObjectId, session=None
    ) -> None:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)

    # -----------------------------------------------------------------
    # Internal — used by other services (e.g. public order submission)
    # -----------------------------------------------------------------

    async def create_from_storefront(
        self,
        user_id: PydanticObjectId,
        customer_id: PydanticObjectId,
        item_id: PydanticObjectId,
        item_price: float | None = None,
        quantity: int | None = None,
        customer_message: str | None = None,
        source: RecordSource = RecordSource.WEB,
        session=None,
    ) -> OrderInternal:
        """Creates an order from a public storefront submission.
        Called by the public order endpoint (to be built).
        """
        data = {
            "user_id": user_id,
            "customer_id": customer_id,
            "item_id": item_id,
            "item_price": item_price,
            "quantity": quantity,
            "customer_message": customer_message,
            "source": source,
            "is_read": False,
        }
        order = await self._repo.create(data, session=session)
        return self._to_internal(order)
