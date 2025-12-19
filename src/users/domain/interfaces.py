from datetime import datetime
from typing import List, Optional, Protocol

from src.four_pillars.entities.schemas import FourPillarDetail
from src.users.api.schemas import UserCreate, UserUpdate
from src.users.domain.entities.models import User


class IUserRepository(Protocol):
    """사용자 리포지토리 인터페이스"""

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """사용자 목록을 조회합니다."""
        ...

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """사용자 ID로 사용자를 조회합니다."""
        ...

    async def get_user_four_pillar(self, user_id: str) -> Optional[dict]:
        """사용자의 사주 정보만 조회합니다."""
        ...

    async def create_user(
        self,
        user_create: UserCreate,
        four_pillar: FourPillarDetail,
        birth_datetime: datetime = None,
    ) -> User:
        """사용자를 생성합니다."""
        ...

    async def update_user(
        self,
        user_id: str,
        user_update: UserUpdate,
        four_pillar: Optional[FourPillarDetail] = None,
        birth_datetime: Optional[datetime] = None,
    ) -> Optional[User]:
        """사용자를 업데이트합니다."""
        ...
