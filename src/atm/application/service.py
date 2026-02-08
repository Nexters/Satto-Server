# src/atm/application/service.py
from decimal import Decimal
from typing import Optional

from src.atm.api.schemas import (
    AtmFirstPrize,
    AtmInfo,
    AtmMapResponse,
    AtmMarker,
    AtmRanking,
    AtmRankingResponse,
    AtmSearchResponse,
    AtmSearchResult,
    AtmSecondPrize,
    WeeklyWinnersResponse,
)
from src.atm.domain.entities.models import (
    Atm,
)
from src.atm.domain.interfaces import IAtmRepository


class AtmService:
    def __init__(self, atm_repository: IAtmRepository):
        self.atm_repository = atm_repository

    def _get_address(self, atm: Atm) -> str:
        """표시용 주소 반환 (도로명 우선)"""
        return atm.road_address or atm.lot_address or ""

    async def get_atms_map(
        self,
        min_lat: Decimal,
        max_lat: Decimal,
        min_lng: Decimal,
        max_lng: Decimal,
        limit: int = 100,
    ) -> AtmMapResponse:
        """지도 영역 내 마커 목록 조회"""
        atms = await self.atm_repository.get_atms_in_bounds(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            limit=limit,
        )

        markers = [
            AtmMarker(
                id=atm.id,
                name=atm.name,
                latitude=atm.latitude,
                longitude=atm.longitude,
            )
            for atm in atms
            if atm.latitude and atm.longitude
        ]

        return AtmMapResponse(markers=markers)

    async def get_atm_info(self, atm_id: str) -> Optional[AtmInfo]:
        """ATM 상세 정보 조회 (마커 클릭 시)"""
        atm = await self.atm_repository.get_atm_by_id(atm_id)
        if not atm:
            return None

        return AtmInfo(
            id=atm.id,
            name=atm.name,
            address=self._get_address(atm),
            phone=atm.phone,
        )

    async def search_atms(
        self,
        query: str,
        limit: int = 20,
    ) -> AtmSearchResponse:
        """ATM 검색"""
        atms = await self.atm_repository.search_atms(
            query=query,
            limit=limit,
        )

        results = [
            AtmSearchResult(
                id=atm.id,
                name=atm.name,
                address=self._get_address(atm),
                latitude=atm.latitude,
                longitude=atm.longitude,
            )
            for atm in atms
        ]

        return AtmSearchResponse(results=results)

    async def get_weekly_winners(
        self,
        round: Optional[int] = None,
    ) -> WeeklyWinnersResponse:
        """이번주 당첨 ATM 조회"""
        # 회차가 없으면 최신 회차 조회
        if round is None:
            round = await self.atm_repository.get_latest_winning_round()
            if not round:
                return WeeklyWinnersResponse(
                    round=0,
                    first_prize_atms=[],
                    second_prize_atms=[],
                )

        # 해당 회차의 당첨 ATM 조회
        winnings = await self.atm_repository.get_winnings_by_round(round)

        first_atms = []
        second_atms = []

        for winning in winnings:
            atm = winning.atm
            if not atm:
                continue

            address = self._get_address(atm)

            if winning.prize_rank == 1:
                first_atms.append(
                    AtmFirstPrize(
                        id=atm.id,
                        name=atm.name,
                        address=address,
                        latitude=atm.latitude,
                        longitude=atm.longitude,
                        prize_type=winning.prize_type,
                    )
                )
            elif winning.prize_rank == 2:
                second_atms.append(
                    AtmSecondPrize(
                        id=atm.id,
                        name=atm.name,
                        address=address,
                        latitude=atm.latitude,
                        longitude=atm.longitude,
                    )
                )

        return WeeklyWinnersResponse(
            round=round,
            first_prize_atms=first_atms,
            second_prize_atms=second_atms,
        )

    async def get_ranking(
        self,
        region1: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: int = 20,
    ) -> AtmRankingResponse:
        """명당 리스트 조회 (1등 당첨 횟수 순)"""
        atms, next_cursor = await self.atm_repository.get_ranking(
            region1=region1,
            cursor=cursor,
            limit=limit,
        )

        ranking_list = [
            AtmRanking(
                id=atm.id,
                name=atm.name,
                address=self._get_address(atm),
                latitude=atm.latitude,
                longitude=atm.longitude,
                first_prize_count=atm.first_prize_count or 0,
                first_prize_auto=atm.first_prize_auto or 0,
                first_prize_manual=atm.first_prize_manual or 0,
                first_prize_semi=atm.first_prize_semi or 0,
            )
            for atm in atms
        ]

        return AtmRankingResponse(
            atms=ranking_list,
            next_cursor=next_cursor,
        )
