from pydantic import BaseModel


class BusinessObjectResponse(BaseModel):
    id: int
    name: str
