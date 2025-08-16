from datetime import datetime, time

from fastapi import Depends, HTTPException

from src.four_pillars.common.calculator import FourPillarsCalculator
from src.four_pillars.entities.schemas import FourPillarDetail
from src.users.common.utils import TimeUtils
from src.users.entities.schemas import UserCreate, UserDetail, UserList, UserUpdate
from src.users.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.repository = user_repository
        self.four_pillar_calculator = FourPillarsCalculator()

    async def get_users(self, skip: int = 0, limit: int = 100) -> UserList:
        users = await self.repository.get_users(skip=skip, limit=limit)
        total = len(users)  # 실제로는 count 쿼리를 사용해야 합니다

        user_details = [self._convert_user_to_detail(user) for user in users]
        return UserList(users=user_details, total=total)

    async def get_user_by_id(self, user_id: str) -> UserDetail:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return self._convert_user_to_detail(user)

    async def create_user(self, user_create: UserCreate) -> UserDetail:
        existing_user = await self.repository.get_user_by_id(user_create.id)
        if existing_user:
            raise HTTPException(status_code=400, detail="User ID already exists")

        birth_time = None
        if user_create.birth_time:
            birth_time = TimeUtils.range_to_time(user_create.birth_time)

        birth_datetime = (
            datetime.combine(user_create.birth_date, birth_time)
            if birth_time
            else datetime.combine(user_create.birth_date, time(0, 0))
        )

        four_pillar = self.four_pillar_calculator.calculate_four_pillars_detailed(
            birth_datetime
        )

        created_user = await self.repository.create_user(
            user_create, four_pillar, birth_datetime
        )
        return self._convert_user_to_detail(created_user)

    async def get_user_four_pillar(self, user_id: str) -> FourPillarDetail:
        """사용자의 사주 정보만 조회"""
        four_pillar_dict = await self.repository.get_user_four_pillar(user_id)
        if not four_pillar_dict:
            raise HTTPException(status_code=404, detail="User not found")

        return FourPillarDetail.model_validate(four_pillar_dict)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserDetail:
        four_pillar = None

        # birth_time과 birth_date를 결합하여 datetime 생성
        birth_datetime = None
        if user_update.birth_date:
            if user_update.birth_time:
                birth_time = TimeUtils.range_to_time(user_update.birth_time)
                if birth_time:
                    birth_datetime = datetime.combine(
                        user_update.birth_date, birth_time
                    )
                else:
                    birth_datetime = datetime.combine(
                        user_update.birth_date, time(0, 0)
                    )
            else:
                birth_datetime = datetime.combine(user_update.birth_date, time(0, 0))

        if birth_datetime:
            four_pillar = self.four_pillar_calculator.calculate_four_pillars_detailed(
                birth_datetime
            )

        updated_user = await self.repository.update_user(
            user_id, user_update, four_pillar, birth_datetime
        )
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        return self._convert_user_to_detail(updated_user)

    def _convert_user_to_detail(self, user) -> UserDetail:
        """User 모델을 UserDetail로 변환 (birth_time을 시간 범위로 변환)"""
        user_dict = user.__dict__.copy()

        if user.birth_date:
            # datetime을 date로 변환
            user_dict["birth_date"] = user.birth_date.date()
            birth_time = user.birth_date.time()
            user_dict["birth_time"] = TimeUtils.time_to_range(birth_time)

        return UserDetail.model_validate(user_dict)
