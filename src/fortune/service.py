# src/fortune/service.py
from datetime import date
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.fortune.entities.models import DailyFortuneResource as DailyFortuneResourceModel
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
        model = DailyFortuneResourceModel(
            publish_date=dto.publish_date,
            fortune_type=dto.fortune_type,
            image_url=dto.image_url,
            description=dto.description,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return DailyFortuneResource.model_validate(model)

    async def update_fortune(self, resource_id: int, dto: DailyFortuneResourceUpdate) -> DailyFortuneResource:
        model = await self.repository.get_fortune_by_id(resource_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="리소스를 찾을 수 없습니다.")

        # 부분 수정 반영
        for field in ("publish_date", "fortune_type", "image_url", "description"):
            value = getattr(dto, field)
            if value is not None:
                setattr(model, field, value)

        await self.session.commit()
        await self.session.refresh(model)
        return DailyFortuneResource.model_validate(model)

    async def delete_fortune(self, resource_id: int) -> None:
        model = await self.repository.get_fortune_by_id(resource_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="리소스를 찾을 수 없습니다.")
        await self.session.delete(model)
        await self.session.commit()
