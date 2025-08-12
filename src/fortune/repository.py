# src/fortune/repository.py
from datetime import date
from typing import List, Optional, Tuple
from fastapi import Depends
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.dependencies import get_db_session
from src.fortune.entities.models import DailyFortuneResource as DailyFortuneResourceModel
from src.fortune.entities.enums import FortuneType


class FortuneRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

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
