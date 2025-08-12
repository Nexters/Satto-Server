# src/fortune/entities/models.py
from sqlalchemy import Column, Integer, Date, Enum as SAEnum, String, CheckConstraint, UniqueConstraint
from src.config.database import Base
from src.fortune.entities.enums import FortuneType


class DailyFortuneResource(Base):
    __tablename__ = "daily_fortune_resources"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="운세 고유 ID")
    publish_date = Column(Date, nullable=False, comment="운세 발행 날짜")
    fortune_type = Column(SAEnum(FortuneType), nullable=False, comment="운세 항목 종류 (귀인의 초성 등)")
    image_url = Column(String(1000), nullable=False, comment="이미지 URL 또는 경로")
    description = Column(String(1000), nullable=False, comment="운세 설명")

    __table_args__ = (
        CheckConstraint("length(image_url) > 0", name="ck_fortune_image_url_len"),
        CheckConstraint("length(description) > 0", name="ck_fortune_description_len"),
    )
