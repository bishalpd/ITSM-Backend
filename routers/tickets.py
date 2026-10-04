from fastapi import APIRouter, Depends, HTTPException, status,Response,Query
from sqlalchemy import select,func,or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import get_db
from depedencies.auth import get_current_user,require_role
from models import User,Category,Ticket,TicketHistory
from schemas.tickets import TicketStatusUpdate,TicketStatusUpdateResponse,MyTicketListResponse,MyTicketItem,TicketResponseWithData,TicketCreate,TicketResponse,TicketListResponse,TicketListItem,TicketDetailResponseWithData,TicketDetailResponse
from uuid import uuid4
from models import TicketType,TicketPriority,TicketStatus
from math import ceil
from datetime import datetime, timedelta, timezone



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

@router.get("/my",response_model=MyTicketListResponse,status_code=status.HTTP_200_OK)
async def get_my_tickets(
     page:int = Query(default = 1,ge=1),
     page_size:int = Query(default=10,ge=1,le=100),
     search:str | None = Query(default = None,max_length = 100),
     ticket_status: TicketStatus | None = Query(default=None),
     category_id: int | None = Query(default=None,ge=1,),
     days: int | None = Query( default=None,ge=1, description="Tickets created within the last N days",),
     db: AsyncSession = Depends(get_db),
     current_user: User = Depends(get_current_user)):
     

     filters = [Ticket.requester_id == current_user.id]

     if search:
          search_value = f"%{search.strip()}%"
          filters.append(
               or_(
                    Ticket.ticket_number.ilike(search_value),
                    Ticket.title.ilike(search_value)
               )
          )
          
     if ticket_status is not None:
          filters.append(Ticket.status == ticket_status)

     if category_id is not None:
          filters.append(
               Ticket.category_id == category_id
          )
     if days is not None:
         from_date = (datetime.now(timezone.utc)- timedelta(days=days))
         filters.append(Ticket.created_at >= from_date)

     count_query = (select(func.count(Ticket.id)).where(*filters))

     count_result = await db.execute(count_query)
     total = count_result.scalar_one()
     offset = (page - 1) * page_size
     query = (
        select(Ticket)
        .options(
            selectinload(Ticket.category),
            selectinload(Ticket.assigned_agent),
        )
        .where(*filters)
        .order_by(Ticket.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
     result = await db.execute(query)
     tickets = result.scalars().all()
     return MyTicketListResponse(
        data=[
            MyTicketItem.model_validate(ticket)
            for ticket in tickets
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(
            ceil(total / page_size)
            if total > 0
            else 0
        ),
        status=status.HTTP_200_OK,
        message="My tickets retrieved successfully",
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

@router.patch("/{ticket_id}/status",response_model=TicketStatusUpdateResponse,status_code=status.HTTP_200_OK)
async def update_ticket_status(ticket_id:int,payload:TicketStatusUpdate,db:AsyncSession=Depends(get_db),current_user:User=Depends(require_role("admin","agent"))):
     result = await db.execute(select(Ticket).where(Ticket.id==ticket_id))
     ticket = result.scalar_one_or_none()

     if ticket is None:
          raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Ticket not found"
          )
     old_status = ticket.status

     #Nothing changed
     if old_status == payload.status:
          raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail=f"Ticket is already {payload.status.value}"
          )

     # Resolution is required when resolving
     if(payload.status == TicketStatus.RESOLVED and not payload.resolution):
          raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolution is required when resolving a ticket",
        )
     now = datetime.now(timezone.utc)

     #updat status
     ticket.status=payload.status

     #Resolved
     if payload.status == TicketStatus.RESOLVED:
          ticket.resolution=payload.resolution
          ticket.resolved_at=now
    #closed
     elif payload.status == TicketStatus.CLOSED:
          ticket.closed_at = now

     elif payload.status in {TicketStatus.OPEN,TicketStatus.IN_PROGRESS,TicketStatus.IN_PROGRESS}:
          ticket.closed_at = None

          if old_status == TicketStatus.RESOLVED:
               ticket.resolved_at = None
               ticket.resolution = None

     history = TicketHistory(
        ticket_id=ticket.id,
        changed_by_id=current_user.id,
        field_name="status",
        old_value=old_status.value,
        new_value=payload.status.value,
     )
     db.add(history)
     await db.commit()
     await db.refresh(ticket)

     return {
        "status": status.HTTP_200_OK,
        "message": "Ticket status updated successfully",
        "success": True,
     }