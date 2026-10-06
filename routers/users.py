from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db import get_db
from depedencies.auth import get_current_user, require_role
from models import User
from math import ceil
from datetime import datetime, timedelta, timezone
from core.security import hash_password
from schemas.users import (
    UserResponseWithData,
    UserResponse,
    UserResponseWithMessage,
    AdminUserCreate,
)

router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.get("", response_model=UserResponseWithData, status_code=status.HTTP_200_OK)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "agent")),
):
    result = await db.execute(select(User))
    users = result.scalars().all()

    return UserResponseWithData(
        data=[UserResponse.model_validate(user) for user in users],
        status=status.HTTP_200_OK,
        message="Users retrieved successfully",
        success=True,
    )


@router.post(
    "", response_model=UserResponseWithMessage, status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    # check duplicate email
    result = await db.execute(select(User).where(User.email == payload.email))

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponseWithMessage(
        status=status.HTTP_201_CREATED,
        message="User created successfully",
        success=True,
    )
