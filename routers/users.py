from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db import get_db
from depedencies.auth import get_current_user, require_role
from models import User
from math import ceil
from datetime import datetime, timedelta, timezone
from schemas.users import UserResponseWithData, UserResponse

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
