from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.deps import TransactionalUnitOfWorkDep, UnitOfWorkDep
from src.core.unit_of_work import UnitOfWork
from src.models.item import Item
from src.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


# --- Response schemas ---
class ItemResponse(BaseModel):
    id: str
    name: str
    quantity: int


class ItemListResponse(BaseModel):
    items: list[ItemResponse]


def _item_to_response(item: Item) -> ItemResponse:
    return ItemResponse(id=str(item.id), name=item.name, quantity=item.quantity)


# --- Read-only: UoW with no transaction ---
@router.get("", response_model=ItemListResponse)
async def list_items(uow: UnitOfWorkDep):
    """List all items. Service uses UoW; no session or DB details in service."""
    service = ItemService(uow)
    items = await service.list_items()
    return ItemListResponse(items=[_item_to_response(i) for i in items])


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, uow: UnitOfWorkDep):
    """Get one item by id."""
    service = ItemService(uow)
    item = await service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(item)


# --- Writes: UoW with transaction (commit/abort handled by dependency) ---
@router.post("", response_model=ItemResponse)
async def create_item(
    name: str,
    quantity: int = 0,
    uow: TransactionalUnitOfWorkDep = None,
):
    """Create item. Service only sees UoW; transaction is inside the UoW."""
    service = ItemService(uow)
    try:
        item = await service.create_item(name, quantity=quantity)
        return _item_to_response(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item_quantity(
    item_id: str,
    quantity: int,
    uow: TransactionalUnitOfWorkDep = None,
):
    """Update item quantity. Service only sees UoW."""
    service = ItemService(uow)
    try:
        item = await service.update_quantity(item_id, quantity)
        return _item_to_response(item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
