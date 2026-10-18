from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import auth, categories, tickets, users, ai, dashboard

app = FastAPI(
    title="ServiceDesk API",
    version="1.0.0",
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(
    ai.router,
    prefix="/api/v1",
)
app.include_router(
    dashboard.router,
    prefix="/api/v1",
)
