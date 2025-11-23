from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from auth_utils import get_current_user, hash_password, check_access_rights, get_token
from .auth_router import logout
from models import User
from schemas.user_schemas import UserResponse, UserPatch

profiles_router = APIRouter()


@profiles_router.patch("/my", response_model=UserResponse)
async def update_my_profile(
    user_patch: UserPatch,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    _=Depends(check_access_rights),
):
    user_patch_data = user_patch.model_dump(exclude_unset=True, exclude_none=True)

    for key, value in user_patch_data.items():
        if key == "password":
            setattr(user, "hashed_password", hash_password(value))
        else:
            setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user


@profiles_router.delete("/my", response_model=UserResponse)
async def soft_delete_my_profile(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    token: str = Depends(get_token),
    _=Depends(check_access_rights),
):
    user.is_active = False
    await session.commit()
    await session.refresh(user)
    await logout(token=token)
    return user
