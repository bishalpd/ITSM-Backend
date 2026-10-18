from datetime import date, datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_tickets: int
    open: int
    in_progress: int
    pending: int
    resolved: int
    closed: int
    critical: int


class TicketTrend(BaseModel):
    date: date
    created: int
    resolved: int


class StatusDistribution(BaseModel):
    status: str
    count: int


class CategoryDistribution(BaseModel):
    category_id: int | None
    category_name: str
    count: int
    percentage: float


class PriorityDistribution(BaseModel):
    priority: str
    count: int


class AttentionMetrics(BaseModel):
    unassigned: int
    critical_unresolved: int
    pending_over_48_hours: int


class DashboardOverviewResponse(BaseModel):
    summary: DashboardSummary
    trends: list[TicketTrend]
    status_distribution: list[StatusDistribution]
    categories: list[CategoryDistribution]
    priorities: list[PriorityDistribution]
    attention: AttentionMetrics


class DashboardOverviewResponseWithData(BaseModel):
    data: DashboardOverviewResponse
    status: int
    message: str
    success: bool


class DashboardRecentTicket(BaseModel):
    id: int
    ticket_number: str
    title: str
    category_name: str | None
    priority: str
    status: str
    assigned_agent_name: str | None
    created_at: datetime


class DashboardRecentTicketWithData(BaseModel):
    data: list[DashboardRecentTicket]
    status: int
    message: str
    success: bool
