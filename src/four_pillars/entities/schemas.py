from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ========= 테스트 용 요청/응답 모델 ==========
class FourPillarRequest(BaseModel):
    name: str
    gender: str = Field(..., pattern="^[mf]$")  # m 또는 f만 허용
    birth_date: datetime


class FourPillarResponse(BaseModel):
    year_pillar: str
    month_pillar: str
    day_pillar: str
    time_pillar: Optional[str] = None
