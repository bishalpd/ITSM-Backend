import os
from dotenv import load_dotenv
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set in the environment variables.")

if not JWT_ALGORITHM:
    raise RuntimeError("JWT_ALGORITHM is not set in the environment variables.")

if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES is not set in the environment variables."
    )
