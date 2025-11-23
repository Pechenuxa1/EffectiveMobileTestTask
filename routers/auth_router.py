from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from db import get_session
from auth_utils import hash_password, create_jwt_token, get_current_user, TOKEN_EXPIRE_SECONDS, get_token
from models import User, Role, RoleType
from redis_client import redis_client
from schemas.user_schemas import UserResponse, UserRequest, TokenResponse, UserLoginRequest

auth_router = APIRouter()


@auth_router.post("/sign-up", response_model=TokenResponse)
async def sign_up(user_request: UserRequest, session: AsyncSession = Depends(get_session)):
    exists = (
        await session.execute(
            select(User).where(User.email == user_request.email)
        )
    ).scalars().all()
    if exists:
        raise HTTPException(
            detail="User with such login already exists",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    role = (
        await session.execute(select(Role).where(Role.id == user_request.role_id))
    ).scalars().one()
    if role.name == RoleType.ADMIN:
        raise HTTPException(detail="You cannot choose ADMIN role", status_code=status.HTTP_400_BAD_REQUEST)
    user_request.role_id = role.id

    user_data = user_request.model_dump(exclude={'password'})
    user = User(**user_data, hashed_password=hash_password(user_request.password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    token_data = {"id": user.id}
    token = create_jwt_token(token_data)
    return TokenResponse(token=token)


@auth_router.post("/login", response_model=TokenResponse)
async def login(user_login_request: UserLoginRequest, session: AsyncSession = Depends(get_session)):
    user: User = (
        await session.execute(
            select(User).where(User.email == user_login_request.email)
        )
    ).scalars().one_or_none()
    if not user:
        raise HTTPException(
            detail="No user with such login or password",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not bcrypt.checkpw(
        user_login_request.password.encode('utf-8'),
        user.hashed_password.encode('utf-8')
    ):
        raise HTTPException(
            detail="No user with such login or password",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not user.is_active:
        raise HTTPException(
            detail="Inactive user",
            status_code=status.HTTP_403_FORBIDDEN
        )

    token_data = {"id": user.id}
    token = create_jwt_token(token_data)
    return TokenResponse(token=token)


@auth_router.post("/logout")
async def logout(_=Depends(get_current_user), token: str = Depends(get_token)):
    await redis_client.setex(token, "token", TOKEN_EXPIRE_SECONDS)
