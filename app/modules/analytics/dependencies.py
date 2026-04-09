from typing import Annotated

from fastapi import Depends

from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.service import AnalyticsService


def get_analytics_repository() -> AnalyticsRepository:
    return AnalyticsRepository()


def get_analytics_service(
    repo: Annotated[AnalyticsRepository, Depends(get_analytics_repository)],
) -> AnalyticsService:
    return AnalyticsService(repo)
