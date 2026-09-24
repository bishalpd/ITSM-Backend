from fastapi import APIRouter, Depends, HTTPException, status,Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token,verify_password,hash_password
from db import get_db
from depedencies.auth import get_current_user
from models import User
from schemas.auth import TokenResponse,UserResponse,UserCreate,UserProfileResponse
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register(user_data:UserCreate,db:AsyncSession=Depends(get_db)):
    # check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already exists")
    # hash the password before stoing it
    hashed_password = hash_password(user_data.password)
    new_user = User(name=user_data.name,email=user_data.email,hashed_password=hashed_password,role=user_data.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login",response_model=TokenResponse)
async def login(response:Response, form_data:OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))

    user = result.scalar_one_or_none()

    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if(user is None):
        raise authentication_error

    if not verify_password(form_data.password,user.hashed_password):
        raise authentication_error

    if not user.is_active:
        raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="User account is inactive",  
        )
    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    return TokenResponse(access_token=access_token)

@router.post("/logout")
async def signout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    return {"detail": "Successfully signed out"}

@router.get("/me",response_model=UserProfileResponse)
async def get_my_profile(current_user:User=Depends(get_current_user)):
    return {
        "data": current_user,
        "status": status.HTTP_200_OK,
    }

