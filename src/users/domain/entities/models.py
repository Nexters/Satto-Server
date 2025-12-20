from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship

from src.config.database import Base
from src.users.domain.entities.enums import Gender


class User(Base):
    __tablename__ = "users"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    four_pillar = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    lotto_recommendations = relationship(
        "LottoRecommendations", back_populates="user"
    )
