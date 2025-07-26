# ========= 테스트 용 라우터 ==========

from fastapi import APIRouter

from src.four_pillars.common.calculator import FourPillarsCalculator
from src.four_pillars.entities.schemas import FourPillarRequest, FourPillarResponse

four_pillar_router = APIRouter(prefix="/four-pillars", tags=["four-pillars"])


@four_pillar_router.post("/test", response_model=FourPillarResponse)
async def get_four_pillar(request: FourPillarRequest):
    """사주 API 호출"""
    result = FourPillarsCalculator().calculate_four_pillars(request.birth_date)
    return FourPillarResponse.model_validate(result)
