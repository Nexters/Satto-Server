# src/fortune/service.py
from datetime import date
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.fortune.entities.models import DailyFortuneResource as DailyFortuneResourceModel
from src.fortune.entities.schemas import UserDailyFortuneSummary
from src.fortune.entities.schemas import (
    DailyFortuneResource,
    DailyFortuneResourceCreate,
    DailyFortuneResourceUpdate,
    DailyFortuneResourceList,
)
from src.fortune.repository import FortuneRepository
from src.common.dependencies import get_db_session
from src.fortune.entities.enums import FortuneType


class FortuneService:
    def __init__(
        self,
        fortune_repository: FortuneRepository = Depends(),
        session: AsyncSession = Depends(get_db_session),
    ):
        self.repository = fortune_repository
        self.session = session

    async def list_fortunes(
        self,
        cursor: Optional[int],
        limit: int,
        publish_date: Optional[date],
        fortune_type: Optional[FortuneType],
    ) -> DailyFortuneResourceList:
        items, next_cursor = await self.repository.get_fortunes(
            cursor=cursor, limit=limit, publish_date=publish_date, fortune_type=fortune_type
        )
        return DailyFortuneResourceList(
            items=[DailyFortuneResource.model_validate(i) for i in items],
            next_cursor=next_cursor,
        )

    async def create_fortune(self, dto: DailyFortuneResourceCreate) -> DailyFortuneResource:
        # DTO에서 개별 필드를 추출하여 리포지토리 메서드 호출
        model = await self.repository.create_fortune(
            publish_date=dto.publish_date,
            fortune_type=dto.fortune_type,
            image_url=dto.image_url,
            description=dto.description
        )

        # DB 모델을 DTO로 변환하여 반환
        return DailyFortuneResource.model_validate(model)

    async def update_fortune(self, resource_id: int, dto: DailyFortuneResourceUpdate) -> DailyFortuneResource:
        model = await self.repository.update_fortune(
            resource_id=resource_id,
            publish_date=dto.publish_date,
            fortune_type=dto.fortune_type,
            image_url=dto.image_url,
            description=dto.description
        )

        return DailyFortuneResource.model_validate(model)

    async def delete_fortune(self, resource_id: int) -> None:
        try:
            await self.repository.delete_fortune(resource_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="리소스를 찾을 수 없습니다.")

    async def get_user_daily_fortune_summaries(self, user_id: str, fortune_date: date) -> List[UserDailyFortuneSummary]:
        summaries = await self.repository.get_user_daily_fortune_summaries(user_id, fortune_date)
        if not summaries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="오늘의 운세 데이터를 찾을 수 없습니다."
            )
        return summaries  # Return the list directly