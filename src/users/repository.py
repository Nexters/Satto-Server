from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.dependencies import get_db_session
from src.four_pillars.entities.schemas import FourPillarDetail
from src.users.entities.models import User
from src.users.entities.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        query = select(User).where(User.is_active == True).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_four_pillar(self, user_id: str) -> Optional[dict]:
        """사용자의 사주 정보만 조회"""
        query = select(User.four_pillar).where(
            User.id == user_id, User.is_active == True
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self, user_create: UserCreate, four_pillar: FourPillarDetail
    ) -> User:
        four_pillar_dict = four_pillar.model_dump()

        user = User(
            id=user_create.id,
            name=user_create.name,
            birth_date=user_create.birth_date,
            gender=user_create.gender,
            four_pillar=four_pillar_dict,
            is_active=True,
        )

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def update_user(
        self,
        user_id: str,
        user_update: UserUpdate,
        four_pillar: Optional[FourPillarDetail] = None,
    ) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        if four_pillar is not None:
            four_pillar_dict = four_pillar.model_dump()
            update_data["four_pillar"] = four_pillar_dict

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.flush()
        await self.session.refresh(user)

        return user
