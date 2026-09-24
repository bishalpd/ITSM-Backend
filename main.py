from contextlib import asynccontextmanager
from fastapi import FastAPI

from db import engine
from models import Base
from routers import auth
from routers import categories

app = FastAPI(
    title="ServiceDesk API",
    version="1.0.0",
)

app = FastAPI()

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(
    auth.router,
    prefix="/api/v1",
)

app.include_router(
    categories.router,
    prefix="/api/v1"
)