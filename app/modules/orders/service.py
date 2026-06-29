from typing import Any

import structlog
from beanie import PydanticObjectId

from app.core.audit import service as audit
from app.core.audit.enums import AuditEventType, AuditResourceType
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
from app.modules.orders.schemas.requests import OrderItemInput, OrderItemInputPublic
from app.modules.orders.schemas.responses import OrderResponse
from app.modules.items.service import ItemService
from app.modules.items.exceptions import ItemNotFoundException

logger = structlog.get_logger(__name__)


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

    @staticmethod
    def _calculate_totals(
        items: list[dict],
        discount_amount: float = 0.0,
        shipping_fees: float = 0.0,
        extra_fees: float = 0.0,
    ) -> tuple[float, float, float]:
        """Return (subtotal, total) computed from resolved items and fee adjustments.

        subtotal = sum of each item's subtotal
        total    = subtotal - discount_amount + shipping_fees + extra_fees
        """
        subtotal = round(sum(item["subtotal"] for item in items), 2)
        total_cost = round(sum(item["cost"] * item["quantity"] for item in items), 2)
        total = round(subtotal - discount_amount + shipping_fees + extra_fees, 2)
        return subtotal, total, total_cost

    async def _resolve_items(
        self, 
        user_id: PydanticObjectId, 
        item_inputs: list[OrderItemInput | OrderItemInputPublic], 
        visible_only: bool = True,
    ) -> list[dict[str, Any]]:
        resolved = []
        for item_input in item_inputs:
            db_item = await self._item_service.get_by_id(user_id, item_input.id)
            if visible_only and not db_item.is_visible:
                raise ItemNotFoundException()
            price = item_input.price if isinstance(item_input, OrderItemInput) else db_item.price
            subtotal = item_input.quantity * price
            resolved.append({
                "id": db_item.id,
                "name": db_item.name,
                "quantity": item_input.quantity,
                "price": round(price, 2),
                "cost": round(db_item.cost, 2),
                "subtotal": round(subtotal, 2),
                "type": db_item.type,
                "thumbnail": db_item.thumbnail.model_dump() if db_item.thumbnail else None,
            })
        return resolved

    # -----------------------------------------------------------------
    # Owner-scoped
    # -----------------------------------------------------------------

    async def get_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId
    ) -> OrderResponse:
        order = await self._repo.get_by_id(current_user.user.id, id)
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
        
        data = payload.model_dump(exclude={"items", "customer_id"})
        
        items = await self._resolve_items(current_user.user.id, payload.items, visible_only=False)
        customer = await self._customer_service.get_own_by_id(current_user, payload.customer_id)
        order_number = await self._repo.next_order_number(current_user.user.id, session=session)
        
        subtotal, total, total_cost = self._calculate_totals(
            items,
            data.get("discount_amount", 0.0),
            data.get("shipping_fees", 0.0),
            data.get("extra_fees", 0.0),
        )
        data["items"] = items
        data["subtotal"] = subtotal
        data["total"] = total
        data["total_cost"] = total_cost
        data["customer"] = customer.model_dump()
        data["user_id"] = current_user.user.id
        data["source"] = RecordSource.INTERNAL
        data["is_read"] = True
        data["order_number"] = f"{order_number:06d}"
        order = await self._repo.create(data, session=session)

        await audit.log_event(
            AuditEventType.ORDER_CREATED,
            user_id=current_user.user.id,
            store_id=current_user.store.id,
            resource_type=AuditResourceType.ORDER,
            resource_id=str(order.id),
            details={
                "order_number": order.order_number,
                "source": RecordSource.INTERNAL,
                "customer_id": str(payload.customer_id),
            },
        )
        return self._to_response(order)

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

        update_data = payload.model_dump(exclude_unset=True, exclude={"items"})

        if payload.items is not None:
            items = await self._resolve_items(current_user.user.id, payload.items, visible_only=False)
            update_data["items"] = items

        # Check if pricing fields were changed
        pricing_fields = {"items", "discount_amount", "shipping_fees", "extra_fees"}
        if payload.model_fields_set & pricing_fields:
            items_for_calc = update_data.get("items") or [i.model_dump() for i in order.items]
            subtotal, total, total_cost = self._calculate_totals(
                items_for_calc,
                update_data.get("discount_amount", order.discount_amount or 0.0),
                update_data.get("shipping_fees", order.shipping_fees or 0.0),
                update_data.get("extra_fees", order.extra_fees or 0.0),
            )
            update_data["subtotal"] = subtotal
            update_data["total"] = total
            update_data["total_cost"] = total_cost

        updated = await self._repo.update_by_id(current_user.user.id, id, update_data, session=session)

        await audit.log_event(
            AuditEventType.ORDER_UPDATED,
            user_id=current_user.user.id,
            store_id=current_user.store.id,
            resource_type=AuditResourceType.ORDER,
            resource_id=str(id),
            details={
                "order_number": order.order_number
            },
        )
        return self._to_response(updated)

    async def delete_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId, session=None
    ) -> None:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)

        await audit.log_event(
            AuditEventType.ORDER_DELETED,
            user_id=current_user.user.id,
            store_id=current_user.store.id,
            resource_type=AuditResourceType.ORDER,
            resource_id=str(id),
            details={"order_number": order.order_number},
        )

    async def set_invoice_id(
        self,
        user_id: PydanticObjectId,
        order_id: PydanticObjectId,
        invoice_id: PydanticObjectId | None,
        session=None,
    ) -> None:
        await self._repo.update_by_id(user_id, order_id, {"invoice_id": invoice_id}, session=session)

    # -----------------------------------------------------------------
    # Internal — used by other services (e.g. public order submission)
    # -----------------------------------------------------------------

    async def create_public_order(
        self,
        user_id: PydanticObjectId,
        payload: OrderCreatePublic,
        session=None,
    ) -> None:

        data = payload.model_dump(exclude={"items", "customer"})
        
        items = await self._resolve_items(user_id, payload.items, visible_only=True)
        
        customer = await self._customer_service.get_by_phone(user_id, payload.customer.phone)
        if not customer:
            customer = await self._customer_service.create_public_customer(
                user_id, 
                payload.customer, 
                session=session
            )

        subtotal, total, total_cost = self._calculate_totals(items)
        data["items"] = items
        data["subtotal"] = subtotal
        data["total"] = total
        data["total_cost"] = total_cost
        data["user_id"] = user_id
        data["customer"] = customer.model_dump()
        data["source"] = RecordSource.WEB
        data["status"] = OrderStatus.NEW
        data["is_read"] = False
        order_number = await self._repo.next_order_number(user_id, session=session)
        data["order_number"] = f"{order_number:06d}"
        await self._repo.create(data, session=session)

        await audit.log_event(
            AuditEventType.ORDER_CREATED,
            user_id=user_id,
            resource_type=AuditResourceType.ORDER,
            details={
                "order_number": data["order_number"],
                "source": RecordSource.WEB,
            },
        )
