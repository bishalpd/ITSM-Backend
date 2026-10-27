from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category

from schemas.ai_support import (
    SupportAnalysisResponse,
    SupportAnalysisWithData,
)

from services.ai.gemini_client import gemini_client


async def analyze_employee_issue(
    db: AsyncSession,
    problem: str,
) -> SupportAnalysisWithData:

    # 1. Fetch real categories from PostgreSQL
    result = await db.execute(
        select(
            Category.id,
            Category.name,
        ).order_by(Category.name)
    )

    category_rows = result.all()

    categories = [
        {
            "id": row.id,
            "name": row.name,
        }
        for row in category_rows
    ]

    # 2. Ask Gemini to analyze the issue
    suggestion = await gemini_client.analyze_problem(
        problem=problem,
        categories=categories,
    )

    # 3. Validate the suggested category
    category_map = {category["id"]: category["name"] for category in categories}

    category_id = suggestion.category_id

    if category_id not in category_map:
        category_id = None

    category_name = category_map[category_id] if category_id is not None else None

    # 4. Build validated response
    analysis = SupportAnalysisResponse(
        **{
            **suggestion.model_dump(),
            "category_id": category_id,
            "category_name": category_name,
        }
    )

    return SupportAnalysisWithData(
        data=analysis,
        status=200,
        message="Issue analyzed successfully",
        success=True,
    )
