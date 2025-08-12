# src/fortune/router.py
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from src.fortune.entities.schemas import (
    DailyFortuneResource,
    DailyFortuneResourceCreate,
    DailyFortuneResourceUpdate,
    DailyFortuneResourceList,
)
from src.fortune.service import FortuneService
from src.fortune.entities.enums import FortuneType

fortune_router = APIRouter(prefix="/admin/fortune", tags=["fortune-admin"])


@fortune_router.get(
    "/resources",
    response_model=DailyFortuneResourceList,
    summary="운세 리소스 목록 조회 (관리자)",
)
async def list_fortune_resources(
    cursor: Optional[int] = Query(None, description="다음 페이지 조회를 위한 cursor 값 (id)"),
    limit: int = Query(10, ge=1, le=100, description="한 페이지 크기"),
    publish_date: Optional[date] = Query(None, description="발행일 필터"),
    fortune_type: Optional[FortuneType] = Query(None, description="유형 필터"),
    service: FortuneService = Depends(),
):
    return await service.list_fortunes(cursor, limit, publish_date, fortune_type)


@fortune_router.post(
    "/resources",
    response_model=DailyFortuneResource,
    status_code=status.HTTP_201_CREATED,
    summary="운세 리소스 등록 (관리자)",
)
async def create_fortune_resource(
    body: DailyFortuneResourceCreate,
    service: FortuneService = Depends(),
):
    return await service.create_fortune(body)


@fortune_router.patch(
    "/resources/{resource_id}",
    response_model=DailyFortuneResource,
    summary="운세 리소스 수정 (관리자)",
)
async def update_fortune_resource(
    resource_id: int = Path(..., description="운세 리소스 ID"),
    body: DailyFortuneResourceUpdate = None,
    service: FortuneService = Depends(),
):
    return await service.update_fortune(resource_id, body)


@fortune_router.delete(
    "/resources/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="운세 리소스 삭제 (관리자)",
)
async def delete_fortune_resource(
    resource_id: int = Path(..., description="운세 리소스 ID"),
    service: FortuneService = Depends(),
):
    await service.delete_fortune(resource_id)
    # 204 No Content
