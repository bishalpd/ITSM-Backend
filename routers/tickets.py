from fastapi import APIRouter, Depends, HTTPException, status,Response,Query
from sqlalchemy import select,func,or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import get_db
from depedencies.auth import get_current_user,require_role
from models import User,Category,Ticket
from schemas.tickets import TicketResponseWithData,TicketCreate,TicketResponse,TicketListResponse,TicketListItem,TicketDetailResponseWithData,TicketDetailResponse
from uuid import uuid4
from models import TicketType,TicketPriority,TicketStatus
from math import ceil



router = APIRouter(
    prefix="/tickets",
    tags=["Ticket"],
)

def generate_ticket_number() -> str:
    return f"TKT-{uuid4().hex[:8].upper()}"

@router.post("",response_model=TicketResponseWithData,status_code=status.HTTP_201_CREATED,)
async def create_ticket(payload:TicketCreate,db:AsyncSession = Depends(get_db),current_user:User = Depends(get_current_user)):
    ticket = Ticket(
        ticket_number=generate_ticket_number(),
        title=payload.title,
        description=payload.description,
        ticket_type=payload.ticket_type,
        priority=payload.priority,
        category_id=payload.category_id,
        assigned_agent_id=None,

        # Do NOT accept requester_id from frontend
        requester_id=current_user.id,

        # Backend-controlled initial status
        status=TicketStatus.OPEN,
    )

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return TicketResponseWithData(
        data=TicketResponse.model_validate(ticket),
        status=status.HTTP_201_CREATED,
        message="Ticket created successfully",
        success=True,
    )

@router.get("",response_model=TicketListResponse,status_code=status.HTTP_200_OK,
)
async def get_all_tickets(
        page:int = Query(default=1,ge=1),
        page_size:int = Query(default=10,ge=1,le=100),

        ticket_status:TicketStatus | None = Query(default=None),
        priority: TicketPriority | None = Query(default=None),
        ticket_type: TicketType | None = Query(default=None),
        category_id: int | None = Query(default=None),
        db:AsyncSession=Depends(get_db),
        current_user:User = Depends(require_role("admin","agent"))):

        filters = []

        if ticket_status is not None:
             filters.append(
                  Ticket.status == ticket_status
             )

        if priority is not None:
             filters.append(
                  Ticket.priority == priority
             )

        if ticket_type is not None:
            filters.append(
                Ticket.ticket_type == ticket_type
            )

        if category_id is not None:
            filters.append(
                Ticket.category_id == category_id
            )

        count_query = select(func.count(Ticket.id)).where(*filters)

        total_result = await db.execute(
             count_query
        )

        total = total_result.scalar_one()

        offset = (page-1) * page_size

        query = (
             select(Ticket)
             .options(
                selectinload(Ticket.requester),
                selectinload(Ticket.assigned_agent),
                selectinload(Ticket.category),
             )
             .where(*filters)
             .order_by(Ticket.created_at.desc())
             .offset(offset)
             .limit(page_size)
        )

        result = await db.execute(query)

        tickets = result.scalars().all()

        return TicketListResponse(
            data = [
                TicketListItem.model_validate(ticket)
                for ticket in tickets
             ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size),
            status=status.HTTP_200_OK,
            message="Tickets retrieved successfully",
            success=True,
            )

@router.get("/{ticket_id}",response_model=TicketDetailResponseWithData,status_code=status.HTTP_200_OK)
async def get_ticket_by_id(ticket_id:int,db:AsyncSession=Depends(get_db),current_user:User = Depends(get_current_user)):
     query = (select(Ticket).options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_agent),
            selectinload(Ticket.category),
            selectinload(Ticket.comments),
            selectinload(Ticket.history),
     )
     .where(Ticket.id == ticket_id)
     )

     result = await db.execute(query)

     ticket = result.scalar_one_or_none()

     if ticket is None:
          raise HTTPException(
               status_code = status.HTTP_404_NOT_FOUND,
               detail="Ticket not found"
          )
     return TicketDetailResponseWithData(
          data = TicketDetailResponse.model_validate(ticket),
          status = status.HTTP_200_OK,
          message = "Ticket retrieved successfully",
          success = True,
        )