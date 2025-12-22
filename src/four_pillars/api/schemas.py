from typing import Optional

from pydantic import field_validator

from src.config.schemas import CommonBase
from src.four_pillars.domain.entities.enums import FiveElements
from src.four_pillars.domain.entities.models import PillarInfo


class FourPillarDetail(CommonBase):
    """사주 상세 정보 (API 응답 스키마)"""

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
