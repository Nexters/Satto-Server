from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON

from src.config.database import Base
from src.users.entities.enums import Gender


class User(Base):
    __tablename__ = "users"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    four_pillar = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
