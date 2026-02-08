# src/atm/domain/entities/models.py

from sqlalchemy import Column, Numeric, String, Index
from src.config.database import Base


class Atm(Base):
    """ATM 테이블 (Kakao Local 기반 ATM 데이터)"""

    __tablename__ = "atm"

    # Kakao place id는 숫자 문자열이지만 길이가 길 수 있어 넉넉히
    id = Column(String(32), primary_key=True)

    place_name = Column(String(255), nullable=False)
    category_name = Column(String(255), nullable=True)

    category_group_code = Column(String(16), nullable=True)
    category_group_name = Column(String(64), nullable=True)

    phone = Column(String(64), nullable=True)

    address_name = Column(String(255), nullable=True)
    road_address_name = Column(String(255), nullable=True)

    # 명세에서 latitude/longitude 순서로 들어오므로 그대로 유지
    latitude = Column(Numeric(10, 7), nullable=True)   # y
    longitude = Column(Numeric(10, 7), nullable=True)  # x

    place_url = Column(String(255), nullable=True)

    __table_args__ = (
        # 좌표 기반 조회가 많으면 인덱스 추천
        Index("idx_atm_lat_lon", "latitude", "longitude"),
        Index("idx_atm_place_name", "place_name"),
    )
