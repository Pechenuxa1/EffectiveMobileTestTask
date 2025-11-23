import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session, AsyncSessionLocal
from models import Role, RoleType, User, BusinessObject, AccessRule
from auth_utils import hash_password


async def create_user_access_rules(session: AsyncSession):
    user_role = (await session.execute(select(Role).where(Role.name == RoleType.USER))).scalars().one()
    access_rules_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "access_rules"))).scalars().one()
    profiles_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "profiles"))).scalars().one()
    products_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "products"))).scalars().one()
    seller_access_rules = [
        AccessRule(
            role_id=user_role.id, business_object_id=access_rules_object.id, create_permission=False,
            read_permission=True, read_all_permission=False,
            update_permission=False, update_all_permission=False,
            delete_permission=False, delete_all_permission=False
        ),
        AccessRule(
            role_id=user_role.id, business_object_id=profiles_object.id, create_permission=True,
            read_permission=True, read_all_permission=False,
            update_permission=True, update_all_permission=False,
            delete_permission=True, delete_all_permission=False
        ),
        AccessRule(
            role_id=user_role.id, business_object_id=products_object.id, create_permission=True,
            read_permission=True, read_all_permission=False,
            update_permission=True, update_all_permission=False,
            delete_permission=True, delete_all_permission=False
        ),
    ]
    session.add_all(seller_access_rules)
    await session.flush()


async def create_superuser_access_rules(session: AsyncSession):
    superuser_role = (await session.execute(select(Role).where(Role.name == RoleType.SUPERUSER))).scalars().one()
    access_rules_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "access_rules"))).scalars().one()
    profiles_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "profiles"))).scalars().one()
    products_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "products"))).scalars().one()
    buyer_access_rules = [
        AccessRule(
            role_id=superuser_role.id, business_object_id=access_rules_object.id, create_permission=False,
            read_permission=True, read_all_permission=False,
            update_permission=False, update_all_permission=False,
            delete_permission=False, delete_all_permission=False
        ),
        AccessRule(
            role_id=superuser_role.id, business_object_id=profiles_object.id, create_permission=True,
            read_permission=True, read_all_permission=False,
            update_permission=True, update_all_permission=False,
            delete_permission=True, delete_all_permission=False
        ),
        AccessRule(
            role_id=superuser_role.id, business_object_id=products_object.id, create_permission=True,
            read_permission=True, read_all_permission=True,
            update_permission=True, update_all_permission=True,
            delete_permission=True, delete_all_permission=True
        ),
    ]
    session.add_all(buyer_access_rules)
    await session.flush()


async def create_admin_access_rules(session: AsyncSession):
    admin_role = (await session.execute(select(Role).where(Role.name == RoleType.ADMIN))).scalars().one()
    access_rules_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "access_rules"))).scalars().one()
    profiles_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "profiles"))).scalars().one()
    products_object = (
        await session.execute(select(BusinessObject).where(BusinessObject.name == "products"))).scalars().one()
    business_objects = [access_rules_object, profiles_object, products_object]
    admin_access_rules = []
    for business_object in business_objects:
        admin_access_rules.append(
            AccessRule(
                role_id=admin_role.id, business_object_id=business_object.id, create_permission=True,
                read_permission=True, read_all_permission=True,
                update_permission=True, update_all_permission=True,
                delete_permission=True, delete_all_permission=True
            )
        )
    session.add_all(admin_access_rules)
    await session.flush()


async def create_business_objects(session: AsyncSession):
    business_objects = [
        BusinessObject(name="access_rules"),
        BusinessObject(name="profiles"),
        BusinessObject(name="products"),
        BusinessObject(name="orders"),
    ]
    session.add_all(business_objects)
    await session.flush()


async def create_admin(session: AsyncSession):
    admin_role = (await session.execute(select(Role).where(Role.name == RoleType.ADMIN))).scalars().one()
    user = User(
        firstname="Олег",
        surname="Олегов",
        middle_name="Олегович",
        email="oleg@mail.com",
        hashed_password=hash_password("aBc123-+"),
        role_id=admin_role.id
    )
    session.add(user)
    await session.flush()


async def create_roles(session: AsyncSession):
    roles = [
        Role(name=RoleType.USER),
        Role(name=RoleType.SUPERUSER),
        Role(name=RoleType.ADMIN),
    ]
    session.add_all(roles)
    await session.flush()


async def fill_db_data(session: AsyncSession):
    await create_roles(session)
    await create_admin(session)
    await create_business_objects(session)
    await create_admin_access_rules(session)
    await create_user_access_rules(session)
    await create_superuser_access_rules(session)


async def main():
    session = AsyncSessionLocal()
    try:
        await fill_db_data(session)
        await session.commit()
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
