from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.users.service import UserService

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.get("")
async def get_user(request: Request, user_service: UserService = Depends()):
    """
    현재 로그인한 사용자의 정보를 반환합니다.
    """

    return await user_service.test()
