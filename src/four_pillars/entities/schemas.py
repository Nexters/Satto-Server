from enum import Enum
from typing import Optional, List
from typing_extensions import TypedDict


class FiveElements(str, Enum):
    """오행 (五行)"""
    WOOD = "목(木)"  # 목
    FIRE = "화(火)"  # 화
    EARTH = "토(土)"  # 토
    METAL = "금(金)"  # 금
    WATER = "수(水)"  # 수


class FourPillar(TypedDict, total=False):
    year_pillar: str  # 년주
    month_pillar: str  # 월주
    day_pillar: str  # 일주
    time_pillar: Optional[str]  # 시주
    strong_elements: Optional[List[str]]  # 가장 많은 오행
    weak_elements: Optional[List[str]]  # 가장 적은 오행
