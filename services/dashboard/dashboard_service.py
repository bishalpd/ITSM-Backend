from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Ticket, TicketHistory, Category, TicketStatus, TicketPriority

from schemas.dashboard import (
    DashboardSummary,
    TicketTrend,
    StatusDistribution,
    CategoryDistribution,
    PriorityDistribution,
    AttentionMetrics,
    DashboardOverviewResponse,
    DashboardRecentTicket,
    DashboardOverviewResponseWithData,
    DashboardRecentTicketWithData,
)


async def get_summary(db: AsyncSession) -> DashboardSummary:
    query = select(
        func.count(Ticket.id).label("total_tickets"),
        func.count(Ticket.id).filter(Ticket.status == TicketStatus.OPEN).label("open"),
        func.count(Ticket.id)
        .filter(Ticket.status == TicketStatus.IN_PROGRESS)
        .label("in_progress"),
        func.count(Ticket.id)
        .filter(Ticket.status == TicketStatus.PENDING)
        .label("pending"),
        func.count(Ticket.id)
        .filter(Ticket.status == TicketStatus.RESOLVED)
        .label("resolved"),
        func.count(Ticket.id)
        .filter(Ticket.status == TicketStatus.CLOSED)
        .label("closed"),
        func.count(Ticket.id)
        .filter(
            Ticket.priority == TicketPriority.CRITICAL,
            Ticket.status.in_(
                [
                    TicketStatus.OPEN,
                    TicketStatus.IN_PROGRESS,
                    TicketStatus.PENDING,
                ]
            ),
        )
        .label("critical"),
    )
    result = await db.execute(query)
    row = result.one()
    return DashboardSummary(**row._mapping)


async def get_status_distribution(db: AsyncSession) -> list[StatusDistribution]:
    result = await db.execute(
        select(Ticket.status, func.count(Ticket.id).label("count")).group_by(
            Ticket.status
        )
    )
    counts = {row.status.value: row.count for row in result.all()}

    return [
        StatusDistribution(status=status.value, count=counts.get(status.value, 0))
        for status in TicketStatus
    ]


async def get_category_distribution(
    db: AsyncSession,
    total_tickets: int,
) -> list[CategoryDistribution]:

    query = (
        select(
            Category.id,
            Category.name,
            func.count(Ticket.id).label("count"),
        )
        .select_from(Ticket)
        .outerjoin(
            Category,
            Ticket.category_id == Category.id,
        )
        .group_by(Category.id, Category.name)
        .order_by(func.count(Ticket.id).desc())
    )

    result = await db.execute(query)

    return [
        CategoryDistribution(
            category_id=row.id,
            category_name=row.name or "Uncategorized",
            count=row.count,
            percentage=(
                round(row.count / total_tickets * 100, 2) if total_tickets else 0
            ),
        )
        for row in result.all()
    ]


async def get_priority_distribution(db: AsyncSession) -> list[PriorityDistribution]:
    result = await db.execute(
        select(Ticket.priority, func.count(Ticket.id).label("count")).group_by(
            Ticket.priority
        )
    )
    counts = {row.priority.value: row.count for row in result.all()}

    return [
        PriorityDistribution(
            priority=priority.value, count=counts.get(priority.value, 0)
        )
        for priority in TicketPriority
    ]


async def get_pending_over_48_hours(
    db: AsyncSession,
) -> int:

    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    latest_pending = (
        select(
            TicketHistory.ticket_id,
            func.max(TicketHistory.created_at).label("pending_since"),
        )
        .where(
            TicketHistory.field_name == "status",
            TicketHistory.new_value == TicketStatus.PENDING.value,
        )
        .group_by(TicketHistory.ticket_id)
        .subquery()
    )

    query = (
        select(func.count(Ticket.id))
        .join(
            latest_pending,
            Ticket.id == latest_pending.c.ticket_id,
        )
        .where(
            Ticket.status == TicketStatus.PENDING,
            latest_pending.c.pending_since < cutoff,
        )
    )

    result = await db.execute(query)

    return result.scalar_one()


