from typing import Optional, List

from fastapi import APIRouter, Depends, Query

from src.lotto.entities.enums import SortType
from src.lotto.entities.schemas import LottoDrawList, LottoStatistic
from src.lotto.service import LottoService

lotto_router = APIRouter(prefix="/lotto", tags=["lotto"])


@lotto_router.get("/draws", response_model=LottoDrawList)
async def get_lotto_draws(
    cursor: Optional[int] = Query(
        None, description="다음 페이지 조회를 위한 cursor 값"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    lotto_service: LottoService = Depends(),
):
    """로또 회차별 리스트를 조회합니다."""
    return await lotto_service.get_lotto_draws(cursor=cursor, limit=limit)


@lotto_router.get("/statistics", response_model=List[LottoStatistic])
async def get_lotto_statistics(
    sort_type: SortType = Query(
        SortType.FREQUENCY, description="정렬 기준: frequency(빈도순), number(번호순)"
    ),
    include_bonus: bool = Query(True, description="보너스 번호 포함 여부"),
    lotto_service: LottoService = Depends(),
):
    """로또 번호별 통계를 조회합니다."""
    return await lotto_service.get_lotto_statistics(
        sort_type=sort_type, include_bonus=include_bonus
    )
