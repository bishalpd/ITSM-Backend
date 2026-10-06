from pydantic import BaseModel, ConfigDict, Field, EmailStr
from models import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole


class UserResponseWithData(BaseModel):
    data: list[UserResponse]
    status: int
    message: str
    success: bool


class AdminUserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole


class UserResponseWithMessage(BaseModel):
    status: int
    message: str
    success: bool
