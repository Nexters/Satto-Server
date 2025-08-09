from datetime import datetime, date
from pathlib import Path
from typing import List, Tuple, Dict
from collections import Counter

from src.four_pillars.entities.schemas import FourPillar, FiveElements


class FourPillarsCalculator:
    # 천간 (天干)
    JIKKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    # 지지 (地支)
    JYUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def __init__(self):
        self._init_kanshi_data()
        self._init_setsuiri_data()
        self._init_five_elements_mapping()

    def _init_five_elements_mapping(self):
        """천간과 지지의 오행 매핑 초기화"""
        # 천간 오행 매핑
        self.jikkan_five_elements = {
            "甲": FiveElements.WOOD,   # 갑 - 목
            "乙": FiveElements.WOOD,   # 을 - 목
            "丙": FiveElements.FIRE,   # 병 - 화
            "丁": FiveElements.FIRE,   # 정 - 화
            "戊": FiveElements.EARTH,  # 무 - 토
            "己": FiveElements.EARTH,  # 기 - 토
            "庚": FiveElements.METAL,  # 경 - 금
            "辛": FiveElements.METAL,  # 신 - 금
            "壬": FiveElements.WATER,  # 임 - 수
            "癸": FiveElements.WATER,  # 계 - 수
        }
        
        # 지지 오행 매핑
        self.jyunishi_five_elements = {
            "寅": FiveElements.WOOD,   # 인 - 목
            "卯": FiveElements.WOOD,   # 묘 - 목
            "巳": FiveElements.FIRE,   # 사 - 화
            "午": FiveElements.FIRE,   # 오 - 화
            "辰": FiveElements.EARTH,  # 진 - 토
            "戌": FiveElements.EARTH,  # 술 - 토
            "丑": FiveElements.EARTH,  # 축 - 토
            "未": FiveElements.EARTH,  # 미 - 토
            "申": FiveElements.METAL,  # 신 - 금
            "酉": FiveElements.METAL,  # 유 - 금
            "亥": FiveElements.WATER,  # 해 - 수
            "子": FiveElements.WATER,  # 자 - 수
        }

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

    def _analyze_five_elements(self, pillars: List[str]) -> Tuple[List[FiveElements], List[FiveElements]]:
        """사주팔자의 오행 분석"""
        element_counts = Counter()
        
        # 모든 오행을 0으로 초기화
        all_elements = [FiveElements.WOOD, FiveElements.FIRE, FiveElements.EARTH, FiveElements.METAL, FiveElements.WATER]
        for element in all_elements:
            element_counts[element] = 0
        
        for pillar in pillars:
            if pillar is None:
                continue
                
            # 천간과 지지 분리
            jikkan = pillar[0]  # 첫 번째 글자는 천간
            jyunishi = pillar[1]  # 두 번째 글자는 지지
            
            # 천간 오행 추가
            if jikkan in self.jikkan_five_elements:
                element_counts[self.jikkan_five_elements[jikkan]] += 1
            
            # 지지 오행 추가
            if jyunishi in self.jyunishi_five_elements:
                element_counts[self.jyunishi_five_elements[jyunishi]] += 1
        
        # 가장 많은 오행과 가장 적은 오행 찾기
        max_count = max(element_counts.values())
        min_count = min(element_counts.values())
        
        strong_elements = [element for element, count in element_counts.items() if count == max_count]
        weak_elements = [element for element, count in element_counts.items() if count == min_count]
        
        return strong_elements, weak_elements

    def calculate_four_pillars(self, birth_date: datetime) -> FourPillar:
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
        
        # 오행 분석
        strong_elements, weak_elements = self._analyze_five_elements(pillars)
        
        # FiveElements enum을 문자열로 변환
        strong_elements_str = [element.value for element in strong_elements] if strong_elements else None
        weak_elements_str = [element.value for element in weak_elements] if weak_elements else None
        
        result: FourPillar = {
            "year_pillar": pillars[0],  # 년주
            "month_pillar": pillars[1],  # 월주
            "day_pillar": pillars[2],  # 일주
            "time_pillar": pillars[3], # 시주
            "strong_elements": strong_elements_str,
            "weak_elements": weak_elements_str
        }

        return result
