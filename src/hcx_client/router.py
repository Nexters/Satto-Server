# ========= 테스트 용 라우터 ==========
import traceback

from fastapi import APIRouter, HTTPException

from src.common.logger import logger
from src.hcx_client.client import HCXClient
from src.hcx_client.entities.schemas import FourPillarRequest, FourPillarResponse

hcx_router = APIRouter(prefix="/hcx", tags=["hcx"])


@hcx_router.post("/four-pillar", response_model=FourPillarResponse)
async def get_four_pillar(
    request: FourPillarRequest
):
    """사주 API 호출"""
    try:
        result = await HCXClient().get_four_pillar(
            name=request.name,
            gender=request.gender,
            birth_date=request.birth_date
        )
        return result
    except Exception as e:
        logger.info(f"{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"HCX API 호출 실패: {str(e)}")
