from datetime import date
from typing import List, Optional, Tuple

from src.config.schemas import CommonBase
from src.four_pillars.entities.schemas import FourPillarDetail
from src.users.common.utils import TimeUtils
from src.users.entities.enums import Gender


class UserBase(CommonBase):
    name: str
    birth_date: date
    gender: Gender
    is_active: bool = True


class UserCreate(CommonBase):
    id: str
    name: str
    birth_date: date
    birth_time: Optional[Tuple[str, str]] = None  # 시간 범위 (start_time, end_time)
    gender: Gender

    def __init__(self, **data):
        super().__init__(**data)
        if self.birth_time and not TimeUtils.is_valid_time_range(self.birth_time):
            raise ValueError("Invalid birth_time range")


class UserUpdate(CommonBase):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    birth_time: Optional[Tuple[str, str]] = None  # 시간 범위 (start_time, end_time)
    gender: Optional[Gender] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.birth_time and not TimeUtils.is_valid_time_range(self.birth_time):
            raise ValueError("Invalid birth_time range")


class UserDetail(CommonBase):
    id: str
    name: str
    birth_date: date
    birth_time: Optional[Tuple[str, str]] = None
    gender: Gender
    four_pillar: Optional[FourPillarDetail] = None


class UserList(CommonBase):
    users: List[UserDetail]
    total: int