async def get_attention_metrics(
    db: AsyncSession,
) -> AttentionMetrics:

    active_statuses = [
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS,
        TicketStatus.PENDING,
    ]

    query = select(
        func.count(Ticket.id)
        .filter(
            Ticket.assigned_agent_id.is_(None),
            Ticket.status.in_(active_statuses),
        )
        .label("unassigned"),
        func.count(Ticket.id)
        .filter(
            Ticket.priority == TicketPriority.CRITICAL,
            Ticket.status.in_(active_statuses),
        )
        .label("critical_unresolved"),
    )

    result = await db.execute(query)
    row = result.one()

    pending_count = await get_pending_over_48_hours(db)

    return AttentionMetrics(
        unassigned=row.unassigned,
        critical_unresolved=row.critical_unresolved,
        pending_over_48_hours=pending_count,
    )


async def get_ticket_trends(db: AsyncSession, days: int = 7) -> list[TicketTrend]:
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=days - 1)

    created_query = (
        select(
            func.date(Ticket.created_at).label("day"),
            func.count(Ticket.id).label("count"),
        )
        .where(
            Ticket.created_at
            >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
        )
        .group_by(func.date(Ticket.created_at))
    )
    resolved_query = (
        select(
            func.date(Ticket.resolved_at).label("day"),
            func.count(Ticket.id).label("count"),
        )
        .where(
            Ticket.resolved_at.is_not(None),
            Ticket.resolved_at
            >= datetime.combine(
                start_date,
                datetime.min.time(),
                tzinfo=timezone.utc,
            ),
        )
        .group_by(func.date(Ticket.resolved_at))
    )
    created_result = await db.execute(created_query)
    resolved_result = await db.execute(resolved_query)

    created_map = {row.day: row.count for row in created_result.all()}
    resolved_map = {row.day: row.count for row in resolved_result.all()}
    return [
        TicketTrend(
            date=start_date + timedelta(days=i),
            created=created_map.get(start_date + timedelta(days=i), 0),
            resolved=resolved_map.get(start_date + timedelta(days=i), 0),
        )
        for i in range(days)
    ]


async def get_dashboard_overview(
    db: AsyncSession,
    days: int = 7,
) -> DashboardOverviewResponseWithData:

    summary = await get_summary(db)

    status_distribution = await get_status_distribution(db)

    categories = await get_category_distribution(
        db,
        total_tickets=summary.total_tickets,
    )

    priorities = await get_priority_distribution(db)

    trends = await get_ticket_trends(
        db,
        days=days,
    )

    attention = await get_attention_metrics(db)

    return DashboardOverviewResponseWithData(
        data=DashboardOverviewResponse(
            summary=summary,
            trends=trends,
            status_distribution=status_distribution,
            categories=categories,
            priorities=priorities,
            attention=attention,
        ),
        status=200,
        message="Dashboard overview fetched successfully",
        success=True,
    )


async def get_recent_tickets(
    db: AsyncSession,
    limit: int = 10,
) -> DashboardRecentTicketWithData:

    query = (
        select(Ticket)
        .options(
            selectinload(Ticket.category),
            selectinload(Ticket.assigned_agent),
        )
        .order_by(
            Ticket.created_at.desc(),
            Ticket.id.desc(),
        )
        .limit(limit)
    )

    result = await db.execute(query)
    tickets = result.scalars().all()
    return DashboardRecentTicketWithData(
        data=[
            DashboardRecentTicket(
                id=ticket.id,
                ticket_number=ticket.ticket_number,
                title=ticket.title,
                category_name=(ticket.category.name if ticket.category else None),
                priority=ticket.priority.value,
                status=ticket.status.value,
                assigned_agent_name=(
                    ticket.assigned_agent.name if ticket.assigned_agent else None
                ),
                created_at=ticket.created_at,
            )
            for ticket in tickets
        ],
        status=200,
        message="Data fetched successfully",
        success=True,
    )
