from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from models import TicketType, TicketPriority, TicketStatus

from fastapi import Form


class UserShortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class CategoryShortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


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
    model_config = ConfigDict(from_attributes=True)

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
    attachments: list[TicketAttachmentResponse] = Field(default_factory=list)


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

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str | None = Form(None),
        ticket_type: TicketType = Form(TicketType.INCIDENT),
        priority: TicketPriority = Form(TicketPriority.MEDIUM),
        category_id: int = Form(...),
        assigned_agent_id: int | None = Form(None),
    ):
        return cls(
            title=title,
            description=description,
            ticket_type=ticket_type,
            priority=priority,
            category_id=category_id,
            assigned_agent_id=assigned_agent_id,
        )


class TicketAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int
    created_at: datetime


class TicketResponseWithData(BaseModel):
    data: TicketResponse
    status: int
    message: str
    success: bool


class TicketListItem(BaseModel):
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
    requester: UserShortResponse
    assigned_agent: UserShortResponse | None
    category: CategoryShortResponse
    resolution: str | None
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    attachments: list[TicketAttachmentResponse] = Field(default_factory=list)


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
    attachments: list[TicketAttachmentResponse] = Field(default_factory=list)


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
    status: int
    message: str
    success: bool


class TicketAssignData(BaseModel):
    ticket_id: int
    ticket_number: str
    assigned_agent: UserShortResponse


class TicketAssignResponse(BaseModel):
    data: TicketAssignData
    status: int
    message: str
    success: bool


class TicketAssignRequest(BaseModel):
    agent_id: int = Field(gt=0)
