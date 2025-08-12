# src/fortune/entities/schemas.py
from datetime import date
from typing import List, Optional
from src.config.schemas import CommonBase
from src.fortune.entities.enums import FortuneType


class DailyFortuneResource(CommonBase):
    id: int
    publish_date: date
    fortune_type: FortuneType
    image_url: str
    description: str


class DailyFortuneResourceList(CommonBase):
    items: List[DailyFortuneResource]
    next_cursor: Optional[int] = None


class DailyFortuneResourceCreate(CommonBase):
    publish_date: date
    fortune_type: FortuneType
    image_url: str
    description: str


class DailyFortuneResourceUpdate(CommonBase):
    publish_date: Optional[date] = None
    fortune_type: Optional[FortuneType] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
