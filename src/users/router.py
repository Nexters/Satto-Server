from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from src.lotto.entities.schemas import LottoRecommendation
from src.lotto.service import LottoService
from src.users.entities.schemas import UserCreate, UserDetail, UserList
from src.users.service import UserService

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.get("", response_model=UserList)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    user_service: UserService = Depends(),
):
    """사용자 목록을 조회합니다."""
    return await user_service.get_users(skip=skip, limit=limit)


@user_router.get("/{user_id}", response_model=UserDetail)
async def get_user(user_id: str, user_service: UserService = Depends()):
    """사용자 단건을 조회합니다."""
    return await user_service.get_user_by_id(user_id)


@user_router.post("", response_model=UserDetail, status_code=201)
async def create_user(user_create: UserCreate, user_service: UserService = Depends()):
    """새로운 사용자를 생성합니다."""
    return await user_service.create_user(user_create)


@user_router.post("/{user_id}/lotto-recommendation", response_model=LottoRecommendation)
async def create_lotto_recommendation(
    user_id: str,
    lotto_service: LottoService = Depends(),
):
    """사용자별 로또 추천을 생성합니다."""
    try:
        return await lotto_service.create_lotto_recommendation(user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"로또 추천 생성 중 오류가 발생했습니다: {str(e)}"
        )


@user_router.get(
    "/{user_id}/lotto-recommendation", response_model=Optional[LottoRecommendation]
)
async def get_lotto_recommendation(
    user_id: str,
    lotto_service: LottoService = Depends(),
):
    """사용자의 최신 로또 추천을 조회합니다."""
    return await lotto_service.get_lotto_recommendation(user_id=user_id)
