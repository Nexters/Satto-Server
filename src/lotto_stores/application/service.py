# src/lotto_stores/application/service.py
from decimal import Decimal
from typing import Optional

from src.lotto_stores.api.schemas import (
    LottoStoreFirstPrize,
    LottoStoreInfo,
    LottoStoreMapResponse,
    LottoStoreMarker,
    LottoStoreRanking,
    LottoStoreRankingResponse,
    LottoStoreSearchResponse,
    LottoStoreSearchResult,
    LottoStoreSecondPrize,
    WeeklyWinnersResponse,
)
from src.lotto_stores.domain.entities.models import (
    LottoStore,
)
from src.lotto_stores.domain.interfaces import ILottoStoreRepository


class LottoStoreService:
    def __init__(self, store_repository: ILottoStoreRepository):
        self.store_repository = store_repository

    def _get_address(self, store: LottoStore) -> str:
        """표시용 주소 반환 (도로명 우선)"""
        return store.road_address or store.lot_address or ""

    async def get_stores_map(
        self,
        min_lat: Decimal,
        max_lat: Decimal,
        min_lng: Decimal,
        max_lng: Decimal,
        limit: int = 100,
    ) -> LottoStoreMapResponse:
        """지도 영역 내 마커 목록 조회"""
        stores = await self.store_repository.get_stores_in_bounds(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            limit=limit,
        )

        markers = [
            LottoStoreMarker(
                id=store.id,
                name=store.name,
                latitude=store.latitude,
                longitude=store.longitude,
            )
            for store in stores
            if store.latitude and store.longitude
        ]

        return LottoStoreMapResponse(markers=markers)

    async def get_store_info(self, store_id: str) -> Optional[LottoStoreInfo]:
        """복권방 상세 정보 조회 (마커 클릭 시)"""
        store = await self.store_repository.get_store_by_id(store_id)
        if not store:
            return None

        return LottoStoreInfo(
            id=store.id,
            name=store.name,
            address=self._get_address(store),
            phone=store.phone,
        )

    async def search_stores(
        self,
        query: str,
        limit: int = 20,
    ) -> LottoStoreSearchResponse:
        """복권방 검색"""
        stores = await self.store_repository.search_stores(
            query=query,
            limit=limit,
        )

        results = [
            LottoStoreSearchResult(
                id=store.id,
                name=store.name,
                address=self._get_address(store),
                latitude=store.latitude,
                longitude=store.longitude,
            )
            for store in stores
        ]

        return LottoStoreSearchResponse(results=results)

    async def get_weekly_winners(
        self,
        round: Optional[int] = None,
    ) -> WeeklyWinnersResponse:
        """이번주 당첨 판매점 조회"""
        # 회차가 없으면 최신 회차 조회
        if round is None:
            round = await self.store_repository.get_latest_winning_round()
            if not round:
                return WeeklyWinnersResponse(
                    round=0,
                    first_prize_stores=[],
                    second_prize_stores=[],
                )

        # 해당 회차의 당첨 판매점 조회
        winnings = await self.store_repository.get_winnings_by_round(round)

        first_stores = []
        second_stores = []

        for winning in winnings:
            store = winning.store
            if not store:
                continue

            address = self._get_address(store)

            if winning.prize_rank == 1:
                first_stores.append(
                    LottoStoreFirstPrize(
                        id=store.id,
                        name=store.name,
                        address=address,
                        latitude=store.latitude,
                        longitude=store.longitude,
                        prize_type=winning.prize_type,
                    )
                )
            elif winning.prize_rank == 2:
                second_stores.append(
                    LottoStoreSecondPrize(
                        id=store.id,
                        name=store.name,
                        address=address,
                        latitude=store.latitude,
                        longitude=store.longitude,
                    )
                )

        return WeeklyWinnersResponse(
            round=round,
            first_prize_stores=first_stores,
            second_prize_stores=second_stores,
        )

    async def get_ranking(
        self,
        region1: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: int = 20,
    ) -> LottoStoreRankingResponse:
        """명당 리스트 조회 (1등 당첨 횟수 순)"""
        stores, next_cursor = await self.store_repository.get_ranking(
            region1=region1,
            cursor=cursor,
            limit=limit,
        )

        ranking_list = [
            LottoStoreRanking(
                id=store.id,
                name=store.name,
                address=self._get_address(store),
                latitude=store.latitude,
                longitude=store.longitude,
                first_prize_count=store.first_prize_count or 0,
                first_prize_auto=store.first_prize_auto or 0,
                first_prize_manual=store.first_prize_manual or 0,
                first_prize_semi=store.first_prize_semi or 0,
            )
            for store in stores
        ]

        return LottoStoreRankingResponse(
            stores=ranking_list,
            next_cursor=next_cursor,
        )
