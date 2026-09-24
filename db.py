from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,async_sessionmaker
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

DB_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_async_engine(DB_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise