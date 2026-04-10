from fastapi import APIRouter, Depends

from beanie import PydanticObjectId

from app.core.context import SessionContext
from app.modules.auth.dependencies import get_current_session
from app.modules.analytics.dependencies import AnalyticsService, get_analytics_service
from app.modules.analytics.schemas import AnalyticsPeriodQuery
from app.modules.analytics.schemas.responses import (
    ItemAnalyticsResponse,
    StoreAnalyticsResponse,
)
from app.shared.schemas.responses import SingleResponse

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/overview",
    response_model=SingleResponse[StoreAnalyticsResponse],
    summary="Get store analytics overview",
    description=(
        "Returns aggregated analytics for the authenticated store owner's store. "
        "Pass ?days=30 for the last N days, or ?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD "
        "for a specific date range. Defaults to the last 30 days."
    ),
)
async def get_store_analytics(
    period: AnalyticsPeriodQuery = Depends(),
    current_user: SessionContext = Depends(get_current_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> SingleResponse[StoreAnalyticsResponse]:
    data = await analytics_service.get_store_analytics(
        user_id=current_user.user.id,
        store_id=current_user.store.id,
        days=period.days,
        from_date=period.from_date,
        to_date=period.to_date,
    )
    return SingleResponse[StoreAnalyticsResponse](data=data)


@router.get(
    "/items/{item_id}",
    response_model=SingleResponse[ItemAnalyticsResponse],
    summary="Get per-item analytics",
    description=(
        "Returns views, orders, revenue, and daily trend for a specific item. "
        "The item must belong to the authenticated store owner."
    ),
)
async def get_item_analytics(
    item_id: PydanticObjectId,
    period: AnalyticsPeriodQuery = Depends(),
    current_user: SessionContext = Depends(get_current_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> SingleResponse[ItemAnalyticsResponse]:
    data = await analytics_service.get_item_analytics(
        user_id=current_user.user.id,
        item_id=item_id,
        store_id=current_user.store.id,
        days=period.days,
        from_date=period.from_date,
        to_date=period.to_date,
    )
    return SingleResponse[ItemAnalyticsResponse](data=data)
