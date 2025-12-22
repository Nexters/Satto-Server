# src/lotto_stores/domain/entities/models.py
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from src.config.database import Base
from src.lotto_stores.domain.entities.enums import PrizeType


class LottoStore(Base):
    """로또 판매점 마스터 테이블"""
    __tablename__ = "lotto_stores"

    id = Column(String(20), primary_key=True)  # RTLRID (판매점 ID)
    name = Column(String(100), nullable=False)  # FIRMNM

    # 위치 정보
    latitude = Column(Numeric(10, 7))  # LATITUDE
    longitude = Column(Numeric(10, 7))  # LONGITUDE
    road_address = Column(String(200))  # BPLCDORODTLADRES (도로명주소)
    lot_address = Column(String(100))  # BPLCLOCPLCDTLADRES (지번주소)

    # 지역 분류 (명당 필터링용)
    region1 = Column(String(20), index=True)  # BPLCLOCPLC1 - 시/도 (경기, 서울 등)
    region2 = Column(String(30), index=True)  # BPLCLOCPLC2 - 시/군/구
    region3 = Column(String(20))  # BPLCLOCPLC3 - 동/읍/면

    phone = Column(String(20))  # RTLRSTRTELNO

    # 누적 당첨 통계 (비정규화 - 조회 성능용)
    first_prize_count = Column(Integer, default=0)  # 1등 배출 횟수
    first_prize_auto = Column(Integer, default=0)   # 자동
    first_prize_manual = Column(Integer, default=0)  # 수동
    first_prize_semi = Column(Integer, default=0)   # 반자동

    # 관계
    winning_records = relationship("LottoStoreWinning", back_populates="store")


class LottoStoreWinning(Base):
    """판매점별 당첨 이력 테이블"""
    __tablename__ = "lotto_store_winnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(
        String(20), ForeignKey("lotto_stores.id"), nullable=False, index=True
    )
    round = Column(
        Integer, ForeignKey("lotto_draws.round"), nullable=False, index=True
    )

    prize_rank = Column(Integer, nullable=False)  # 1 또는 2 (1등/2등)
    prize_type = Column(SAEnum(PrizeType))  # 자동/수동/반자동

    # 관계
    store = relationship("LottoStore", back_populates="winning_records")
    draw = relationship("LottoDraws")

    __table_args__ = (
        Index("ix_winning_round_rank", "round", "prize_rank"),  # 회차별 등수 조회용
        Index("ix_winning_store_rank", "store_id", "prize_rank"),  # 판매점별 등수 조회용
    )

