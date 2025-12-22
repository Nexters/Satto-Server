# src/lotto_stores/domain/interfaces.py
from decimal import Decimal
from typing import Protocol

from src.lotto_stores.domain.entities.models import (
    LottoStore,
    LottoStoreWinning,
)


class ILottoStoreRepository(Protocol):
    """로또 판매점 리포지토리 인터페이스"""

    async def get_store_by_id(self, store_id: str) -> LottoStore | None:
        """판매점 ID로 조회"""
        ...

    async def get_stores_in_bounds(
        self,
        min_lat: Decimal,
        max_lat: Decimal,
        min_lng: Decimal,
        max_lng: Decimal,
        limit: int = 100,
    ) -> list[LottoStore]:
        """지도 영역 내 판매점 조회"""
        ...

    async def search_stores(
        self,
        query: str,
        limit: int = 20,
    ) -> list[LottoStore]:
        """판매점 검색 (이름, 주소)"""
        ...

    async def get_latest_winning_round(self) -> int | None:
        """가장 최근 당첨 회차 조회"""
        ...

    async def get_winnings_by_round(
        self,
        round: int,
    ) -> list[LottoStoreWinning]:
        """특정 회차의 당첨 판매점 조회"""
        ...

    async def get_ranking(
        self,
        region1: str | None = None,
        cursor: str | None = None,
        limit: int = 20,
    ) -> tuple[list[LottoStore], str | None]:
        """명당 리스트 조회 (1등 당첨 횟수 순)"""
        ...

    async def create_store(self, store_data: dict) -> LottoStore:
        """판매점 생성"""
        ...

    async def bulk_create_stores(self, stores_data: list[dict]) -> int:
        """판매점 일괄 생성"""
        ...

    async def create_store_winning(
        self, winning_data: dict
    ) -> LottoStoreWinning:
        """당첨 이력 생성"""
        ...

    async def update_store_statistics(
        self,
        store_id: str,
        prize_type: str | None = None,
    ) -> None:
        """판매점 당첨 통계 업데이트"""
        ...
