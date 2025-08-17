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

    async def create_lotto_draw(self, lotto_data: dict) -> LottoDraws:
        """로또 추첨 데이터를 생성합니다."""
        lotto_draw = LottoDraws(**lotto_data)
        self.session.add(lotto_draw)
        await self.session.flush()
        await self.session.refresh(lotto_draw)
        return lotto_draw

    async def get_lotto_draw_by_round(self, round: int) -> Optional[LottoDraws]:
        """특정 회차의 로또 추첨 데이터를 조회합니다."""
        query = select(LottoDraws).where(LottoDraws.round == round)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_lotto_statistics(self, lotto_data: dict) -> None:
        """로또 통계 데이터를 업데이트합니다."""
        # 메인 번호들 (1-6번)과 보너스 번호
        main_numbers = [
            lotto_data["num1"], lotto_data["num2"], lotto_data["num3"],
            lotto_data["num4"], lotto_data["num5"], lotto_data["num6"]
        ]
        bonus_number = lotto_data["bonus_num"]
        
        # 당첨된 번호들만 수집 (중복 제거)
        winning_numbers = set(main_numbers + [bonus_number])
        
        # 당첨된 번호들의 통계만 조회
        stats_query = select(LottoStatistics).where(
            LottoStatistics.num.in_(winning_numbers)
        )
        result = await self.session.execute(stats_query)
        existing_stats = {stat.num: stat for stat in result.scalars().all()}
        
        # 각 당첨 번호에 대해 통계 업데이트
        for num in winning_numbers:
            if num in existing_stats:
                stat = existing_stats[num]
            else:
                # 새로운 통계 생성
                stat = LottoStatistics(
                    num=num,
                    main_count=0,
                    bonus_count=0,
                    total_count=0
                )
                self.session.add(stat)
            
            # 카운트 업데이트
            if num in main_numbers:
                stat.main_count += 1
                stat.total_count += 1
            elif num == bonus_number:
                stat.bonus_count += 1
                stat.total_count += 1
            
            # 마지막 출현 정보 업데이트
            stat.last_round = lotto_data["round"]
            stat.last_date = lotto_data["draw_date"]

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
