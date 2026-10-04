from pydantic import BaseModel, ConfigDict, Field
from models import UserRole

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    name:str
    email:str
    role:UserRole

class UserResponseWithData(BaseModel):
    data:list[UserResponse]
    status: int
    message: str
    success: bool