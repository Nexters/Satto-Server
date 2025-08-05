from sqlalchemy import Column, Integer, Date, CheckConstraint, BigInteger

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

    __table_args__ = (
        CheckConstraint("num1 BETWEEN 1 AND 45", name="num1_range_check"),
        CheckConstraint("num2 BETWEEN 1 AND 45", name="num2_range_check"),
        CheckConstraint("num3 BETWEEN 1 AND 45", name="num3_range_check"),
        CheckConstraint("num4 BETWEEN 1 AND 45", name="num4_range_check"),
        CheckConstraint("num5 BETWEEN 1 AND 45", name="num5_range_check"),
        CheckConstraint("num6 BETWEEN 1 AND 45", name="num6_range_check"),
        CheckConstraint("bonus_num BETWEEN 1 AND 45", name="bonus_num_range_check"),
    )
