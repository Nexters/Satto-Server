# src/atm/domain/interfaces.py
from decimal import Decimal
from typing import Protocol

from src.atm.domain.entities.models import (
    Atm,
    AtmWinning,
)


class IAtmRepository(Protocol):
    """로또 ATM 리포지토리 인터페이스"""

    async def get_atm_by_id(self, atm_id: str) -> Atm | None:
        """ATM ID로 조회"""
        ...

    async def get_atms_in_bounds(
        self,
        min_lat: Decimal,
        max_lat: Decimal,
        min_lng: Decimal,
        max_lng: Decimal,
        limit: int = 100,
    ) -> list[Atm]:
        """지도 영역 내 ATM 조회"""
        ...

    async def search_atms(
        self,
        query: str,
        limit: int = 20,
    ) -> list[Atm]:
        """ATM 검색 (이름, 주소)"""
        ...

    async def create_atm(self, atm_data: dict) -> Atm:
        """ATM 생성"""
        ...

    async def bulk_create_atms(self, atms_data: list[dict]) -> int:
        """ATM 일괄 생성"""
        ...
