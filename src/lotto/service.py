from typing import List, Optional

from fastapi import Depends

from src.lotto.entities.enums import SortType
from src.lotto.entities.schemas import LottoDraw, LottoDrawList, LottoStatistic
from src.lotto.repository import LottoRepository


class LottoService:
    def __init__(self, lotto_repository: LottoRepository = Depends()):
        self.repository = lotto_repository

    async def get_lotto_draws(
        self, cursor: Optional[int] = None, limit: int = 10
    ) -> LottoDrawList:
        draws, next_cursor = await self.repository.get_lotto_draws(
            cursor=cursor, limit=limit
        )
        draw_list = [LottoDraw.model_validate(draw) for draw in draws]
        return LottoDrawList(draws=draw_list, next_cursor=next_cursor)

    async def get_lotto_statistics(
        self, sort_type: SortType = SortType.FREQUENCY, include_bonus: bool = True
    ) -> List[LottoStatistic]:
        statistics = await self.repository.get_lotto_statistics(
            sort_type=sort_type, include_bonus=include_bonus
        )

        # include_bonus에 따라 적절한 count 값 설정
        statistic_list = []
        for stat in statistics:
            count = stat.total_count if include_bonus else stat.main_count
            statistic_list.append(LottoStatistic(num=stat.num, count=count))

        return statistic_list
