from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from models import TicketType,TicketPriority,TicketStatus

class TicketResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    ticket_number: str
    title: str
    description: str | None

    ticket_type: TicketType
    status: TicketStatus
    priority: TicketPriority

    category_id: int
    requester_id: int
    assigned_agent_id: int | None

    resolution: str | None

    resolved_at: datetime | None
    closed_at: datetime | None

    created_at: datetime
    updated_at: datetime

class TicketCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str | None = None
    ticket_type: TicketType = TicketType.INCIDENT
    priority: TicketPriority = TicketPriority.MEDIUM
    category_id: int
    assigned_agent_id: int | None = None


class TicketResponseWithData(BaseModel):
    data: TicketResponse
    status: int
    message: str
    success: bool