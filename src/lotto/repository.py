from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import Depends
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.dependencies import get_db_session
from src.lotto.entities.enums import SortType
from src.lotto.entities.models import LottoDraws, LottoStatistics, LottoRecommendations


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

    async def get_latest_round(self) -> Optional[int]:
        """가장 최신 로또 회차를 조회합니다."""
        query = select(LottoDraws.round).order_by(desc(LottoDraws.round)).limit(1)
        result = await self.session.execute(query)
        latest = result.scalar_one_or_none()
        return latest

    async def create_lotto_recommendation(
        self, user_id: str, round: int, content: dict
    ) -> LottoRecommendations:
        """로또 추천을 생성합니다."""
        recommendation = LottoRecommendations(
            user_id=user_id,
            round=round,
            content=content,
        )
        self.session.add(recommendation)
        await self.session.flush()
        await self.session.refresh(recommendation)
        return recommendation

    async def get_lotto_recommendation_by_user_id(
        self, user_id: str, start_time: datetime = None, end_time: datetime = None
    ) -> Optional[LottoRecommendations]:
        """사용자의 최신 로또 추천을 조회합니다."""
        query = select(LottoRecommendations).where(
            LottoRecommendations.user_id == user_id
        )

        if start_time and end_time:
            query = query.where(
                LottoRecommendations.created_at >= start_time,
                LottoRecommendations.created_at < end_time,
            )

        query = query.order_by(desc(LottoRecommendations.created_at)).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_frequent_numbers(self, limit: int = 10) -> List[int]:
        """빈도 순으로 가장 많이 나온 번호들을 조회합니다."""
        query = (
            select(LottoStatistics.num)
            .order_by(desc(LottoStatistics.total_count))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]

    async def get_excluded_numbers(self, limit: int = 2) -> List[int]:
        """last_round 기준 오름차순으로 정렬했을 때 가장 마지막 2개 번호를 조회합니다 (최근에 가장 안나온 번호)."""
        query = (
            select(LottoStatistics.num)
            .order_by(asc(LottoStatistics.last_round))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]
