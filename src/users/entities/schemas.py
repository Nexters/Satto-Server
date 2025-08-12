from datetime import datetime
from typing import List, Optional

from src.config.schemas import CommonBase
from src.four_pillars.entities.schemas import FourPillarDetail
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


class UserUpdate(CommonBase):
    name: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None


class UserDetail(CommonBase):
    id: str
    name: str
    birth_date: datetime
    gender: Gender
    four_pillar: Optional[FourPillarDetail] = None


class UserList(CommonBase):
    users: List[UserDetail]
    total: int
