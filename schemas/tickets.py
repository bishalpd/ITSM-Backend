from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from models import TicketType,TicketPriority,TicketStatus

class UserShortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    name:str
    email:str

class CategoryShortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    name:str


class TicketCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    comment: str
    user_id: int
    created_at: datetime

    user: UserShortResponse

class TicketHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    field_name: str
    old_value: str | None
    new_value: str | None
    changed_by_id: int
    created_at: datetime

    changed_by: UserShortResponse

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

class TicketListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    ticket_number:str
    title:str
    description:str|None
    ticket_type: TicketType
    status: TicketStatus
    priority: TicketPriority
    requester_id:int
    assigned_agent_id:int|None
    category_id:int
    requester: UserShortResponse
    assigned_agent: UserShortResponse | None
    category: CategoryShortResponse
    resolution: str | None
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime

class TicketListResponse(BaseModel):
    data: list[TicketListItem]

    total: int
    page: int
    page_size: int
    total_pages: int

    status: int
    message: str
    success: bool

class TicketDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    title: str
    description: str | None

    ticket_type: TicketType
    status: TicketStatus
    priority: TicketPriority

    requester_id: int
    assigned_agent_id: int | None
    category_id: int

    resolution: str | None
    resolved_at: datetime | None
    closed_at: datetime | None

    created_at: datetime
    updated_at: datetime

    requester: UserShortResponse
    assigned_agent: UserShortResponse | None
    category: CategoryShortResponse

    comments: list[TicketCommentResponse] = []
    history: list[TicketHistoryResponse] = []

class TicketDetailResponseWithData(BaseModel):
    data: TicketDetailResponse
    status: int
    message: str
    success: bool

class MyTicketItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    title: str
    description: str | None

    ticket_type: TicketType
    status: TicketStatus
    priority: TicketPriority

    category_id: int
    assigned_agent_id: int | None

    category: CategoryShortResponse
    assigned_agent: UserShortResponse | None

    resolution: str | None
    resolved_at: datetime | None
    closed_at: datetime | None

    created_at: datetime
    updated_at: datetime


class MyTicketListResponse(BaseModel):
    data: list[MyTicketItem]

    total: int
    page: int
    page_size: int
    total_pages: int

    status: int
    message: str
    success: bool

class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    resolution: str | None = Field(
        default=None,
        max_length=2000,
    )

class TicketStatusUpdateResponse(BaseModel):
    status:int
    message:str
    success:bool