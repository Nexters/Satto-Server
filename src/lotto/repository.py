from typing import List, Optional, Tuple

from fastapi import Depends
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.dependencies import get_db_session
from src.lotto.entities.enums import SortType
from src.lotto.entities.models import LottoDraws, LottoStatistics


class LottoRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_lotto_draws(
        self, cursor: Optional[int] = None, limit: int = 10
    ) -> Tuple[List[LottoDraws], Optional[int]]:
        query = select(LottoDraws).order_by(desc(LottoDraws.round))
        if cursor:
            query = query.where(LottoDraws.round < cursor)

        query = query.limit(limit)

        result = await self.session.execute(query)
        draws = result.scalars().all()

        next_cursor = draws[-1].round if len(draws) == limit else None
        return draws, next_cursor

    async def get_lotto_statistics(
        self, sort_type: SortType = SortType.FREQUENCY, include_bonus: bool = True
    ) -> List[LottoStatistics]:
        # 정렬 기준 설정
        if include_bonus:
            # 보너스 번호 포함
            if sort_type == SortType.FREQUENCY:
                order_column = desc(LottoStatistics.total_count)
            else:  # NUMBER
                order_column = asc(LottoStatistics.num)
        else:
            # 보너스 번호 미포함
            if sort_type == SortType.FREQUENCY:
                order_column = desc(LottoStatistics.main_count)
            else:  # NUMBER
                order_column = asc(LottoStatistics.num)

        query = select(LottoStatistics).order_by(order_column)
        result = await self.session.execute(query)
        return result.scalars().all()
