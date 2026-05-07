from typing import Any

from beanie import PydanticObjectId

from app.core.context import SessionContext
from app.modules.customers.service import CustomerService
from app.modules.invoices.exceptions import (
    InvoiceAlreadyExistsForOrderException,
    InvoiceNotFoundException,
    InvoiceOrderNotCompletedException,
)
from app.modules.invoices.models import InvoiceCustomer
from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.schemas import InvoiceCreate, InvoiceFilters
from app.modules.invoices.schemas.requests import InvoiceItemInput
from app.modules.invoices.schemas.responses import InvoiceResponse
from app.modules.items.service import ItemService
from app.modules.orders.service import OrderService


class InvoiceService:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        order_service: OrderService,
        customer_service: CustomerService,
        item_service: ItemService,
    ) -> None:
        self._repo = invoice_repo
        self._order_service = order_service
        self._customer_service = customer_service
        self._item_service = item_service

    def _to_response(self, invoice) -> InvoiceResponse:
        return InvoiceResponse.model_validate(invoice)

    async def _resolve_items(
        self,
        user_id: PydanticObjectId,
        item_inputs: list[InvoiceItemInput],
    ) -> list[dict[str, Any]]:
        resolved: list[dict[str, Any]] = []
        for item_input in item_inputs:
            db_item = await self._item_service.get_by_id(user_id, item_input.id)
            price = item_input.price
            subtotal = item_input.quantity * price
            resolved.append(
                {
                    "id": db_item.id,
                    "name": db_item.name,
                    "quantity": item_input.quantity,
                    "price": round(price, 2),
                    "subtotal": round(subtotal, 2),
                    "type": db_item.type,
                }
            )
        return resolved

    async def get_next_invoice_number(self, user_id: PydanticObjectId, session) -> str:
        seq = await self._repo.next_invoice_number(user_id, session=session)
        return f"INV-{seq:06d}"

    async def get_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId
    ) -> InvoiceResponse:
        invoice = await self._repo.get_by_id(current_user.user.id, id)
        if not invoice:
            raise InvoiceNotFoundException()
        return self._to_response(invoice)

    async def get_own_list(
        self,
        current_user: SessionContext,
        skip: int = 0,
        limit: int = 10,
        filters: InvoiceFilters | None = None,
    ) -> tuple[int, list[InvoiceResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, invoices = await self._repo.get_list(
            user_id=current_user.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [self._to_response(inv) for inv in invoices]

    async def create(
        self, current_user: SessionContext, payload: InvoiceCreate, session
    ) -> InvoiceResponse:
        customer_resp = await self._customer_service.get_own_by_id(
            current_user, payload.customer_id
        )
        customer_snapshot = InvoiceCustomer(
            id=customer_resp.id,
            name=customer_resp.name,
            email=customer_resp.email,
            phone=customer_resp.phone,
            address=customer_resp.address,
        )

        items = await self._resolve_items(current_user.user.id, payload.items)

        order_id = None
        order_number = None
        if payload.order_id is not None:
            order = await self._order_service.get_own_by_id(
                current_user, payload.order_id
            )
            order_id = order.id
            order_number = order.order_number

        data = payload.model_dump(exclude_none=True, exclude={"customer_id", "items"})
        data["user_id"] = current_user.user.id
        data["order_id"] = order_id
        data["order_number"] = order_number
        data["customer"] = customer_snapshot.model_dump()
        data["items"] = items
        data["invoice_number"] = await self.get_next_invoice_number(current_user.user.id, session)

        invoice = await self._repo.create(data, session=session)
        if invoice is None:
            raise InvoiceNotFoundException()
        return self._to_response(invoice)

    async def create_from_order(
        self,
        current_user: SessionContext,
        order_id: PydanticObjectId,
        session,
    ) -> InvoiceResponse:
        existing = await self._repo.get_by_order_id(
            current_user.user.id, order_id, session=session
        )
        if existing is not None:
            raise InvoiceAlreadyExistsForOrderException()

        order = await self._order_service.get_own_by_id(current_user, order_id)

        if order.total is None:
            raise InvoiceOrderNotCompletedException()

        invoice_create = InvoiceCreate(
            order_id=order.id,
            customer_id=order.customer.id,
            items=[InvoiceItemInput.model_validate(item) for item in order.items],
            subtotal=order.total,
            discount=0,
            total=order.total,
            notes=order.notes,
        )
        return await self.create(current_user, invoice_create, session)

    async def delete_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId, session=None
    ) -> None:
        invoice = await self._repo.get_by_id(current_user.user.id, id)
        if not invoice:
            raise InvoiceNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)
