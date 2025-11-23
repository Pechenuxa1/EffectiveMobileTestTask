from pydantic import BaseModel

from models import RoleType


class RoleResponse(BaseModel):
    id: int
    name: RoleType

    class Config:
        from_attributes = True
