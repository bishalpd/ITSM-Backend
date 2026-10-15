from pydantic import BaseModel, Field, ConfigDict
from models import TicketPriority, TicketType


class TicketAIRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5)


# Ollama returns this structure
class TicketAISuggestionRaw(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: int
    priority: TicketPriority
    ticket_type: TicketType
    reason: str = Field(max_length=500)


# FastAPI returns this structure to Next.js
class TicketAISuggestion(TicketAISuggestionRaw):
    category_name: str
