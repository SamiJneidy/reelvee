import math

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.core.context import SessionContext
from app.core.database import get_session
from app.modules.auth.dependencies import get_current_session
from app.modules.customers.dependencies import CustomerService, get_customer_service
from app.modules.customers.docs import CustomerDocs
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerFilters,
    CustomerResponse,
    CustomerUpdate,
)
from app.shared.schemas import SingleResponse
from app.shared.schemas.pagination import Pagination, PaginatedResponse

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "",
    response_model=PaginatedResponse[CustomerResponse],
    summary=CustomerDocs.ListOwnCustomers.summary,
    description=CustomerDocs.ListOwnCustomers.description,
    responses=CustomerDocs.ListOwnCustomers.responses,
)
async def list_customers(
    pagination: Pagination = Depends(),
    filters: CustomerFilters = Depends(),
    current_user: SessionContext = Depends(get_current_session),
    customer_service: CustomerService = Depends(get_customer_service),
) -> PaginatedResponse[CustomerResponse]:
    total, customers = await customer_service.get_own_list(
        current_user=current_user,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
    )
    return PaginatedResponse[CustomerResponse](
        data=customers,
        total_rows=total,
        total_pages=math.ceil(total / pagination.limit),
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/{customer_id}",
    response_model=SingleResponse[CustomerResponse],
    summary=CustomerDocs.GetOwnCustomer.summary,
    description=CustomerDocs.GetOwnCustomer.description,
    responses=CustomerDocs.GetOwnCustomer.responses,
)
async def get_customer(
    customer_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    customer_service: CustomerService = Depends(get_customer_service),
) -> SingleResponse[CustomerResponse]:
    customer = await customer_service.get_own_by_id(current_user, customer_id)
    return SingleResponse[CustomerResponse](data=customer)


# ---------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------
@router.post(
    "",
    response_model=SingleResponse[CustomerResponse],
    status_code=status.HTTP_201_CREATED,
    summary=CustomerDocs.CreateCustomer.summary,
    description=CustomerDocs.CreateCustomer.description,
    responses=CustomerDocs.CreateCustomer.responses,
)
async def create_customer(
    body: CustomerCreate,
    current_user: SessionContext = Depends(get_current_session),
    customer_service: CustomerService = Depends(get_customer_service),
    session=Depends(get_session),
) -> SingleResponse[CustomerResponse]:
    customer = await customer_service.create(current_user, body, session)
    return SingleResponse[CustomerResponse](data=customer)


# ---------------------------------------------------------------------
# PATCH
# ---------------------------------------------------------------------
@router.patch(
    "/{customer_id}",
    response_model=SingleResponse[CustomerResponse],
    summary=CustomerDocs.UpdateOwnCustomer.summary,
    description=CustomerDocs.UpdateOwnCustomer.description,
    responses=CustomerDocs.UpdateOwnCustomer.responses,
)
async def update_customer(
    customer_id: PydanticObjectId,
    body: CustomerUpdate,
    current_user: SessionContext = Depends(get_current_session),
    customer_service: CustomerService = Depends(get_customer_service),
    session=Depends(get_session),
) -> SingleResponse[CustomerResponse]:
    customer = await customer_service.update_own_by_id(
        current_user, customer_id, body, session
    )
    return SingleResponse[CustomerResponse](data=customer)


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=CustomerDocs.DeleteOwnCustomer.summary,
    description=CustomerDocs.DeleteOwnCustomer.description,
    responses=CustomerDocs.DeleteOwnCustomer.responses,
)
async def delete_customer(
    customer_id: PydanticObjectId,
    current_user: SessionContext = Depends(get_current_session),
    customer_service: CustomerService = Depends(get_customer_service),
    session=Depends(get_session),
) -> None:
    await customer_service.delete_own_by_id(current_user, customer_id, session)
