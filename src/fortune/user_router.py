# src/fortune/router/user_fortune_router.py

from fastapi import APIRouter, Depends, Query
from src.fortune.service import FortuneService
from src.fortune.entities.schemas import UserDailyFortuneSummary
from typing import List
from datetime import date

user_fortune_router = APIRouter(prefix="/fortune", tags=["fortune-user"])

@user_fortune_router.get("/user-daily-fortunes", response_model=List[UserDailyFortuneSummary])
async def get_user_daily_fortunes(
    user_id: str,
    fortune_date: date = Query(default=date.today()),
    service: FortuneService = Depends(),
):
    return await service.get_user_daily_fortune_summaries(user_id, fortune_date)
