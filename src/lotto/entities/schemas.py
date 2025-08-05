from datetime import date
from typing import List, Optional

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
