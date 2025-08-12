from enum import Enum


class FiveElements(str, Enum):
    """오행 (五行)"""

    WOOD = "목(木)"
    FIRE = "화(火)"
    EARTH = "토(土)"
    METAL = "금(金)"
    WATER = "수(水)"


class TenGods(str, Enum):
    """십신 (十神)"""

    COMPARISON = "비견"
    COMPETITOR = "겁재"
    EATING = "식신"
    HURTING = "상관"
    PARTIAL_WEALTH = "편재"
    DIRECT_WEALTH = "정재"
    PARTIAL_OFFICIAL = "편관"
    DIRECT_OFFICIAL = "정관"
    PARTIAL_PRINT = "편인"
    DIRECT_PRINT = "정인"
