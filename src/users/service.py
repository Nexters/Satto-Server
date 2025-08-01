from fastapi import Depends, HTTPException

from src.four_pillars.common.calculator import FourPillarsCalculator
from src.users.entities.schemas import UserCreate, UserDetail, UserList
from src.users.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.repository = user_repository
        self.four_pillar_calculator = FourPillarsCalculator()

    async def get_users(self, skip: int = 0, limit: int = 100) -> UserList:
        users = await self.repository.get_users(skip=skip, limit=limit)
        total = len(users)  # 실제로는 count 쿼리를 사용해야 합니다

        user_details = [UserDetail.model_validate(user) for user in users]

        return UserList(users=user_details, total=total)

    async def get_user_by_id(self, user_id: str) -> UserDetail:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserDetail.model_validate(user)

    async def create_user(self, user_create: UserCreate) -> UserDetail:
        existing_user = await self.repository.get_user_by_id(user_create.id)
        if existing_user:
            raise HTTPException(status_code=400, detail="User ID already exists")

        four_pillar = self.four_pillar_calculator.calculate_four_pillars(
            user_create.birth_date
        )
        created_user = await self.repository.create_user(user_create, four_pillar)

        return UserDetail.model_validate(created_user)
