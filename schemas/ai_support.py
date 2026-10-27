from typing import Literal

from pydantic import BaseModel, Field

PriorityValue = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

TicketTypeValue = Literal[
    "incident",
    "service_request",
]


class SupportAnalyzeRequest(BaseModel):
    problem: str = Field(
        min_length=10,
        max_length=5000,
    )


# Structure returned by Gemini
class SupportAnalysisRaw(BaseModel):
    issue_summary: str
    possible_cause: str

    troubleshooting_steps: list[str]

    recommend_ticket: bool
    recommendation_reason: str

    title: str
    description: str

    category_id: int | None

    priority: PriorityValue
    ticket_type: TicketTypeValue


# Structure returned to the frontend
class SupportAnalysisResponse(SupportAnalysisRaw):
    category_name: str | None


class SupportAnalysisWithData(BaseModel):
    data: SupportAnalysisResponse
    status: int = 200
    message: str = "Issue analyzed successfully"
    success: bool = True
