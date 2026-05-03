from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.enums import AnalyticsEventType
from app.modules.analytics.dependencies import AnalyticsService, get_analytics_service
from app.modules.analytics.schemas import AnalyticsEventCreate
from app.modules.store.dependencies import StoreService,get_store_service
from app.modules.items.dependencies import ItemService, get_item_service
from app.shared.ip.dependencies import get_ip_metadata
from app.shared.ip.schemas import IPMetadata
from app.shared.schemas.responses import SuccessResponse

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.post(
    "/events",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Track an analytics event",
    description=(
        "Records a store_view or item_view event. "
        "Processing is fire-and-forget — the response is returned immediately "
        "and the event is recorded in the background."
    ),
)
async def track_event(
    body: AnalyticsEventCreate,
    background_tasks: BackgroundTasks,
    client: IPMetadata = Depends(get_ip_metadata),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    store_service: StoreService = Depends(get_store_service),
    item_service: ItemService = Depends(get_item_service),
) -> SuccessResponse:
    store = await store_service.get_by_store_url(body.store_url)

    if body.event_type == AnalyticsEventType.item_view:
        # check if item belongs to user
        item = await item_service.get_by_id(store.user_id, body.item_id)
    
    background_tasks.add_task(analytics_service.record_event, store.id, body, client)
    return SuccessResponse(detail="Event received")
