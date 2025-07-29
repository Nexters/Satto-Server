from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.dependencies import get_db_session
from src.four_pillars.entities.schemas import FourPillar
from src.users.entities.models import User
from src.users.entities.schemas import UserCreate


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

    async def create_user(
        self, user_create: UserCreate, four_pillar: FourPillar
    ) -> User:
        user = User(
            id=user_create.id,
            name=user_create.name,
            birth_date=user_create.birth_date,
            gender=user_create.gender,
            four_pillar=four_pillar,
            is_active=True,
        )

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user
