from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import User, UserRole

from schemas.dashboard import (
    DashboardOverviewResponse,
    DashboardOverviewResponseWithData,
    DashboardRecentTicket,
    DashboardRecentTicketWithData,
)

from services.dashboard.dashboard_service import (
    get_dashboard_overview,
    get_recent_tickets,
)
from depedencies.auth import get_current_user, require_role

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/overview",
    response_model=DashboardOverviewResponseWithData,
)
async def dashboard_overview(
    period: Literal["7d", "30d", "90d"] = "7d",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
        )
    ),
):
    days = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }[period]

    return await get_dashboard_overview(
        db=db,
        days=days,
    )


@router.get(
    "/recent-tickets",
    response_model=DashboardRecentTicketWithData,
)
async def dashboard_recent_tickets(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
        )
    ),
):
    return await get_recent_tickets(
        db=db,
        limit=limit,
    )
