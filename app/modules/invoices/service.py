from beanie import PydanticObjectId

from app.core.context import SessionContext
from app.modules.invoices.exceptions import InvoiceNotFoundException
from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.schemas import (
    InvoiceCreate,
    InvoiceFilters,
)
from app.modules.invoices.schemas.responses import InvoiceResponse


class InvoiceService:
    def __init__(self, invoice_repo: InvoiceRepository) -> None:
        self._repo = invoice_repo

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
        self, current_user: SessionContext, payload: InvoiceCreate, session=None
    ) -> InvoiceResponse:
        data = payload.model_dump()
        data["user_id"] = current_user.user.id
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
