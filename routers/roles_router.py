from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from models import Role
from schemas.role_schemas import RoleResponse

roles_router = APIRouter()


@roles_router.get("", response_model=list[RoleResponse])
async def get_all_roles(session: AsyncSession = Depends(get_session)):
    roles = (await session.execute(select(Role))).scalars().all()
    return roles
