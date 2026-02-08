# src/atm/application/service.py
from decimal import Decimal
from typing import Optional

from src.atm.api.schemas import (
    AtmInfo,
    AtmMapResponse,
    AtmMarker,
    AtmSearchResponse,
    AtmSearchResult,
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
        return atm.road_address_name or atm.address_name or ""

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
                name=atm.place_name,
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
            name=atm.place_name,
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
                name=atm.place_name,
                address=self._get_address(atm),
                latitude=atm.latitude,
                longitude=atm.longitude,
            )
            for atm in atms
        ]

        return AtmSearchResponse(results=results)