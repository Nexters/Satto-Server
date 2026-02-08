# src/atm/api/router.py
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query

from src.common.dependencies import get_atm_service
from src.atm.api.schemas import (
    AtmInfo,
    AtmMapResponse,
    AtmSearchResponse,
)
from src.atm.application.service import AtmService

atm_router = APIRouter(prefix="/atm", tags=["atm"])


@atm_router.get("/map", response_model=AtmMapResponse)
async def get_atm_map(
    min_lat: Decimal = Query(..., description="최소 위도"),
    max_lat: Decimal = Query(..., description="최대 위도"),
    min_lng: Decimal = Query(..., description="최소 경도"),
    max_lng: Decimal = Query(..., description="최대 경도"),
    limit: int = Query(100, ge=1, le=500, description="조회할 최대 개수"),
    atm_service: AtmService = Depends(get_atm_service),
):
    """지도 영역 내 ATM 마커 목록을 조회합니다."""
    return await atm_service.get_atms_map(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        limit=limit,
    )


@atm_router.get("/search", response_model=AtmSearchResponse)
async def search_atm(
    query: str = Query(
        ..., min_length=1, max_length=100, description="검색어 (ATM명)"
    ),
    limit: int = Query(20, ge=1, le=50, description="조회할 개수"),
    atm_service: AtmService = Depends(get_atm_service),
):
    """ATM을 검색합니다."""
    return await atm_service.search_atms(query=query, limit=limit)


@atm_router.get("/{atm_id}", response_model=AtmInfo)
async def get_atm_info(
    atm_id: str,
    atm_service: AtmService = Depends(get_atm_service),
):
    """ATM 상세 정보를 조회합니다. (마커 클릭 시)"""
    atm = await atm_service.get_atm_info(atm_id)
    if not atm:
        raise HTTPException(
            status_code=404, detail="ATM을 찾을 수 없습니다."
        )
    return atm
