from fastapi import APIRouter, Depends, HTTPException, status,Response,Query
from sqlalchemy import select,func,or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import get_db
from depedencies.auth import get_current_user
from models import User,Category,Ticket
from depedencies.auth import require_role
from schemas.tickets import TicketResponseWithData,TicketCreate,TicketResponse
from uuid import uuid4
from models import TicketType,TicketPriority,TicketStatus



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