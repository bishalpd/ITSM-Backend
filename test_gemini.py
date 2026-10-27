import asyncio

from google import genai
from google.genai import types

from core.config import get_settings


async def main():
    settings = get_settings()

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(
            timeout=120_000,
        ),
    )

    try:
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents="Reply with exactly: Gemini is working.",
        )

        print(response.text)

    finally:
        await client.aio.aclose()


if __name__ == "__main__":
    asyncio.run(main())
