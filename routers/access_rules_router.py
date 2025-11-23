from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from auth_utils import get_current_user, get_role, check_access_rights
from db import get_session
from models import AccessRule, User, Role
from schemas.access_rules_schemas import AccessRuleResponse, AccessRuleCreate, AccessRulePatch


access_rules_router = APIRouter()


@access_rules_router.get("/my", response_model=list[AccessRuleResponse])
async def get_my_access_rules(
    role: Role = Depends(get_role),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    _=Depends(check_access_rights),
):
    access_rules = (
        await session.execute(select(AccessRule).where(AccessRule.role_id == role.id))
    ).scalars().all()
    return access_rules


@access_rules_router.get("", response_model=list[AccessRuleResponse])
async def get_access_rules(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    _=Depends(check_access_rights),
):
    access_rules = (await session.execute(select(AccessRule))).scalars().all()
    return access_rules


@access_rules_router.post("", response_model=AccessRuleResponse)
async def create_access_rule(
    access_rule_create: AccessRuleCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    _=Depends(check_access_rights),
):
    exists = (
        await session.execute(
            select(AccessRule).where(
                and_(
                    AccessRule.role_id == access_rule_create.role_id,
                    AccessRule.business_object_id == access_rule_create.business_object_id
                )
            )
        )
    ).scalars().all()
    if exists:
        raise HTTPException(
            detail=f"Access rule with role_id = {access_rule_create.role_id} and "
                   f"business_object_id = {access_rule_create.business_object_id} already exists",
            status_code=status.HTTP_409_CONFLICT
        )
    access_rule_data = access_rule_create.model_dump()
    new_access_rule = AccessRule(**access_rule_data)
    session.add(new_access_rule)
    await session.commit()
    await session.refresh(new_access_rule)
    return new_access_rule


@access_rules_router.patch("/{id}", response_model=AccessRuleResponse)
async def update_access_rules(
    id: int,
    access_rule_patch: AccessRulePatch,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    _=Depends(check_access_rights),
):
    access_rule = (
        await session.execute(select(AccessRule).where(AccessRule.id == id))
    ).scalars().one_or_none()
    if access_rule is None:
        raise HTTPException(detail=f"No access rule with id = {id}", status_code=status.HTTP_404_NOT_FOUND)

    access_rule_data = access_rule_patch.model_dump(exclude_unset=True)
    for key, value in access_rule_data.items():
        setattr(access_rule, key, value)

    await session.commit()
    await session.refresh(access_rule)
    return access_rule
