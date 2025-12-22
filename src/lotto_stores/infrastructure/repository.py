# src/lotto_stores/infrastructure/repository.py
from decimal import Decimal

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.lotto_stores.domain.entities.enums import PrizeType
from src.lotto_stores.domain.entities.models import (
    LottoStore,
    LottoStoreWinning,
)


class LottoStoreRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_store_by_id(self, store_id: str) -> LottoStore | None:
        """판매점 ID로 조회"""
        query = select(LottoStore).where(LottoStore.id == store_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_stores_in_bounds(
        self,
        min_lat: Decimal,
        max_lat: Decimal,
        min_lng: Decimal,
        max_lng: Decimal,
        limit: int = 100,
    ) -> list[LottoStore]:
        """지도 영역 내 판매점 조회"""
        query = (
            select(LottoStore)
            .where(
                LottoStore.latitude.isnot(None),
                LottoStore.longitude.isnot(None),
                LottoStore.latitude >= min_lat,
                LottoStore.latitude <= max_lat,
                LottoStore.longitude >= min_lng,
                LottoStore.longitude <= max_lng,
            )
            .order_by(desc(LottoStore.first_prize_count), LottoStore.id)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_stores(
        self,
        query: str,
        limit: int = 20,
    ) -> list[LottoStore]:
        """판매점 검색 (이름, 주소)"""
        search_pattern = f"%{query}%"

        stmt = (
            select(LottoStore)
            .where(
                or_(
                    LottoStore.name.ilike(search_pattern),
                    LottoStore.road_address.ilike(search_pattern),
                    LottoStore.lot_address.ilike(search_pattern),
                    LottoStore.region1.ilike(search_pattern),
                    LottoStore.region2.ilike(search_pattern),
                    LottoStore.region3.ilike(search_pattern),
                )
            )
            .order_by(desc(LottoStore.first_prize_count), LottoStore.name)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_winning_round(self) -> int | None:
        """가장 최근 당첨 회차 조회"""
        query = (
            select(LottoStoreWinning.round)
            .order_by(desc(LottoStoreWinning.round))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_winnings_by_round(
        self,
        round: int,
    ) -> list[LottoStoreWinning]:
        """특정 회차의 당첨 판매점 조회 (store 정보 포함)"""
        query = (
            select(LottoStoreWinning)
            .options(joinedload(LottoStoreWinning.store))
            .where(LottoStoreWinning.round == round)
            .order_by(LottoStoreWinning.prize_rank, LottoStoreWinning.id)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_ranking(
        self,
        region1: str | None = None,
        cursor: str | None = None,
        limit: int = 20,
    ) -> tuple[list[LottoStore], str | None]:
        """명당 리스트 조회 (1등 당첨 횟수 순)"""
        query = (
            select(LottoStore)
            .where(LottoStore.first_prize_count > 0)
            .order_by(desc(LottoStore.first_prize_count), LottoStore.id)
        )

        if region1:
            query = query.where(LottoStore.region1 == region1)

        if cursor:
            # cursor는 "당첨횟수_id" 형식
            parts = cursor.split("_", 1)
            if len(parts) == 2:
                cursor_count, cursor_id = int(parts[0]), parts[1]
                query = query.where(
                    or_(
                        LottoStore.first_prize_count < cursor_count,
                        (
                            (LottoStore.first_prize_count == cursor_count)
                            & (LottoStore.id > cursor_id)
                        ),
                    )
                )

        query = query.limit(limit)

        result = await self.session.execute(query)
        stores = list(result.scalars().all())

        # 다음 페이지 cursor 생성
        next_cursor = None
        if len(stores) == limit:
            last = stores[-1]
            next_cursor = f"{last.first_prize_count}_{last.id}"

        return stores, next_cursor

    async def create_store(self, store_data: dict) -> LottoStore:
        """판매점 생성"""
        store = LottoStore(**store_data)
        self.session.add(store)
        await self.session.flush()
        await self.session.refresh(store)
        return store

    async def bulk_create_stores(self, stores_data: list[dict]) -> int:
        """판매점 일괄 생성"""
        stores = [LottoStore(**data) for data in stores_data]
        self.session.add_all(stores)
        await self.session.flush()
        return len(stores)

    async def create_store_winning(
        self, winning_data: dict
    ) -> LottoStoreWinning:
        """당첨 이력 생성"""
        winning = LottoStoreWinning(**winning_data)
        self.session.add(winning)
        await self.session.flush()
        await self.session.refresh(winning)
        return winning

    async def update_store_statistics(
        self,
        store_id: str,
        prize_type: str | None = None,
    ) -> None:
        """판매점 1등 당첨 통계 업데이트"""
        store = await self.get_store_by_id(store_id)
        if not store:
            return

        store.first_prize_count = (store.first_prize_count or 0) + 1

        if prize_type:
            if prize_type == PrizeType.AUTO.value:
                store.first_prize_auto = (store.first_prize_auto or 0) + 1
            elif prize_type == PrizeType.MANUAL.value:
                store.first_prize_manual = (store.first_prize_manual or 0) + 1
            elif prize_type == PrizeType.SEMI.value:
                store.first_prize_semi = (store.first_prize_semi or 0) + 1
