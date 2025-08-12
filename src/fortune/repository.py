# src/fortune/repository.py
from datetime import date
from typing import List, Optional, Tuple
from fastapi import Depends
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.dependencies import get_db_session
from src.fortune.entities.models import UserDailyFortuneSummary as UserDailyFortuneSummaryModel, DailyFortuneResource as DailyFortuneResourceModel
from src.fortune.entities.enums import FortuneType
from src.fortune.entities.schemas import UserDailyFortuneSummary


class FortuneRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_fortune(
        self,
        publish_date: date,
        fortune_type: FortuneType,
        image_url: str,
        description: str
    ) -> DailyFortuneResourceModel:
        model = DailyFortuneResourceModel(
            publish_date=publish_date,
            fortune_type=fortune_type,
            image_url=image_url,
            description=description,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model  # DB 모델 반환

    async def update_fortune(
        self,
        resource_id: int,
        publish_date: Optional[date],
        fortune_type: Optional[FortuneType],
        image_url: Optional[str],
        description: Optional[str]
    ) -> DailyFortuneResourceModel:
        model = await self.get_fortune_by_id(resource_id)
        if not model:
            raise ValueError("리소스를 찾을 수 없습니다.")

        if publish_date is not None:
            model.publish_date = publish_date
        if fortune_type is not None:
            model.fortune_type = fortune_type
        if image_url is not None:
            model.image_url = image_url
        if description is not None:
            model.description = description

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete_fortune(self, resource_id: int) -> None:
        model = await self.get_fortune_by_id(resource_id)
        if not model:
            raise ValueError("리소스를 찾을 수 없습니다.")
        await self.session.delete(model)
        await self.session.commit()

    async def get_fortunes(
        self,
        cursor: Optional[int] = None,
        limit: int = 10,
        publish_date: Optional[date] = None,
        fortune_type: Optional[FortuneType] = None,
    ) -> Tuple[List[DailyFortuneResourceModel], Optional[int]]:
        query = select(DailyFortuneResourceModel).order_by(desc(DailyFortuneResourceModel.id))

        conditions = []
        if cursor:
            conditions.append(DailyFortuneResourceModel.id < cursor)
        if publish_date:
            conditions.append(DailyFortuneResourceModel.publish_date == publish_date)
        if fortune_type:
            conditions.append(DailyFortuneResourceModel.fortune_type == fortune_type)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.limit(limit)
        result = await self.session.execute(query)
        items = result.scalars().all()

        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor

    async def get_fortune_by_id(self, resource_id: int) -> Optional[DailyFortuneResourceModel]:
        return await self.session.get(DailyFortuneResourceModel, resource_id)

    async def get_user_daily_fortune_summaries(
            self, user_id: str, fortune_date: date
    ) -> List[UserDailyFortuneSummary]:
        query = select(
            UserDailyFortuneSummaryModel.id,
            UserDailyFortuneSummaryModel.user_id,
            UserDailyFortuneSummaryModel.fortune_date,
            DailyFortuneResourceModel.fortune_type,
            DailyFortuneResourceModel.image_url,
            DailyFortuneResourceModel.description
        ).join(
            DailyFortuneResourceModel,
            UserDailyFortuneSummaryModel.daily_fortune_resource_id == DailyFortuneResourceModel.id
        ).filter(
            UserDailyFortuneSummaryModel.user_id == user_id,
            UserDailyFortuneSummaryModel.fortune_date == fortune_date
        )

        result = await self.session.execute(query)
        summaries = result.fetchall()

        # 반환할 데이터를 Pydantic 모델로 변환하여 반환
        return [
            UserDailyFortuneSummary(
                id=summary[0],
                user_id=summary[1],
                fortune_date=summary[2],
                fortune_type=summary[3],
                image_url=summary[4],
                description=summary[5]
            )
            for summary in summaries
        ]