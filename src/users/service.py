from fastapi import Depends, HTTPException

from src.users.entities.models import User
from src.users.entities.schemas import UserCreateRequest, UserResponse, UserListResponse
from src.users.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.repository = user_repository

    async def get_users(self, skip: int = 0, limit: int = 100) -> UserListResponse:
        users = await self.repository.get_users(skip=skip, limit=limit)
        total = len(users)  # 실제로는 count 쿼리를 사용해야 합니다
        return UserListResponse(users=users, total=total)

    async def create_user(self, user_data: UserCreateRequest) -> UserResponse:
        # 이메일 중복 확인
        existing_user = await self.repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 새 사용자 생성
        user = User(
            name=user_data.name,
            email=user_data.email,
            is_active=user_data.is_active
        )

        created_user = await self.repository.create_user(user)
        return created_user
