import structlog
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from beanie.exceptions import RevisionIdWasChanged

from app.core.audit import service as audit
from app.core.audit.enums import AuditEventType, AuditResourceType
from app.core.exceptions.exceptions import DuplicateKeyErrorException
from app.modules.categories.exceptions import CategoryAlreadyExistsException, CategoryNotFoundException
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryFilters,
    CategoryInternal,
    CategoryResponse,
    CategoryUpdate,
)

logger = structlog.get_logger(__name__)


class CategoryService:
    def __init__(self, category_repo: CategoryRepository) -> None:
        self._repo = category_repo

    async def get_by_id(self, id: PydanticObjectId, session=None) -> CategoryInternal:
        category = await self._repo.get_by_id(id, session=session)
        if not category:
            raise CategoryNotFoundException()
        return CategoryInternal.model_validate(category)

    async def get_categories(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: CategoryFilters | None = None,
        session=None,
    ) -> tuple[int, list[CategoryResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, categories = await self._repo.get_categories(
            skip=skip,
            limit=limit,
            filters=filter_dict,
            session=session,
        )
        return total, [CategoryResponse.model_validate(category) for category in categories]

    async def create(self, payload: CategoryCreate, session=None) -> CategoryInternal:
        existing = await self._repo.get_by_name(payload.name, session=session)
        if existing:
            raise CategoryAlreadyExistsException()
        data = payload.model_dump()
        try:
            category = await self._repo.create(data, session=session)
        except DuplicateKeyError:
            raise DuplicateKeyErrorException("Category already exists")
        result = CategoryInternal.model_validate(category)
        await audit.log_event(
            AuditEventType.CATEGORY_CREATED,
            resource_type=AuditResourceType.CATEGORY,
            resource_id=str(result.id),
            details={"name": payload.name},
        )
        return result

    async def update_by_id(self, id: PydanticObjectId, payload: CategoryUpdate, session=None) -> CategoryInternal:
        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("name"):
            update_data["name"] = update_data["name"].strip().lower()
            existing = await self._repo.get_by_name(update_data["name"], session=session)
            if existing and existing.id != id:
                raise CategoryAlreadyExistsException()
        try:
            category = await self._repo.update_by_id(id, update_data, session=session)
        except (DuplicateKeyError, RevisionIdWasChanged):
            raise DuplicateKeyErrorException("Category already exists")
        if not category:
            raise CategoryNotFoundException()
        result = CategoryInternal.model_validate(category)
        await audit.log_event(
            AuditEventType.CATEGORY_UPDATED,
            resource_type=AuditResourceType.CATEGORY,
            resource_id=str(id),
            details={"changed_fields": list(payload.model_fields_set)},
        )
        return result

    async def delete_by_id(self, id: PydanticObjectId, session=None) -> None:
        category = await self._repo.get_by_id(id, session=session)
        if not category:
            raise CategoryNotFoundException()
        await self._repo.delete_by_id(id, session=session)
        await audit.log_event(
            AuditEventType.CATEGORY_DELETED,
            resource_type=AuditResourceType.CATEGORY,
            resource_id=str(id),
        )
