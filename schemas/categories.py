# app/schemas/category.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )
    description: str | None = None
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    description: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryCreateResponse(BaseModel):
    data:CategoryResponse
    status:int
    message:str

class CategoryListResponse(BaseModel):
    data: list[CategoryResponse]
    status: int
    message: str


class CategoryDetailResponse(BaseModel):
    data: CategoryResponse
    status: int
    message: str


class SubcategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class CategoryWithChildrenResponse(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int | None
    is_active: bool
    children: list[SubcategoryResponse] = []

    model_config = ConfigDict(from_attributes=True)

class CategoryTreeResponse(BaseModel):
    data: list[CategoryWithChildrenResponse]
    status: int
    message: str

class CategoryDetailWithChildrenResponse(BaseModel):
    data: CategoryWithChildrenResponse
    status: int
    message: str