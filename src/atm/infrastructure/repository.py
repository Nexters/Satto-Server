# src/atm/infrastructure/repository.py
from decimal import Decimal

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.atm.domain.entities.models import (
    Atm,
)


class AtmRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_atm_by_id(self, atm_id: str) -> Atm | None:
        """ATM ID로 조회"""
        query = select(Atm).where(Atm.id == atm_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_atms_in_bounds(
        self,
        min_lat: Decimal,
        max_lat: Decimal,
        min_lng: Decimal,
        max_lng: Decimal,
        limit: int = 100,
    ) -> list[Atm]:
        """지도 영역 내 ATM 조회"""
        # TODO: Spatial query 사용
        query = (
            select(Atm)
            .where(
                Atm.latitude.isnot(None),
                Atm.longitude.isnot(None),
                Atm.latitude >= min_lat,
                Atm.latitude <= max_lat,
                Atm.longitude >= min_lng,
                Atm.longitude <= max_lng,
            )
            .order_by(desc(Atm.first_prize_count), Atm.id)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_atms(
        self,
        query: str,
        limit: int = 20,
    ) -> list[Atm]:
        """ATM 검색 (이름, 주소)"""
        search_pattern = f"%{query}%"

        stmt = (
            select(Atm)
            .where(
                or_(
                    Atm.name.ilike(search_pattern),
                    Atm.road_address.ilike(search_pattern),
                    Atm.lot_address.ilike(search_pattern),
                    Atm.region1.ilike(search_pattern),
                    Atm.region2.ilike(search_pattern),
                    Atm.region3.ilike(search_pattern),
                )
            )
            .order_by(desc(Atm.first_prize_count), Atm.name)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_atm(self, atm_data: dict) -> Atm:
        """ATM 생성"""
        atm = Atm(**atm_data)
        self.session.add(atm)
        await self.session.flush()
        await self.session.refresh(atm)
        return atm

    async def bulk_create_atms(self, atms_data: list[dict]) -> int:
        """ATM 일괄 생성"""
        atms = [Atm(**data) for data in atms_data]
        self.session.add_all(atms)
        await self.session.flush()
        return len(atms)