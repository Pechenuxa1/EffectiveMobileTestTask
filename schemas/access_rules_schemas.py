from pydantic import BaseModel

from schemas.business_object import BusinessObjectResponse
from schemas.role_schemas import RoleResponse


class AccessRuleResponse(BaseModel):
    id: int
    create_permission: bool
    read_permission: bool
    read_all_permission: bool
    update_permission: bool
    update_all_permission: bool
    delete_permission: bool
    delete_all_permission: bool

    role: RoleResponse
    business_object: BusinessObjectResponse

    class Config:
        from_attributes = True


class AccessRuleCreate(BaseModel):
    create_permission: bool
    read_permission: bool
    read_all_permission: bool
    update_permission: bool
    update_all_permission: bool
    delete_permission: bool
    delete_all_permission: bool

    role_id: int
    business_object_id: int

    class Config:
        from_attributes = True


class AccessRulePatch(BaseModel):
    create_permission: bool | None = None
    read_permission: bool | None = None
    read_all_permission: bool | None = None
    update_permission: bool | None = None
    update_all_permission: bool | None = None
    delete_permission: bool | None = None
    delete_all_permission: bool | None = None

    class Config:
        from_attributes = True
