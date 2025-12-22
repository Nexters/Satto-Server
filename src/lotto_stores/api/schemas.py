# src/lotto_stores/api/schemas.py
from decimal import Decimal
from typing import Optional

from pydantic import Field

from src.config.schemas import CommonBase
from src.lotto_stores.domain.entities.enums import PrizeType


# ========================================
# 1. 지도 마커용 (최소 정보)
# ========================================
class LottoStoreMarker(CommonBase):
    """지도 마커 표시용"""

    id: str
    name: str = Field(description="복권방 이름")
    latitude: Decimal = Field(description="위도")
    longitude: Decimal = Field(description="경도")


# ========================================
# 2. 마커 클릭 시 상세 정보
# ========================================
class LottoStoreInfo(CommonBase):
    """마커 클릭 시 표시되는 정보"""

    id: str
    name: str = Field(description="복권방 이름")
    address: str = Field(description="주소")
    phone: Optional[str] = Field(None, description="전화번호")


# ========================================
# 3. 검색 결과용 (지도 마커 표시 필요)
# ========================================
class LottoStoreSearchResult(CommonBase):
    """검색 결과 (지도 마커 표시 가능)"""

    id: str
    name: str = Field(description="복권방 이름")
    address: str = Field(description="주소")
    latitude: Optional[Decimal] = Field(None, description="위도")
    longitude: Optional[Decimal] = Field(None, description="경도")


# ========================================
# 4. 이번주 당첨 - 1등 배출점
# ========================================
class LottoStoreFirstPrize(CommonBase):
    """1등 배출점 (자동/수동/반자동 여부 포함)"""

    id: str
    name: str = Field(description="복권방 이름")
    address: str = Field(description="주소")
    latitude: Optional[Decimal] = Field(None, description="위도")
    longitude: Optional[Decimal] = Field(None, description="경도")
    prize_type: Optional[PrizeType] = Field(
        None, description="자동/수동/반자동"
    )


# ========================================
# 5. 이번주 당첨 - 2등 배출점
# ========================================
class LottoStoreSecondPrize(CommonBase):
    """2등 배출점 (자동/수동/반자동 없음)"""

    id: str
    name: str = Field(description="복권방 이름")
    address: str = Field(description="주소")
    latitude: Optional[Decimal] = Field(None, description="위도")
    longitude: Optional[Decimal] = Field(None, description="경도")


# ========================================
# 6. 명당 리스트용 (순위별)
# ========================================
class LottoStoreRanking(CommonBase):
    """명당 리스트 (1등 당첨 통계 포함)"""

    id: str
    name: str = Field(description="복권방 이름")
    address: str = Field(description="주소")
    latitude: Optional[Decimal] = Field(None, description="위도")
    longitude: Optional[Decimal] = Field(None, description="경도")
    first_prize_count: int = Field(description="1등 당첨 횟수")
    first_prize_auto: int = Field(description="자동 횟수")
    first_prize_manual: int = Field(description="수동 횟수")
    first_prize_semi: int = Field(description="반자동 횟수")


# ========================================
# API 응답 스키마
# ========================================
class LottoStoreMapResponse(CommonBase):
    """지도 마커 목록 응답"""

    markers: list[LottoStoreMarker]


class LottoStoreSearchResponse(CommonBase):
    """검색 결과 응답"""

    results: list[LottoStoreSearchResult]


class WeeklyWinnersResponse(CommonBase):
    """이번주 당첨 판매점 응답"""

    round: int = Field(description="회차")
    first_prize_stores: list[LottoStoreFirstPrize] = Field(
        description="1등 배출점"
    )
    second_prize_stores: list[LottoStoreSecondPrize] = Field(
        description="2등 배출점"
    )


class LottoStoreRankingResponse(CommonBase):
    """명당 리스트 응답"""

    stores: list[LottoStoreRanking]
    next_cursor: Optional[str] = None
