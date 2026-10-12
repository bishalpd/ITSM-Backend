from fastapi import FastAPI

from routers import auth, categories, tickets, users

app = FastAPI(
    title="ServiceDesk API",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
