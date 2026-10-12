from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from landora_backend.core.database import get_db
from landora_backend.schemas.dashboard import DashboardStatsResponse
from landora_backend.services import dashboard_service


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

DBSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
)
def get_dashboard_stats(db: DBSession):
    return dashboard_service.get_dashboard_stats(db)