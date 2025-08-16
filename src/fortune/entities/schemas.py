# src/fortune/entities/schemas.py
from fastapi import Form
from datetime import date
from typing import List, Optional, Dict
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
    # image_url: str
    description: str

    @classmethod
    def as_form(
            cls,
            publish_date: date = Form(..., description="게시일 (YYYY-MM-DD)"),
            fortune_type: FortuneType = Form(..., description="운세 타입"),
            description: str = Form(None, description="설명"),
    ):
        return cls(
            publish_date=publish_date,
            fortune_type=fortune_type,
            description=description,
        )


class DailyFortuneResourceUpdate(CommonBase):
    publish_date: Optional[date] = None
    fortune_type: Optional[FortuneType] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

class UserDailyFortuneSummary(CommonBase):
    id: int
    user_id: str
    fortune_date: date
    fortune_type: FortuneType
    image_url: str
    description: str

class UserDailyFortuneDetail(CommonBase):
    id: int
    user_id: str
    fortune_date: date
    fortune_score: int
    fortune_comment: str
    fortune_details: Dict[str, str]