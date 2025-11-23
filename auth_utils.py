import re
from datetime import datetime, timedelta, timezone
import os

import bcrypt
import jwt
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from db import get_session
from models import User, Role, BusinessObject, AccessRule
from redis_client import redis_client

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_SECONDS = int(os.getenv("TOKEN_EXPIRE_SECONDS"))


http_bearer = HTTPBearer()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_jwt_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=TOKEN_EXPIRE_SECONDS)
    data.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def get_token(token: HTTPBearer = Depends(http_bearer)):
    return token.credentials


async def get_payload(token: str = Depends(get_token)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            detail="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except InvalidTokenError:
        raise HTTPException(
            detail="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception:
        raise HTTPException(
            detail="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return payload


async def check_token_in_redis_blacklist(token: str = Depends(get_token)):
    if await redis_client.get(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(get_payload),
    _=Depends(check_token_in_redis_blacklist)
) -> User:
    try:
        user_id: int = int(payload['id'])
        user: User = (
            await session.execute(select(User).where(User.id == user_id))
        ).scalars().one_or_none()
        return user
    except Exception:
        raise HTTPException(
            detail=f"No user from token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


async def get_role(
    user: User = Depends(get_current_user),
) -> Role:
    if user.role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user.role


method_permissions = {
    "POST": ["create_permission", "create_permission"],
    "GET": ["read_permission", "read_all_permission"],
    "DELETE": ["delete_permission", "delete_all_permission"],
    "PUT": ["update_permission", "update_all_permission"],
    "PATCH": ["update_permission", "update_all_permission"],
}


async def check_access_rights(
    request: Request,
    role: Role = Depends(get_role),
    session: AsyncSession = Depends(get_session),
):
    route = request.scope.get('route')
    tags = route.tags if route else []
    if not tags:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    business_object = (
        await session.execute(
            select(BusinessObject).where(BusinessObject.name.in_(tags))
        )
    ).scalars().one_or_none()
    if business_object is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    access_rule = (
        await session.execute(
            select(AccessRule).where(
                and_(
                    AccessRule.role_id == role.id,
                    AccessRule.business_object_id == business_object.id)
                )
        )
    ).scalars().one_or_none()
    if access_rule is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    permissions = method_permissions.get(request.method)
    if not permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    all_permission = permissions[1] if len(permissions) > 1 else None
    own_permission = permissions[0]
    if all_permission and getattr(access_rule, all_permission, False):
        return
    elif "/my" in request.url.path and getattr(access_rule, own_permission, False):
        return
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def password_validator(password):
    errors = []
    if len(password) < 8:
        errors.append("8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("one lowercase letter")
    if not re.search(r'\d', password):
        errors.append("one digit")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?`~]', password):
        errors.append("one special character")
    if errors:
        raise ValueError(f"Password must contains at least {', '.join(errors)}")
