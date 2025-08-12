# src/fortune/entities/enums.py
from enum import Enum


class FortuneType(str, Enum):
    """운세 항목 종류"""
    GUIIN_INITIAL = "귀인의 초성"
    LUCKY_OBJECT = "행운의 오브제"
    PERFECT_TIMING = "절호의 타이밍"
    TABOO_OF_DAY = "오늘의 금기"
