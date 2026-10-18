from math import ceil

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Ticket, TicketPriority, TicketStatus

from schemas.tickets import (
    AssignedTicketResponse,
    AssignedTicketsWithData,
    PaginationResponse,
)


async def get_assigned_tickets(
    db: AsyncSession,
    current_user_id: int,
    search: str | None = None,
    priority: TicketPriority | None = None,
    category_id: int | None = None,
    ticket_status: TicketStatus | None = None,
    page: int = 1,
    page_size: int = 10,
) -> AssignedTicketsWithData:

    filters = [Ticket.assigned_agent_id == current_user_id]

    if search and search.strip():
        search_term = f"%{search.strip()}%"

        filters.append(
            or_(
                Ticket.ticket_number.ilike(search_term),
                Ticket.title.ilike(search_term),
                Ticket.description.ilike(search_term),
            )
        )

    if priority is not None:
        filters.append(Ticket.priority == priority)

    if category_id is not None:
        filters.append(Ticket.category_id == category_id)

    if ticket_status is not None:
        filters.append(Ticket.status == ticket_status)

    count_query = select(func.count(Ticket.id)).where(*filters)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size

    query = (
        select(Ticket)
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_agent),
            selectinload(Ticket.category),
            selectinload(Ticket.attachments),
        )
        .where(*filters)
        .order_by(
            Ticket.created_at.desc(),
            Ticket.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    tickets = result.scalars().all()

    ticket_data = [
        AssignedTicketResponse(
            id=ticket.id,
            ticket_number=ticket.ticket_number,
            title=ticket.title,
            description=ticket.description,
            ticket_type=ticket.ticket_type.value,
            status=ticket.status.value,
            priority=ticket.priority.value,
            category_id=ticket.category_id,
            category_name=(ticket.category.name if ticket.category else None),
            requester_id=ticket.requester_id,
            requester_name=ticket.requester.name,
            assigned_agent_id=ticket.assigned_agent_id,
            assigned_agent_name=(
                ticket.assigned_agent.name if ticket.assigned_agent else None
            ),
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            attachments=ticket.attachments,
        )
        for ticket in tickets
    ]

    return AssignedTicketsWithData(
        data=ticket_data,
        pagination=PaginationResponse(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size),
        ),
        status=200,
        message="Assigned tickets fetched successfully",
        success=True,
    )
