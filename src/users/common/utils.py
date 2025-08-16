from datetime import time
from typing import Optional, Tuple


class TimeUtils:
    # 시간 범위 정의 (2시간 단위)
    TIME_RANGES = [
        ("23:00", "00:59"),
        ("01:00", "02:59"),
        ("03:00", "04:59"),
        ("05:00", "06:59"),
        ("07:00", "08:59"),
        ("09:00", "10:59"),
        ("11:00", "12:59"),
        ("13:00", "14:59"),
        ("15:00", "16:59"),
        ("17:00", "18:59"),
        ("19:00", "20:59"),
        ("21:00", "22:59"),
    ]

    @staticmethod
    def time_to_range(time_obj: time) -> Optional[Tuple[str, str]]:
        """
        time 객체를 시간 범위로 변환
        """
        if time_obj is None:
            return None

        # 00:00인 경우는 사용자가 시간을 입력하지 않은 것으로 간주하여 None 반환
        if time_obj == time(0, 0):
            return None

        for start_str, end_str in TimeUtils.TIME_RANGES:
            start_time = time.fromisoformat(start_str)
            end_time = time.fromisoformat(end_str)

            if start_str == "23:00":
                if time_obj >= start_time or time_obj <= end_time:
                    return start_str, end_str
            else:
                if start_time <= time_obj <= end_time:
                    return start_str, end_str

        return None

    @staticmethod
    def range_to_time(time_range: Optional[Tuple[str, str]]) -> Optional[time]:
        """
        시간 범위를 time 객체로 변환 (앞 시간 기준)
        """
        if time_range is None:
            return None

        start_time_str = time_range[0]
        return time.fromisoformat(start_time_str)

    @staticmethod
    def is_valid_time_range(time_range: Optional[Tuple[str, str]]) -> bool:
        """
        시간 범위가 유효한지 검증
        """
        if time_range is None:
            return True

        if len(time_range) != 2:
            return False

        start_str, end_str = time_range

        # 정의된 시간 범위에 있는지 확인
        for defined_start, defined_end in TimeUtils.TIME_RANGES:
            if start_str == defined_start and end_str == defined_end:
                return True

        return False
