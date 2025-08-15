# src/fortune/entities/models.py
from sqlalchemy import Column, Integer, Date, Enum as SAEnum, String, CheckConstraint, ForeignKey, JSON
from sqlalchemy.orm import relationship
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

class UserDailyFortuneSummary(Base):
    __tablename__ = "user_daily_fortune_summary"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="운세 기록 고유 ID")
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False, comment="유저 ID")
    daily_fortune_resource_id = Column(Integer, ForeignKey("daily_fortune_resources.id"), nullable=False, comment="운세 리소스 ID")
    fortune_date = Column(Date, nullable=False, comment="운세 날짜")


class UserDailyFortuneDetail(Base):
    __tablename__ = "user_daily_fortune_detail"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="운세 상세 기록 고유 ID")
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False, comment="유저 ID")
    fortune_date = Column(Date, nullable=False, comment="운세 날짜")
    fortune_score = Column(Integer, nullable=False, comment="운세 점수")
    fortune_comment = Column(String(1000), nullable=False, comment="운세 코멘트")
    fortune_details = Column(JSON, nullable=False, comment="운세 상세 정보 (JSON)")

    __table_args__ = (
        CheckConstraint("fortune_score >= 0 AND fortune_score <= 100", name="ck_fortune_score_range"),
        CheckConstraint("length(fortune_comment) > 0", name="ck_fortune_comment_len"),
    )
