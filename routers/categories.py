from fastapi import APIRouter, Depends, HTTPException, status,Response,Query
from sqlalchemy import select,func,or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import get_db
from depedencies.auth import get_current_user
from models import User,Category
from schemas.categories import CategoryCreate,CategoryUpdate,CategoryResponse,CategoryCreateResponse,CategoryDetailResponse,CategoryListResponse,CategoryTreeResponse
from depedencies.auth import require_role


router = APIRouter(
    prefix="/categories",
    tags=["Category"],
)

@router.post("",response_model=CategoryCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data:CategoryCreate,db:AsyncSession = Depends(get_db),current_user:User = Depends(require_role("admin"))):
    result = await db.execute(select(Category).where(func.lower(Category.name) == data.name.strip().lower()))
    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists"
        )
    category = Category(
        name = data.name,
        description = data.description,
        parent_id = data.parent_id
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return CategoryCreateResponse(
        data=category,
        status=201,
        message="Category created successfully",
    )

@router.get("",response_model=CategoryListResponse)
async def get_categories(search:str|None =Query(default=None,max_length=100),is_active:bool|None=Query(default=None),db:AsyncSession = Depends(get_db),current_user:User=Depends(get_current_user)):
    query = select(Category)

    if search:
        search_value = f"%{search.strip()}%"
        query = query.where(
            or_(
                Category.name.ilike(search_value),
                Category.description.ilike(search_value),
            )
        )

    if is_active is not None:
        query = query.where(Category.is_active == is_active)

    query = query.order_by(Category.name.asc())
    result = await db.execute(query)
    categories = result.scalars().all()

    return CategoryListResponse(
        data=list(categories),
        status=200,
        message="Categories retrieved successfully",
    )

@router.get(
    "/tree",
    response_model=CategoryTreeResponse,
)
async def get_category_tree(
    is_active: bool | None = Query(default=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Category)
        .where(Category.parent_id.is_(None))
        .options(
            selectinload(Category.children)
        )
        .order_by(Category.name.asc())
    )

    if is_active is not None:
        query = query.where(
            Category.is_active == is_active
        )

    result = await db.execute(query)
    categories = result.scalars().all()

    return CategoryTreeResponse(
        data=list(categories),
        status=200,
        message="Category tree retrieved successfully",
    )