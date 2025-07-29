from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from src.config.schemas import CommonBase
from src.four_pillars.entities.schemas import FourPillar
from src.users.entities.enums import Gender


class UserBase(CommonBase):
    name: str
    birth_date: datetime
    gender: Gender
    is_active: bool = True


class UserCreate(CommonBase):
    id: str
    name: str
    birth_date: datetime
    gender: Gender


class UserDetail(CommonBase):
    id: str
    name: str
    birth_date: datetime
    gender: Gender
    four_pillar: FourPillar
    is_active: bool


class UserList(CommonBase):
    users: List[UserDetail]
    total: int
