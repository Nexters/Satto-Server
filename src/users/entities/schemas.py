from pydantic import BaseModel, EmailStr
from typing import List


class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True


class UserCreateRequest(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
