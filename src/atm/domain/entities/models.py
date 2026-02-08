# src/atm/domain/entities/models.py
from xmlrpc.client import Boolean

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from src.config.database import Base

class Atm(Base):
    """ATM 테이블"""

    __tablename__ = "atm"

    id = Column(String(20), primary_key=True)  # RTLRID (ATM ID)
    name = Column(String(100), nullable=False)  # ATM_NAME

    trns_org_code = Column(String(3), nullable=False) # 전송기관코드
    org_type_code = Column(String(3), nullable=False) # 한 기관 내 다수법인 코드가 구분된 경우 사용
    atm_no = Column(String(20), nullable=False) # 단말번호
    dup_atm_no = Column(String(20), nullable=True) # 중복 ATM 번호

    # 위치 정보
    latitude = Column(Numeric(10, 7))  # ATM_LATITUDE
    longitude = Column(Numeric(10, 7))  # ATM_LONGITUDE
    mob_cash_card_psb_yn = Column(String(1)) # 모바일현금카드사용여부
    istl_loc_type_code = Column(String(3)) # 설치장소구분코드
