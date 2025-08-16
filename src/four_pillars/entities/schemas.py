from typing import Optional, List

from pydantic import BaseModel, field_validator
from typing_extensions import TypedDict

from src.config.schemas import CommonBase
from src.four_pillars.entities.enums import FiveElements, TenGods


class PillarInfo(BaseModel):
    stem: str  # 천간 (첫 번째 글자)
    branch: str  # 지지 (두 번째 글자)
    stem_ten_god: TenGods  # 천간의 십신
    branch_ten_god: TenGods  # 지지의 십신


class FourPillar(TypedDict, total=False):
    year_pillar: str  # 년주
    month_pillar: str  # 월주
    day_pillar: str  # 일주
    time_pillar: Optional[str]  # 시주
    strong_elements: Optional[List[str]]  # 가장 많은 오행
    weak_elements: Optional[List[str]]  # 가장 적은 오행


class FourPillarDetail(CommonBase):
    strong_element: FiveElements  # 가장 많은 오행
    weak_element: FiveElements  # 가장 적은 오행
    description: str  # 종합 설명

    year_pillar_detail: Optional[PillarInfo]  # 년주 상세
    month_pillar_detail: Optional[PillarInfo]  # 월주 상세
    day_pillar_detail: Optional[PillarInfo]  # 일주 상세
    time_pillar_detail: Optional[PillarInfo]  # 시주 상세

    @field_validator("strong_element", "weak_element", mode="before")
    @classmethod
    def normalize_element(cls, v):
        """오행 문자열을 FiveElements enum으로 정규화"""
        if isinstance(v, str):
            # 기존 형식: "화(火)", "목(木)" 등을 처리
            element_mapping = {
                "화(火)": FiveElements.FIRE,
                "목(木)": FiveElements.WOOD,
                "토(土)": FiveElements.EARTH,
                "금(金)": FiveElements.METAL,
                "수(水)": FiveElements.WATER,
            }

            normalized = element_mapping.get(v)
            if normalized is not None:
                return normalized

        return v
