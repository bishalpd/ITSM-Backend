from pydantic import BaseModel, ConfigDict, EmailStr,Field
from models import UserRole

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserProfileResponse(BaseModel):
    data: UserResponse
    status: int

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.EMPLOYEE