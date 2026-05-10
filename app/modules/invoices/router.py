import math

from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.context import SessionContext
from app.core.database import get_session
from app.modules.auth.dependencies import get_current_session
from app.modules.invoices.dependencies import InvoiceService, get_invoice_service
from app.modules.invoices.docs import InvoiceDocs
from app.modules.invoices.schemas import (
    InvoiceCreate,
    InvoiceFilters,
    InvoiceResponse,
)
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import PaginatedResponse, Pagination

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    dependencies=[Depends(get_current_session)],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "",
    response_model=PaginatedResponse[InvoiceResponse],
    summary=InvoiceDocs.ListOwnInvoices.summary,
    description=InvoiceDocs.ListOwnInvoices.description,
    responses=InvoiceDocs.ListOwnInvoices.responses,
)
async def list_invoices(
    pagination: Pagination = Depends(),
    filters: InvoiceFilters = Depends(),
    current_user: SessionContext = Depends(get_current_session),
    invoice_service: InvoiceService = Depends(get_invoice_service),
) -> PaginatedResponse[InvoiceResponse]:
    total, invoices = await invoice_service.get_own_list(
        current_user=current_user,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[InvoiceResponse](
        data=invoices,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


@router.post(
    "/from-order/{order_id}",
    response_model=SingleResponse[InvoiceResponse],
    status_code=status.HTTP_201_CREATED,
    summary=InvoiceDocs.CreateInvoiceFromOrder.summary,
    description=InvoiceDocs.CreateInvoiceFromOrder.description,
    responses=InvoiceDocs.CreateInvoiceFromOrder.responses,
)
async def create_invoice_from_order(
    order_id: PydanticObjectId,
    background_tasks: BackgroundTasks,
    current_user: SessionContext = Depends(get_current_session),
    invoice_service: InvoiceService = Depends(get_invoice_service),
    session=Depends(get_session),
) -> SingleResponse[InvoiceResponse]:
    invoice = await invoice_service.create_from_order(current_user, order_id, session)
    background_tasks.add_task(invoice_service.get_or_generate_pdf_url, current_user, invoice.id)
    return SingleResponse[InvoiceResponse](data=invoice)


@router.get(
    "/{invoice_id}/pdf",
    response_model=SingleResponse[str],
    summary=InvoiceDocs.GetInvoicePdf.summary,
    description=InvoiceDocs.GetInvoicePdf.description,
    responses=InvoiceDocs.GetInvoicePdf.responses,
)
async def get_invoice_pdf(
    invoice_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    invoice_service: InvoiceService = Depends(get_invoice_service),
) -> SingleResponse[str]:
    url = await invoice_service.get_or_generate_pdf_url(current_user, invoice_id)
    return SingleResponse[str](data=url)


@router.get(
    "/{invoice_id}",
    response_model=SingleResponse[InvoiceResponse],
    summary=InvoiceDocs.GetOwnInvoice.summary,
    description=InvoiceDocs.GetOwnInvoice.description,
    responses=InvoiceDocs.GetOwnInvoice.responses,
)
async def get_invoice(
    invoice_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    invoice_service: InvoiceService = Depends(get_invoice_service),
) -> SingleResponse[InvoiceResponse]:
    invoice = await invoice_service.get_own_by_id(current_user, invoice_id)
    return SingleResponse[InvoiceResponse](data=invoice)


# ---------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------
@router.post(
    "",
    response_model=SingleResponse[InvoiceResponse],
    status_code=status.HTTP_201_CREATED,
    summary=InvoiceDocs.CreateInvoice.summary,
    description=InvoiceDocs.CreateInvoice.description,
    responses=InvoiceDocs.CreateInvoice.responses,
)
async def create_invoice(
    body: InvoiceCreate,
    background_tasks: BackgroundTasks,
    current_user: SessionContext = Depends(get_current_session),
    invoice_service: InvoiceService = Depends(get_invoice_service),
    session=Depends(get_session),
) -> SingleResponse[InvoiceResponse]:
    invoice = await invoice_service.create(current_user, body, session)
    background_tasks.add_task(invoice_service.get_or_generate_pdf_url, current_user, invoice.id)
    return SingleResponse[InvoiceResponse](data=invoice)


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
@router.delete(
    "/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=InvoiceDocs.DeleteOwnInvoice.summary,
    description=InvoiceDocs.DeleteOwnInvoice.description,
    responses=InvoiceDocs.DeleteOwnInvoice.responses,
)
async def delete_invoice(
    invoice_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    invoice_service: InvoiceService = Depends(get_invoice_service),
    session=Depends(get_session),
) -> None:
    await invoice_service.delete_own_by_id(current_user, invoice_id, session)
