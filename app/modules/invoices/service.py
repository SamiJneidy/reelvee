from beanie import PydanticObjectId

from app.core.context import SessionContext
from app.modules.customers.service import CustomerService
from app.modules.invoices.exceptions import InvoiceNotFoundException
from app.modules.invoices.models import InvoiceCustomer, InvoiceItem
from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.schemas import InvoiceCreate, InvoiceFilters
from app.modules.invoices.schemas.responses import InvoiceResponse
from app.modules.items.service import ItemService


class InvoiceService:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        item_service: ItemService,
        customer_service: CustomerService,
    ) -> None:
        self._repo = invoice_repo
        self._item_service = item_service
        self._customer_service = customer_service

    def _to_response(self, invoice) -> InvoiceResponse:
        return InvoiceResponse.model_validate(invoice)

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
        customer = await self._customer_service.get_own_by_id(current_user, payload.customer_id)
        customer_snapshot = InvoiceCustomer(
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
        )

        item = await self._item_service.get_by_id(current_user.user.id, payload.item_id)
        item_snapshot = InvoiceItem(
            name=item.name,
            quantity=payload.quantity,
        )

        data = payload.model_dump(exclude={"quantity"})
        data["user_id"] = current_user.user.id
        data["customer"] = customer_snapshot.model_dump()
        data["item"] = item_snapshot.model_dump()
        data["invoice_number"] = await self.get_next_invoice_number(current_user.user.id, session)

        invoice = await self._repo.create(data, session=session)
        if invoice is None:
            raise InvoiceNotFoundException()
        return self._to_response(invoice)

    async def delete_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId, session=None
    ) -> None:
        invoice = await self._repo.get_by_id(current_user.user.id, id)
        if not invoice:
            raise InvoiceNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)
