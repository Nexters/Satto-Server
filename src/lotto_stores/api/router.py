# src/lotto_stores/api/router.py
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query

from src.common.dependencies import get_lotto_store_service
from src.lotto_stores.api.schemas import (
    LottoStoreInfo,
    LottoStoreMapResponse,
    LottoStoreRankingResponse,
    LottoStoreSearchResponse,
    WeeklyWinnersResponse,
)
from src.lotto_stores.application.service import LottoStoreService

lotto_store_router = APIRouter(prefix="/lotto-stores", tags=["lotto-stores"])


@lotto_store_router.get("/map", response_model=LottoStoreMapResponse)
async def get_stores_map(
    min_lat: Decimal = Query(..., description="최소 위도"),
    max_lat: Decimal = Query(..., description="최대 위도"),
    min_lng: Decimal = Query(..., description="최소 경도"),
    max_lng: Decimal = Query(..., description="최대 경도"),
    limit: int = Query(100, ge=1, le=500, description="조회할 최대 개수"),
    store_service: LottoStoreService = Depends(get_lotto_store_service),
):
    """지도 영역 내 판매점 마커 목록을 조회합니다."""
    return await store_service.get_stores_map(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        limit=limit,
    )


@lotto_store_router.get("/search", response_model=LottoStoreSearchResponse)
async def search_stores(
    query: str = Query(
        ..., min_length=1, max_length=100, description="검색어 (복권방명, 주소)"
    ),
    limit: int = Query(20, ge=1, le=50, description="조회할 개수"),
    store_service: LottoStoreService = Depends(get_lotto_store_service),
):
    """복권방을 검색합니다."""
    return await store_service.search_stores(query=query, limit=limit)


@lotto_store_router.get("/weekly-winners", response_model=WeeklyWinnersResponse)
async def get_weekly_winners(
    round: int | None = Query(None, description="회차 (없으면 최신 회차)"),
    store_service: LottoStoreService = Depends(get_lotto_store_service),
):
    """이번주(특정 회차) 1등/2등 배출점을 조회합니다."""
    return await store_service.get_weekly_winners(round=round)


@lotto_store_router.get("/ranking", response_model=LottoStoreRankingResponse)
async def get_ranking(
    region1: str | None = Query(None, description="시/도 (없으면 전국)"),
    cursor: str | None = Query(None, description="다음 페이지 cursor"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    store_service: LottoStoreService = Depends(get_lotto_store_service),
):
    """명당 리스트를 조회합니다. (1등 당첨 횟수 순)"""
    return await store_service.get_ranking(
        region1=region1,
        cursor=cursor,
        limit=limit,
    )


@lotto_store_router.get("/{store_id}", response_model=LottoStoreInfo)
async def get_store_info(
    store_id: str,
    store_service: LottoStoreService = Depends(get_lotto_store_service),
):
    """복권방 상세 정보를 조회합니다. (마커 클릭 시)"""
    store = await store_service.get_store_info(store_id)
    if not store:
        raise HTTPException(
            status_code=404, detail="판매점을 찾을 수 없습니다."
        )
    return store
