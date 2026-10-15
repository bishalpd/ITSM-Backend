import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category, TicketPriority, TicketType
from schemas.ai import (
    TicketAIRequest,
    TicketAISuggestion,
    TicketAISuggestionRaw,
)

from services.ai.ollama_client import ask_ollama
from services.ai.prompts import build_ticket_prompt


async def analyze_ticket(
    payload: TicketAIRequest,
    db: AsyncSession,
) -> TicketAISuggestion:

    # 1. Fetch available categories
    result = await db.execute(
        select(Category.id, Category.name).order_by(Category.name)
    )

    categories = [{"id": row.id, "name": row.name} for row in result.all()]

    if not categories:
        raise ValueError("No categories configured")

    # 2. Get allowed enum values
    priorities = [item.value for item in TicketPriority]

    ticket_types = [item.value for item in TicketType]

    # 3. Build prompt
    system_prompt = build_ticket_prompt(
        categories=categories,
        priorities=priorities,
        ticket_types=ticket_types,
    )

    user_prompt = json.dumps(
        {
            "title": payload.title,
            "description": payload.description,
        }
    )

    # 4. Call Ollama
    raw_response = await ask_ollama(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # 5. Validate ONLY Ollama's fields
    suggestion = TicketAISuggestionRaw.model_validate_json(raw_response)

    # 6. Resolve category name from PostgreSQL
    category_map = {category["id"]: category["name"] for category in categories}

    category_name = category_map.get(suggestion.category_id)

    if category_name is None:
        raise ValueError(f"Invalid category ID: {suggestion.category_id}")

    # 7. Build final API response
    return TicketAISuggestion(
        **suggestion.model_dump(),
        category_name=category_name,
    )
