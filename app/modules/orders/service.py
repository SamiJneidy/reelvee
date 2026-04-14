from beanie import PydanticObjectId

from app.core.context import SessionContext
from app.core.enums import OrderStatus, RecordSource
from app.modules.customers.service import CustomerService
from app.modules.orders.exceptions import ItemNotBelongToUserException, OrderNotFoundException
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderCreate,
    OrderCreatePublic,
    OrderFilters,
    OrderInternal,
    OrderUpdate,
)
from app.modules.orders.schemas.responses import OrderResponse
from app.modules.items.service import ItemService
from app.modules.items.exceptions import ItemNotFoundException

class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        customer_service: CustomerService,
        item_service: ItemService,
    ) -> None:
        self._repo = order_repo
        self._customer_service = customer_service
        self._item_service = item_service

    # Helper methods
    def _to_response(self, order) -> OrderResponse:
        return OrderResponse.model_validate(order)

    def _to_internal(self, order) -> OrderInternal:
        return OrderInternal.model_validate(order)

    # -----------------------------------------------------------------
    # Owner-scoped
    # -----------------------------------------------------------------

    async def get_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId
    ) -> OrderResponse:
        order = await self._repo.get_by_id_with_relations(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        return self._to_response(order)

    async def get_own_list(
        self,
        current_user: SessionContext,
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

    async def get_unread_count(self, current_user: SessionContext) -> int:
        return await self._repo.count_unread(current_user.user.id)

    async def create(
        self, current_user: SessionContext, payload: OrderCreate, session=None
    ) -> OrderResponse:
        data = payload.model_dump()
        data["user_id"] = current_user.user.id
        data["source"] = RecordSource.INTERNAL
        data["is_read"] = True  # owner created it, so it's already seen
        seq = await self._repo.next_reference_number(current_user.user.id, session=session)
        data["reference_number"] = f"{seq:06d}"
        order = await self._repo.create(data, session=session)
        full = await self._repo.get_by_id_with_relations(
            current_user.user.id, order.id, session=session
        )
        if full is None:
            raise OrderNotFoundException()
        return self._to_response(full)

    async def update_own_by_id(
        self,
        current_user: SessionContext,
        id: PydanticObjectId,
        payload: OrderUpdate,
        session=None,
    ) -> OrderResponse:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        update_data = payload.model_dump(exclude_none=True)
        updated = await self._repo.update_by_id(
            current_user.user.id, id, update_data, session=session
        )
        if updated is None:
            raise OrderNotFoundException()
        return self._to_response(updated)

    async def delete_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId, session=None
    ) -> None:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)

    # -----------------------------------------------------------------
    # Internal — used by other services (e.g. public order submission)
    # -----------------------------------------------------------------

    async def create_public_order(
        self,
        user_id: PydanticObjectId,
        payload: OrderCreatePublic,
        session=None,
    ) -> None:
        item = await self._item_service.get_by_id(user_id, payload.item_id)
        if not item.is_visible:
            raise ItemNotFoundException()

        customer = await self._customer_service.get_by_phone(user_id, payload.customer.phone)
        if not customer:
            customer = await self._customer_service.create_public_customer(
                user_id, 
                payload.customer, 
                session=session
            )
        data = payload.model_dump(exclude={"customer"})
        data["user_id"] = user_id
        data["customer_id"] = customer.id
        data["source"] = RecordSource.WEB
        data["status"] = OrderStatus.NEW
        data["is_read"] = False
        seq = await self._repo.next_reference_number(user_id, session=session)
        data["reference_number"] = f"{seq:06d}"
        await self._repo.create(data, session=session)
