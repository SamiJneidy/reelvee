from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.modules.analytics.dependencies import AnalyticsService, get_analytics_service
from app.modules.analytics.schemas import AnalyticsEventCreate
from app.shared.client_metadata import ClientRequestMetadata, get_client_request_metadata
from app.shared.schemas.responses import SuccessResponse

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# @router.post(
#     "/events",
#     response_model=SuccessResponse,
#     status_code=status.HTTP_202_ACCEPTED,
#     summary="Track an analytics event",
#     description=(
#         "Records a store_view or item_view event. "
#         "Processing is fire-and-forget — the response is returned immediately "
#         "and the event is recorded in the background."
#     ),
# )
# async def track_event(
#     body: AnalyticsEventCreate,
#     client: ClientRequestMetadata = Depends(get_client_request_metadata),
#     background_tasks: BackgroundTasks,
#     analytics_service: AnalyticsService = Depends(get_analytics_service),
# ) -> SuccessResponse:
#     background_tasks.add_task(analytics_service.record_event, body, client)
#     return SuccessResponse(detail="Event received")
