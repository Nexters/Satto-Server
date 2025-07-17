from fastapi import APIRouter, Depends, Query

from src.users.entities.schemas import UserCreateRequest, UserResponse, UserListResponse
from src.users.service import UserService

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.get("", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    user_service: UserService = Depends()
):
    """사용자 목록을 조회합니다."""
    return await user_service.get_users(skip=skip, limit=limit)


@user_router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends()
):
    """새로운 사용자를 생성합니다."""
    return await user_service.create_user(user_data)
