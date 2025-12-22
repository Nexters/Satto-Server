# src/lotto_stores/domain/entities/enums.py
from enum import Enum


class PrizeType(str, Enum):
    """당첨 유형 (자동/수동/반자동)"""
    AUTO = "auto"       # 자동
    MANUAL = "manual"   # 수동
    SEMI = "semi"       # 반자동

