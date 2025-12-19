from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    Date,
    CheckConstraint,
    BigInteger,
    String,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from src.config.database import Base


class LottoStatistics(Base):
    __tablename__ = "lotto_statistics"

    num = Column(Integer, primary_key=True, autoincrement=False)
    main_count = Column(Integer, default=0)  # 메인 번호로 나온 횟수
    bonus_count = Column(Integer, default=0)  # 보너스 번호로 나온 횟수
    total_count = Column(Integer, default=0)  # 전체 출현 횟수
    last_round = Column(Integer)  # 마지막 출현 회차
    last_date = Column(Date)  # 마지막 출현 날짜

    __table_args__ = (CheckConstraint("num BETWEEN 1 AND 45", name="num_range_check"),)


class LottoDraws(Base):
    __tablename__ = "lotto_draws"

    round = Column(Integer, primary_key=True, autoincrement=False)
    draw_date = Column(Date, nullable=False)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    num4 = Column(Integer, nullable=False)
    num5 = Column(Integer, nullable=False)
    num6 = Column(Integer, nullable=False)
    bonus_num = Column(Integer, nullable=False)
    first_prize_amount = Column(BigInteger, nullable=False)
    total_winners = Column(Integer, nullable=False)

    __table_args__ = tuple(
        CheckConstraint(f"{col} BETWEEN 1 AND 45", name=f"{col}_range_check")
        for col in ["num1", "num2", "num3", "num4", "num5", "num6", "bonus_num"]
    )


class LottoRecommendations(Base):
    __tablename__ = "lotto_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    round = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="lotto_recommendations")

