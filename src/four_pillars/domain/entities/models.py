"""도메인 모델 정의

Note: 이 모듈은 SQLAlchemy ORM 모델이 아닌 도메인 모델을 정의합니다.
four_pillars 모듈은 별도의 DB 테이블이 없으며, User 테이블의 JSON 컬럼에 저장됩니다.
"""

from typing import Optional

from pydantic import BaseModel
from typing_extensions import TypedDict

from src.four_pillars.domain.entities.enums import TenGods


class FourPillar(TypedDict, total=False):
    """사주 기본 정보 (도메인 모델)
    
    Note: 이 모델은 별도의 DB 테이블이 없으며, User 테이블의 JSON 컬럼에 저장됩니다.
    """

    year_pillar: str  # 년주
    month_pillar: str  # 월주
    day_pillar: str  # 일주
    time_pillar: Optional[str]  # 시주


class PillarInfo(BaseModel):
    """기둥(주) 상세 정보 (도메인 모델)"""

    stem: str  # 천간 (첫 번째 글자)
    branch: str  # 지지 (두 번째 글자)
    stem_ten_god: TenGods  # 천간의 십신
    branch_ten_god: TenGods  # 지지의 십신

