from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
import httpx
import logging

from db import get_db
from schemas.ai import TicketAIRequest, TicketAISuggestion
from schemas.ai_support import (
    SupportAnalyzeRequest,
    SupportAnalysisWithData,
)
from services.ai.gemini_client import GeminiServiceError

from services.ai.support_service import (
    analyze_employee_issue,
)
from services.ai.ticket_ai import analyze_ticket
from depedencies.auth import get_current_user
from models import User

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/analyze-ticket",
    response_model=TicketAISuggestion,
)
async def analyze_ticket_endpoint(
    payload: TicketAIRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await analyze_ticket(payload, db)

    except httpx.TimeoutException:
        logger.exception("Ollama request timed out")

        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out",
        )

    except httpx.HTTPError:
        logger.exception("Ollama connection or HTTP error")

        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable",
        )

    except ValidationError:
        logger.exception("Invalid AI response schema")

        raise HTTPException(
            status_code=502,
            detail="AI returned an invalid response",
        )

    except ValueError:
        logger.exception("AI classification validation failed")

        raise HTTPException(
            status_code=422,
            detail="AI returned an invalid classification",
        )


@router.post(
    "/create-analyzed-ticket",
    response_model=SupportAnalysisWithData,
    status_code=200,
)
async def analyze_support_issue(
    payload: SupportAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await analyze_employee_issue(
            db=db,
            problem=payload.problem,
        )

    except GeminiServiceError:
        raise HTTPException(
            status_code=503,
            detail="AI support is temporarily unavailable. "
            "You can still create a ticket manually.",
        )
