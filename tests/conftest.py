import os

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from models import Base, User
from main import app
from db import get_db
from core.security import hash_password

load_dotenv()

TEST_PASSWORD = "Test123456"

TEST_DB_URL = os.getenv("TEST_DB_URL")

if not TEST_DB_URL:
    raise RuntimeError("TEST_DB_URL is not configured")

if "itsmdb_test" not in TEST_DB_URL:
    raise RuntimeError("Refusing to run tests against a non-test database")


test_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 1. Create test database tables
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    finally:
        await test_engine.dispose()


# 2. Create database session
@pytest_asyncio.fixture
async def db_session(setup_database):
    async with TestSessionLocal() as session:
        yield session


# 3. Override production database dependency
@pytest_asyncio.fixture
async def override_get_db(setup_database):

    async def _override_get_db():
        async with TestSessionLocal() as session:
            yield session

    previous_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = _override_get_db

    yield

    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override


# 4. Create HTTP client
@pytest_asyncio.fixture
async def client(override_get_db):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client


# 5. Create test user
@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(
        name="Test Employee",
        email="test@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role="employee",
        is_active=True,
    )

    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    return user


# 6. Login and get JWT
@pytest_asyncio.fixture
async def auth_token(client, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200, response.text

    return response.json()["access_token"]


# 7. Generate Authorization header
@pytest_asyncio.fixture
async def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
