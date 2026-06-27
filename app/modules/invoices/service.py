import secrets

import structlog
from beanie import PydanticObjectId

from app.core.audit import service as audit
from app.core.audit.enums import AuditEventType, AuditResourceType
from app.core.context import SessionContext
from app.core.enums import OrderStatus, PermanentFileUploadPath
from app.modules.invoices.exceptions import (
    InvoiceNotFoundException,
    InvoiceOrderNotCompletedException,
)
from app.modules.invoices.models import InvoiceCustomer
from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.schemas import InvoiceCreate, InvoiceFilters
from app.modules.invoices.schemas.responses import InvoiceResponse
from app.modules.orders.service import OrderService
from app.shared.pdf.service import PDFService

logger = structlog.get_logger(__name__)


class InvoiceService:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        order_service: OrderService,
        pdf_service: PDFService,
    ) -> None:
        self._repo = invoice_repo
        self._order_service = order_service
        self._pdf_service = pdf_service

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

    async def create_from_order(
        self,
        current_user: SessionContext,
        order_id: PydanticObjectId,
        generate_pdf: bool = False,
        session=None,
    ) -> InvoiceResponse:
        order = await self._order_service.get_own_by_id(current_user, order_id)

        if order.status != OrderStatus.COMPLETED:
            raise InvoiceOrderNotCompletedException()

        existing = await self._repo.get_by_order_id(
            current_user.user.id, order_id, session=session
        )

        # No need to sync invoice fields with order, invoice holds minimal data that is not affected by order updates.
        if existing:
            return self._to_response(existing)

        invoice_create = InvoiceCreate(
            order_id=order.id,
            order_number=order.order_number,
            customer=InvoiceCustomer(
                id=order.customer.id,
                name=order.customer.name,
                email=order.customer.email,
                phone=order.customer.phone,
                address=order.customer.address,
            ),
        )
        data = invoice_create.model_dump()
        data["user_id"] = current_user.user.id
        data["invoice_number"] = await self.get_next_invoice_number(current_user.user.id, session)
        data["invoice_hash"] = secrets.token_hex(8)
        
        invoice = await self._repo.create(data, session=session)
        await self._order_service.set_invoice_id(
            current_user.user.id, order.id, invoice.id, session=session
        )

        await audit.log_event(
            AuditEventType.INVOICE_CREATED,
            user_id=current_user.user.id,
            store_id=current_user.store.id,
            resource_type=AuditResourceType.INVOICE,
            resource_id=str(invoice.id),
            details={
                "invoice_number": invoice.invoice_number,
                "order_id": str(order.id),
            },
        )

        if generate_pdf:
            await self.get_or_generate_pdf_url(current_user, invoice.id, session=session)
            invoice = await self._repo.get_by_id(current_user.user.id, invoice.id, session=session)
            
        return self._to_response(invoice)

    async def get_or_generate_pdf_url(
        self,
        current_user: SessionContext,
        invoice_id: PydanticObjectId,
        force_generate: bool = False,
        session=None,
    ) -> str:
        invoice = await self._repo.get_by_id(current_user.user.id, invoice_id, session=session)
        if not invoice:
            raise InvoiceNotFoundException()

        if not force_generate and invoice.pdf_url is not None:
            return invoice.pdf_url

        order = await self._order_service.get_own_by_id(current_user, invoice.order_id)
        context = {
            "invoice": invoice,
            "order": order,
            "store": current_user.store,
            "user": current_user.user,
        }
        pdf_filename = f"invoice-{invoice.invoice_number}-{invoice.invoice_hash}.pdf"
        pdf_key = f"{PermanentFileUploadPath.INVOICE_PDF.value}/{pdf_filename}"
        file = await self._pdf_service.render_and_upload(
            template_name="invoice.html",
            filename=pdf_filename,
            context=context,
            path=PermanentFileUploadPath.INVOICE_PDF.value,
            key=pdf_key,
        )
        await self._repo.update_by_id(
            current_user.user.id, invoice_id, {"pdf_url": file.url, "pdf_key": file.key}, session=session
        )

        await audit.log_event(
            AuditEventType.INVOICE_PDF_GENERATED,
            user_id=current_user.user.id,
            store_id=current_user.store.id,
            resource_type=AuditResourceType.INVOICE,
            resource_id=str(invoice_id),
            details={"invoice_number": invoice.invoice_number},
        )
        return file.url
