from datetime import datetime, date
from pathlib import Path
from typing import List, Tuple, Dict


class FourPillarsCalculator:
    # 천간 (天干)
    JIKKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    # 지지 (地支)
    JYUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def __init__(self):
        self._init_kanshi_data()
        self._init_setsuiri_data()

    def _init_kanshi_data(self):
        """60간지 배열과 해시 초기화"""
        self.kanshi_array = []
        for i in range(60):
            j1 = self.JIKKAN[i % 10]
            j2 = self.JYUNISHI[i % 12]
            self.kanshi_array.append(j1 + j2)

        self.kanshi_hash = {}
        for i, v in enumerate(self.kanshi_array):
            self.kanshi_hash[v] = i + 1

    def _init_setsuiri_data(self):
        """절입 데이터 초기화"""
        self.setsuiri_data = {}

        # four_pillars 패키지의 static 폴더에서 파일 읽기
        package_dir = Path(__file__).parent.parent
        setsuiri_file = package_dir / "static" / "solar_terms.txt"

        with open(setsuiri_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    if len(parts) >= 5:
                        year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                        hour = int(parts[3])
                        minute = int(parts[4])

                        key = year * 100 + month
                        self.setsuiri_data[key] = (day, hour * 60 + minute)

    def _get_setsuiri(self, year: int, month: int) -> Tuple[int, int]:
        """절입일과 절입시 계산"""
        key = year * 100 + month

        if key in self.setsuiri_data:
            day, time_minutes = self.setsuiri_data[key]
            hour = time_minutes // 60
            minute = time_minutes % 60
            return (day, hour, minute)
        else:
            # four-pillars 라이브러리와 동일한 기본값 사용
            return (4, 12, 0)  # 4일 12시 0분

    def _calculate_kanshi(
        self, year: int, month: int, day: int, hour: int = None, minute: int = None
    ) -> List[str]:
        # 1864년을 기준으로 한 계산
        base_year = 1864

        # 절입일 계산
        setsuiri_day, setsuiri_hour, setsuiri_minute = self._get_setsuiri(year, month)
        setsuiri_time = setsuiri_hour * 60 + setsuiri_minute

        # 년주 계산
        yd = year - base_year
        if (
            month < 2
            or (month == 2 and day < setsuiri_day)
            or (
                month == 2
                and day == setsuiri_day
                and (hour is None or hour * 60 + (minute or 0) < setsuiri_time)
            )
        ):
            yd -= 1
        year_pillar = self.kanshi_array[yd % 60]

        # 월주 계산
        md = (year - 1863) * 12 + (month - 12)
        if day < setsuiri_day or (
            day == setsuiri_day
            and (hour is None or hour * 60 + (minute or 0) < setsuiri_time)
        ):
            md -= 1
        month_pillar = self.kanshi_array[md % 60]

        # 일주 계산
        dd = (date(year, month, day) - date(1863, 12, 31)).days
        day_pillar = self.kanshi_array[dd % 60]

        if hour is not None and minute is not None:
            if hour == 23:
                jyunishi_idx = 0
            else:
                jyunishi_idx = (hour + 1) // 2

            jikkan_idx = (
                (self.JIKKAN.index(day_pillar[0]) % 5) * 2 + jyunishi_idx
            ) % 10
            time_pillar = self.JIKKAN[jikkan_idx] + self.JYUNISHI[jyunishi_idx]
        else:
            time_pillar = None

        return [year_pillar, month_pillar, day_pillar, time_pillar]

    def calculate_four_pillars(self, birth_date: datetime) -> Dict[str, str]:
        """사주 계산 메인 함수"""
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day

        if birth_date.hour != 0 or birth_date.minute != 0:
            hour = birth_date.hour
            minute = birth_date.minute
        else:
            hour = None
            minute = None

        pillars = self._calculate_kanshi(year, month, day, hour, minute)
        result = {
            "year_pillar": pillars[0],  # 년주
            "month_pillar": pillars[1],  # 월주
            "day_pillar": pillars[2],  # 일주
        }

        if pillars[3] is not None:
            result["time_pillar"] = pillars[3]

        return result
