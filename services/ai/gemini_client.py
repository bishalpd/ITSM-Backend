import logging

from google import genai
from google.genai import types

from core.config import get_settings
from schemas.ai_support import SupportAnalysisRaw
from services.ai.gemini_prompts import (
    SYSTEM_INSTRUCTIONS,
    build_support_prompt,
)

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    pass


class GeminiClient:
    def __init__(self):
        settings = get_settings()

        self.model = settings.GEMINI_MODEL
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=60_000),
        )

    async def analyze_problem(
        self, problem: str, categories: list[dict]
    ) -> SupportAnalysisRaw:
        prompt = build_support_prompt(problem=problem, categories=categories)

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS,
                    response_mime_type="application/json",
                    response_schema=SupportAnalysisRaw,
                    temperature=0.2,
                ),
            )
            if not response.text:
                raise GeminiServiceError("Gemini returned an empty response")

            return SupportAnalysisRaw.model_validate_json(response.text)
        except GeminiServiceError:
            raise
        except Exception:
            logger.exception("Gemini analysis failed")
            raise GeminiServiceError("Unable to analyze the issue at this time")


gemini_client = GeminiClient()
