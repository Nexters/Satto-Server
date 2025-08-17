from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.config.schemas import CommonBase
from src.four_pillars.entities.enums import FiveElements


class LottoDraw(CommonBase):
    round: int
    draw_date: date
    num1: int
    num2: int
    num3: int
    num4: int
    num5: int
    num6: int
    bonus_num: int
    first_prize_amount: int
    total_winners: int
    has_recommendation: bool = False


class LottoDrawList(CommonBase):
    draws: List[LottoDraw]
    next_cursor: Optional[int] = None


class LottoStatistic(CommonBase):
    num: int
    count: int


class LottoRecommendationContent(BaseModel):
    reason: str = Field(
        description="사주 기반 로또 추천 이유",
        examples=["화(火) 기운이 강하여, 역동적인 에너지를 가진 열정의 수를 추천해요."],
    )
    num1: int = Field(
        description="추천 번호 1 (기운과 잘 맞는 숫자)", ge=1, le=45, examples=[3]
    )
    num2: int = Field(
        description="추천 번호 2 (기운과 잘 맞는 숫자)", ge=1, le=45, examples=[34]
    )
    num3: int = Field(
        description="추천 번호 3 (재물운 좋을 때 나오는 숫자)",
        ge=1,
        le=45,
        examples=[22],
    )
    num4: int = Field(
        description="추천 번호 4 (재물운 좋을 때 나오는 숫자)",
        ge=1,
        le=45,
        examples=[28],
    )
    num5: int = Field(
        description="추천 번호 5 (최근 자주 나온 번호)", ge=1, le=45, examples=[15]
    )
    num6: int = Field(
        description="추천 번호 6 (최근 자주 나온 번호)", ge=1, le=45, examples=[45]
    )
    cold_nums: List[int] = Field(
        description="기운과 상충하는 숫자 (1-3개)",
        examples=[[4, 8, 16]],
    )
    infrequent_nums: List[int] = Field(
        description="등장 빈도가 낮은 숫자 (1-3개)", examples=[[1, 2]]
    )
    strong_element: FiveElements = Field(description="강한 기운", examples=["화(火)"])
    weak_element: FiveElements = Field(description="상충되는 기운", examples=["목(木)"])

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


class LottoRecommendation(CommonBase):
    user_id: str
    round: int
    content: Optional[LottoRecommendationContent] = None


class LottoRecommendationCreate(CommonBase):
    user_id: str
    round: int
    content: LottoRecommendationContent
