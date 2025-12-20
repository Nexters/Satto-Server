from datetime import date
from typing import List, Optional, Tuple, Iterable, Protocol

from src.fortune.domain.entities.enums import FortuneType
from src.fortune.domain.entities.models import (
    DailyFortuneResource as DailyFortuneResourceModel,
    UserDailyFortuneDetail as UserDailyFortuneDetailModel,
)
from src.fortune.api.schemas import UserDailyFortuneSummary


class IFortuneRepository(Protocol):
    """운세 리포지토리 인터페이스"""

    async def create_fortune(
        self,
        publish_date: date,
        fortune_type: FortuneType,
        image_url: str,
        description: str,
    ) -> DailyFortuneResourceModel:
        ...

    async def update_fortune(
        self,
        resource_id: int,
        publish_date: Optional[date],
        fortune_type: Optional[FortuneType],
        image_url: Optional[str],
        description: Optional[str],
    ) -> DailyFortuneResourceModel:
        ...

    async def delete_fortune(self, resource_id: int) -> None:
        ...

    async def get_fortunes(
        self,
        cursor: Optional[int] = None,
        limit: int = 10,
        publish_date: Optional[date] = None,
        fortune_type: Optional[FortuneType] = None,
    ) -> Tuple[List[DailyFortuneResourceModel], Optional[int]]:
        ...

    async def get_fortune_by_id(
        self, resource_id: int
    ) -> Optional[DailyFortuneResourceModel]:
        ...

    async def get_user_daily_fortune_summaries(
        self, user_id: str, fortune_date: date
    ) -> List[UserDailyFortuneSummary]:
        ...

    async def get_user_daily_fortune_detail(
        self, user_id: str, fortune_date: date
    ) -> Optional[UserDailyFortuneDetailModel]:
        ...

    async def create_user_daily_fortune_detail(
        self,
        user_id: str,
        fortune_date: date,
        fortune_score: int,
        fortune_comment: str,
        fortune_details: List[dict],
    ) -> UserDailyFortuneDetailModel:
        ...

    async def get_user_daily_fortune_resources(
        self,
        ref_date: Optional[date] = None,
    ) -> List[DailyFortuneResourceModel]:
        ...

    async def bulk_upsert_user_daily_fortune_summaries(
        self,
        user_id: str,
        fortune_date: date,
        resource_ids: Iterable[int],
    ) -> None:
        ...

