from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from beanie.exceptions import RevisionIdWasChanged

from app.core.context import CurrentUser
from app.core.enums import CustomerStatus, RecordSource
from app.modules.customers.exceptions import (
    CustomerAlreadyExistsException,
    CustomerNotFoundException,
)
from app.modules.customers.repository import CustomerRepository
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerCreatePublic,
    CustomerFilters,
    CustomerInternal,
    CustomerUpdate,
    CustomerUpdateInternal,
)
from app.modules.customers.schemas.responses import CustomerResponse


class CustomerService:
    def __init__(self, customer_repo: CustomerRepository) -> None:
        self._repo = customer_repo

    def _to_response(self, customer) -> CustomerResponse:
        return CustomerResponse.model_validate(customer)

    def _to_internal(self, customer) -> CustomerInternal:
        return CustomerInternal.model_validate(customer)

    # -----------------------------------------------------------------
    # Owner-scoped
    # -----------------------------------------------------------------

    async def get_own_by_id(
        self, current_user: CurrentUser, id: PydanticObjectId
    ) -> CustomerResponse:
        customer = await self._repo.get_by_id(current_user.user.id, id)
        if not customer:
            raise CustomerNotFoundException()
        return self._to_response(customer)

    async def get_own_list(
        self,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 10,
        filters: CustomerFilters | None = None,
    ) -> tuple[int, list[CustomerResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, customers = await self._repo.get_list(
            user_id=current_user.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [self._to_response(c) for c in customers]

    async def create(
        self, current_user: CurrentUser, payload: CustomerCreate, session=None
    ) -> CustomerResponse:
        data = payload.model_dump()
        data["user_id"] = current_user.user.id
        data["source"] = RecordSource.INTERNAL
        data["status"] = CustomerStatus.ACTIVE
        try:
            customer = await self._repo.create(data, session=session)
        except (RevisionIdWasChanged, DuplicateKeyError):
            raise CustomerAlreadyExistsException()
        return self._to_response(customer)

    async def update_own_by_id(
        self,
        current_user: CurrentUser,
        id: PydanticObjectId,
        payload: CustomerUpdate,
        session=None,
    ) -> CustomerResponse:
        customer = await self._repo.get_by_id(current_user.user.id, id)
        if not customer:
            raise CustomerNotFoundException()
        update_data = payload.model_dump(exclude_none=True)
        try:
            updated = await self._repo.update_by_id(
                current_user.user.id, id, update_data, session=session
            )
        except (RevisionIdWasChanged, DuplicateKeyError):
            raise CustomerAlreadyExistsException()
        return self._to_response(updated)

    async def delete_own_by_id(
        self, current_user: CurrentUser, id: PydanticObjectId, session=None
    ) -> None:
        customer = await self._repo.get_by_id(current_user.user.id, id)
        if not customer:
            raise CustomerNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)

    # -----------------------------------------------------------------
    # Internal — used by other services (e.g. orders)
    # -----------------------------------------------------------------

    async def create_public_customer(
        self,
        user_id: PydanticObjectId,
        payload: CustomerCreatePublic,
        session=None,
    ) -> CustomerInternal:
        data = payload.model_dump()
        data["user_id"] = user_id
        data["source"] = RecordSource.WEB
        data["status"] = CustomerStatus.ACTIVE
        try:
            customer = await self._repo.create(data, session=session)
        except (RevisionIdWasChanged, DuplicateKeyError):
            raise CustomerAlreadyExistsException()
        return self._to_internal(customer)

    async def get_by_phone(self, user_id: PydanticObjectId, phone: str) -> CustomerInternal | None:
        customer = await self._repo.get_by_phone(user_id, phone)
        if not customer:
            return None
        return self._to_internal(customer)