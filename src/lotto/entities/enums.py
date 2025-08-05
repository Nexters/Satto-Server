from enum import Enum


class SortType(str, Enum):
    FREQUENCY = "frequency"  # 빈도순
    NUMBER = "number"        # 번호순
