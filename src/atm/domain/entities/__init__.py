# src/atm/domain/entities/__init__.py
from src.atm.domain.entities.enums import PrizeType
from src.atm.domain.entities.models import (
    Atm,
    AtmWinning,
)

__all__ = ["Atm", "AtmWinning", "PrizeType"]
