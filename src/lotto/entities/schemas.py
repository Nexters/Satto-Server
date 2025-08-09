from datetime import date, datetime
from typing import List, Optional

from typing_extensions import TypedDict

from src.config.schemas import CommonBase


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


class LottoDrawList(CommonBase):
    draws: List[LottoDraw]
    next_cursor: Optional[int] = None


class LottoStatistic(CommonBase):
    num: int
    count: int


class LottoRecommendationContent(TypedDict):
    reason: str  # 추천 이유
    num1: int  # 추천 번호 1
    num2: int  # 추천 번호 2
    num3: int  # 추천 번호 3
    num4: int  # 추천 번호 4
    num5: int  # 추천 번호 5
    num6: int  # 추천 번호 6
    cold_nums: List[int]  # 기피해야 할 번호들
    infrequent_nums: List[int]  # 등장 빈도가 낮은 번호들


class LottoRecommendation(CommonBase):
    id: int
    user_id: str
    round: int
    content: LottoRecommendationContent
    created_at: datetime
    updated_at: datetime


class LottoRecommendationCreate(CommonBase):
    user_id: str
    round: int
    content: LottoRecommendationContent
