import re

from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator, EmailStr

from auth_utils import password_validator
from schemas.role_schemas import RoleResponse


class UserRequest(BaseModel):
    firstname: str
    surname: str
    middle_name: str | None = None
    email: EmailStr
    password: str
    role_id: int

    @field_validator('password')
    @classmethod
    def password_validator(cls, password):
        try:
            password_validator(password)
        except ValueError as err:
            raise HTTPException(detail=str(err), status_code=status.HTTP_400_BAD_REQUEST)
        return password

    class Config:
        from_attributes = True


class UserPatch(BaseModel):
    firstname: str | None = None
    surname: str | None = None
    middle_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None

    @field_validator('password')
    @classmethod
    def password_validator(cls, password):
        if password:
            try:
                password_validator(password)
            except ValueError as err:
                raise HTTPException(detail=str(err), status_code=status.HTTP_400_BAD_REQUEST)
        return password

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    firstname: str
    surname: str
    middle_name: str | None = None
    email: str
    role: RoleResponse
    is_active: bool


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    token: str
