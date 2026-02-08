# src/atm/api/schemas.py
from decimal import Decimal
from typing import Optional

from pydantic import Field

from src.config.schemas import CommonBase


# ========================================
# 1. 지도 마커용 (최소 정보)
# ========================================
class AtmMarker(CommonBase):
    """지도 마커 표시용"""

    id: str
    name: str = Field(description="ATM 이름")
    latitude: Decimal = Field(description="위도")
    longitude: Decimal = Field(description="경도")


# ========================================
# 2. 마커 클릭 시 상세 정보
# ========================================
class AtmInfo(CommonBase):
    """마커 클릭 시 표시되는 정보"""

    id: str
    name: str = Field(description="ATM 이름")
    address: str = Field(description="주소")
    phone: Optional[str] = Field(None, description="전화번호")


# ========================================
# 3. 검색 결과용 (지도 마커 표시 필요)
# ========================================
class AtmSearchResult(CommonBase):
    """검색 결과 (지도 마커 표시 가능)"""

    id: str
    name: str = Field(description="ATM 이름")
    address: str = Field(description="주소")
    latitude: Optional[Decimal] = Field(None, description="위도")
    longitude: Optional[Decimal] = Field(None, description="경도")


# ========================================
# API 응답 스키마
# ========================================
class AtmMapResponse(CommonBase):
    """지도 마커 목록 응답"""

    markers: list[AtmMarker]


class AtmSearchResponse(CommonBase):
    """검색 결과 응답"""

    results: list[AtmSearchResult]

