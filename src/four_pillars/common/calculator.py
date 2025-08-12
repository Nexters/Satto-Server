from datetime import datetime, date
from pathlib import Path
from typing import List, Tuple, Dict
from collections import Counter

from src.four_pillars.entities.schemas import FourPillar, FourPillarDetail, PillarInfo
from src.four_pillars.entities.enums import FiveElements, TenGods


class FourPillarsCalculator:
    # 천간 (天干)
    JIKKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    # 지지 (地支)
    JYUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def __init__(self):
        self._init_kanshi_data()
        self._init_setsuiri_data()
        self._init_five_elements_mapping()
        self._init_ten_gods_mapping()


    def _init_five_elements_mapping(self):
        """천간과 지지의 오행 매핑 초기화"""
        # 천간 오행 매핑
        self.jikkan_five_elements = {
            "甲": FiveElements.WOOD,  # 갑 - 목
            "乙": FiveElements.WOOD,  # 을 - 목
            "丙": FiveElements.FIRE,  # 병 - 화
            "丁": FiveElements.FIRE,  # 정 - 화
            "戊": FiveElements.EARTH,  # 무 - 토
            "己": FiveElements.EARTH,  # 기 - 토
            "庚": FiveElements.METAL,  # 경 - 금
            "辛": FiveElements.METAL,  # 신 - 금
            "壬": FiveElements.WATER,  # 임 - 수
            "癸": FiveElements.WATER,  # 계 - 수
        }

        # 지지 오행 매핑
        self.jyunishi_five_elements = {
            "寅": FiveElements.WOOD,  # 인 - 목
            "卯": FiveElements.WOOD,  # 묘 - 목
            "巳": FiveElements.FIRE,  # 사 - 화
            "午": FiveElements.FIRE,  # 오 - 화
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

    def _analyze_five_elements(
        self, pillars: List[str]
    ) -> Tuple[List[FiveElements], List[FiveElements]]:
        """사주팔자의 오행 분석"""
        element_counts = Counter()

        # 모든 오행을 0으로 초기화
        all_elements = [
            FiveElements.WOOD,
            FiveElements.FIRE,
            FiveElements.EARTH,
            FiveElements.METAL,
            FiveElements.WATER,
        ]
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

        strong_elements = [
            element for element, count in element_counts.items() if count == max_count
        ]
        weak_elements = [
            element for element, count in element_counts.items() if count == min_count
        ]

        return strong_elements, weak_elements

    def _init_ten_gods_mapping(self):
        """십신 매핑 초기화"""
        # 일간(日干)을 기준으로 한 십신 매핑
        # 각 천간에 대해 다른 천간과의 관계를 십신으로 매핑
        self.ten_gods_mapping = {
            "甲": {  # 갑(甲)을 일간으로 할 때
                "甲": TenGods.COMPARISON,  # 갑-갑: 비견
                "乙": TenGods.COMPETITOR,  # 갑-을: 겁재
                "丙": TenGods.EATING,  # 갑-병: 식신
                "丁": TenGods.HURTING,  # 갑-정: 상관
                "戊": TenGods.PARTIAL_WEALTH,  # 갑-무: 편재
                "己": TenGods.DIRECT_WEALTH,  # 갑-기: 정재
                "庚": TenGods.PARTIAL_OFFICIAL,  # 갑-경: 편관
                "辛": TenGods.DIRECT_OFFICIAL,  # 갑-신: 정관
                "壬": TenGods.PARTIAL_PRINT,  # 갑-임: 편인
                "癸": TenGods.DIRECT_PRINT,  # 갑-계: 정인
            },
            "乙": {  # 을(乙)을 일간으로 할 때
                "甲": TenGods.COMPETITOR,  # 을-갑: 겁재
                "乙": TenGods.COMPARISON,  # 을-을: 비견
                "丙": TenGods.HURTING,  # 을-병: 상관
                "丁": TenGods.EATING,  # 을-정: 식신
                "戊": TenGods.DIRECT_WEALTH,  # 을-무: 정재
                "己": TenGods.PARTIAL_WEALTH,  # 을-기: 편재
                "庚": TenGods.DIRECT_OFFICIAL,  # 을-경: 정관
                "辛": TenGods.PARTIAL_OFFICIAL,  # 을-신: 편관
                "壬": TenGods.DIRECT_PRINT,  # 을-임: 정인
                "癸": TenGods.PARTIAL_PRINT,  # 을-계: 편인
            },
            "丙": {  # 병(丙)을 일간으로 할 때
                "甲": TenGods.PARTIAL_PRINT,  # 병-갑: 편인
                "乙": TenGods.DIRECT_PRINT,  # 병-을: 정인
                "丙": TenGods.COMPARISON,  # 병-병: 비견
                "丁": TenGods.COMPETITOR,  # 병-정: 겁재
                "戊": TenGods.EATING,  # 병-무: 식신
                "己": TenGods.HURTING,  # 병-기: 상관
                "庚": TenGods.PARTIAL_WEALTH,  # 병-경: 편재
                "辛": TenGods.DIRECT_WEALTH,  # 병-신: 정재
                "壬": TenGods.PARTIAL_OFFICIAL,  # 병-임: 편관
                "癸": TenGods.DIRECT_OFFICIAL,  # 병-계: 정관
            },
            "丁": {  # 정(丁)을 일간으로 할 때
                "甲": TenGods.DIRECT_PRINT,  # 정-갑: 정인
                "乙": TenGods.PARTIAL_PRINT,  # 정-을: 편인
                "丙": TenGods.COMPETITOR,  # 정-병: 겁재
                "丁": TenGods.COMPARISON,  # 정-정: 비견
                "戊": TenGods.HURTING,  # 정-무: 상관
                "己": TenGods.EATING,  # 정-기: 식신
                "庚": TenGods.DIRECT_WEALTH,  # 정-경: 정재
                "辛": TenGods.PARTIAL_WEALTH,  # 정-신: 편재
                "壬": TenGods.DIRECT_OFFICIAL,  # 정-임: 정관
                "癸": TenGods.PARTIAL_OFFICIAL,  # 정-계: 편관
            },
            "戊": {  # 무(戊)를 일간으로 할 때
                "甲": TenGods.PARTIAL_OFFICIAL,  # 무-갑: 편관
                "乙": TenGods.DIRECT_OFFICIAL,  # 무-을: 정관
                "丙": TenGods.PARTIAL_PRINT,  # 무-병: 편인
                "丁": TenGods.DIRECT_PRINT,  # 무-정: 정인
                "戊": TenGods.COMPARISON,  # 무-무: 비견
                "己": TenGods.COMPETITOR,  # 무-기: 겁재
                "庚": TenGods.EATING,  # 무-경: 식신
                "辛": TenGods.HURTING,  # 무-신: 상관
                "壬": TenGods.PARTIAL_WEALTH,  # 무-임: 편재
                "癸": TenGods.DIRECT_WEALTH,  # 무-계: 정재
            },
            "己": {  # 기(己)를 일간으로 할 때
                "甲": TenGods.DIRECT_OFFICIAL,  # 기-갑: 정관
                "乙": TenGods.PARTIAL_OFFICIAL,  # 기-을: 편관
                "丙": TenGods.DIRECT_PRINT,  # 기-병: 정인
                "丁": TenGods.PARTIAL_PRINT,  # 기-정: 편인
                "戊": TenGods.COMPETITOR,  # 기-무: 겁재
                "己": TenGods.COMPARISON,  # 기-기: 비견
                "庚": TenGods.HURTING,  # 기-경: 상관
                "辛": TenGods.EATING,  # 기-신: 식신
                "壬": TenGods.DIRECT_WEALTH,  # 기-임: 정재
                "癸": TenGods.PARTIAL_WEALTH,  # 기-계: 편재
            },
            "庚": {  # 경(庚)을 일간으로 할 때
                "甲": TenGods.DIRECT_WEALTH,  # 경-갑: 정재
                "乙": TenGods.PARTIAL_WEALTH,  # 경-을: 편재
                "丙": TenGods.PARTIAL_OFFICIAL,  # 경-병: 편관
                "丁": TenGods.DIRECT_OFFICIAL,  # 경-정: 정관
                "戊": TenGods.PARTIAL_PRINT,  # 경-무: 편인
                "己": TenGods.DIRECT_PRINT,  # 경-기: 정인
                "庚": TenGods.COMPARISON,  # 경-경: 비견
                "辛": TenGods.COMPETITOR,  # 경-신: 겁재
                "壬": TenGods.EATING,  # 경-임: 식신
                "癸": TenGods.HURTING,  # 경-계: 상관
            },
            "辛": {  # 신(辛)을 일간으로 할 때
                "甲": TenGods.PARTIAL_WEALTH,  # 신-갑: 편재
                "乙": TenGods.DIRECT_WEALTH,  # 신-을: 정재
                "丙": TenGods.DIRECT_OFFICIAL,  # 신-병: 정관
                "丁": TenGods.PARTIAL_OFFICIAL,  # 신-정: 편관
                "戊": TenGods.DIRECT_PRINT,  # 신-무: 정인
                "己": TenGods.PARTIAL_PRINT,  # 신-기: 편인
                "庚": TenGods.COMPETITOR,  # 신-경: 겁재
                "辛": TenGods.COMPARISON,  # 신-신: 비견
                "壬": TenGods.HURTING,  # 신-임: 상관
                "癸": TenGods.EATING,  # 신-계: 식신
            },
            "壬": {  # 임(壬)을 일간으로 할 때
                "甲": TenGods.EATING,  # 임-갑: 식신
                "乙": TenGods.HURTING,  # 임-을: 상관
                "丙": TenGods.PARTIAL_WEALTH,  # 임-병: 편재
                "丁": TenGods.DIRECT_WEALTH,  # 임-정: 정재
                "戊": TenGods.PARTIAL_OFFICIAL,  # 임-무: 편관
                "己": TenGods.DIRECT_OFFICIAL,  # 임-기: 정관
                "庚": TenGods.PARTIAL_PRINT,  # 임-경: 편인
                "辛": TenGods.DIRECT_PRINT,  # 임-신: 정인
                "壬": TenGods.COMPARISON,  # 임-임: 비견
                "癸": TenGods.COMPETITOR,  # 임-계: 겁재
            },
            "癸": {  # 계(癸)를 일간으로 할 때
                "甲": TenGods.HURTING,  # 계-갑: 상관
                "乙": TenGods.EATING,  # 계-을: 식신
                "丙": TenGods.DIRECT_WEALTH,  # 계-병: 정재
                "丁": TenGods.PARTIAL_WEALTH,  # 계-정: 편재
                "戊": TenGods.DIRECT_OFFICIAL,  # 계-무: 정관
                "己": TenGods.PARTIAL_OFFICIAL,  # 계-기: 편관
                "庚": TenGods.DIRECT_PRINT,  # 계-경: 정인
                "辛": TenGods.PARTIAL_PRINT,  # 계-신: 편인
                "壬": TenGods.COMPETITOR,  # 계-임: 겁재
                "癸": TenGods.COMPARISON,  # 계-계: 비견
            },
        }

    def _get_ten_god(self, day_stem: str, target_stem: str) -> TenGods:
        """일간을 기준으로 특정 천간의 십신을 구함"""
        if (
            day_stem in self.ten_gods_mapping
            and target_stem in self.ten_gods_mapping[day_stem]
        ):
            return self.ten_gods_mapping[day_stem][target_stem]
        else:
            # 기본값으로 비견 반환 (같은 천간일 때)
            return TenGods.COMPARISON

    def _get_pillar_detail(self, pillar: str, day_stem: str) -> PillarInfo:
        """각 기둥의 상세 정보를 생성"""
        if not pillar or len(pillar) != 2:
            return None

        heavenly_stem = pillar[0]  # 천간
        earthly_branch = pillar[1]  # 지지

        # 천간의 십신과 오행
        heavenly_stem_ten_god = self._get_ten_god(day_stem, heavenly_stem)
        heavenly_stem_element = self.jikkan_five_elements.get(
            heavenly_stem, FiveElements.EARTH
        )

        # 지지의 십신 (지지의 숨겨진 천간을 기준으로 계산)
        hidden_stem = self._get_hidden_stem(earthly_branch)
        earthly_branch_ten_god = self._get_ten_god(day_stem, hidden_stem)
        earthly_branch_element = self.jyunishi_five_elements.get(
            earthly_branch, FiveElements.EARTH
        )

        return PillarInfo(
            stem=heavenly_stem,
            branch=earthly_branch,
            stem_ten_god=heavenly_stem_ten_god,
            branch_ten_god=earthly_branch_ten_god,
            stem_element=heavenly_stem_element,
            branch_element=earthly_branch_element,
        )

    def _get_hidden_stem(self, earthly_branch: str) -> str:
        """지지의 숨겨진 천간을 구함"""
        # 지지별 숨겨진 천간 (장간, 중간, 단간)
        hidden_stems = {
            "子": "癸",  # 자수에 숨겨진 천간: 계수
            "丑": "己",  # 축토에 숨겨진 천간: 기토
            "寅": "甲",  # 인목에 숨겨진 천간: 갑목
            "卯": "乙",  # 묘목에 숨겨진 천간: 을목
            "辰": "戊",  # 진토에 숨겨진 천간: 무토
            "巳": "丙",  # 사화에 숨겨진 천간: 병화
            "午": "丁",  # 오화에 숨겨진 천간: 정화
            "未": "己",  # 미토에 숨겨진 천간: 기토
            "申": "庚",  # 신금에 숨겨진 천간: 경금
            "酉": "辛",  # 유금에 숨겨진 천간: 신금
            "戌": "戊",  # 술토에 숨겨진 천간: 무토
            "亥": "壬",  # 해수에 숨겨진 천간: 임수
        }
        return hidden_stems.get(earthly_branch, "甲")

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
        result: FourPillar = {
            "year_pillar": pillars[0],  # 년주
            "month_pillar": pillars[1],  # 월주
            "day_pillar": pillars[2],  # 일주
            "time_pillar": pillars[3],  # 시주
            "strong_elements": strong_elements,
            "weak_elements": weak_elements,
        }

        return result

    def calculate_four_pillars_detailed(self, birth_date: datetime) -> FourPillarDetail:
        """십신 정보를 포함한 상세한 사주 계산"""
        # 기본 사주 계산
        basic_result = self.calculate_four_pillars(birth_date)

        # 일간 추출 (일주의 천간)
        day_stem = basic_result["day_pillar"][0] if basic_result["day_pillar"] else "甲"

        # 각 기둥의 상세 정보 생성
        year_pillar_detail = self._get_pillar_detail(
            basic_result["year_pillar"], day_stem
        )
        month_pillar_detail = self._get_pillar_detail(
            basic_result["month_pillar"], day_stem
        )
        day_pillar_detail = self._get_pillar_detail(
            basic_result["day_pillar"], day_stem
        )
        time_pillar_detail = (
            self._get_pillar_detail(basic_result["time_pillar"], day_stem)
            if basic_result["time_pillar"]
            else None
        )

        # 가장 강한 오행과 약한 오행
        strong_elements, weak_elements = self._analyze_five_elements(
            [
                basic_result["year_pillar"],
                basic_result["month_pillar"],
                basic_result["day_pillar"],
                basic_result["time_pillar"],
            ]
        )

        # 기본값 설정
        strong_element = strong_elements[0] if strong_elements else FiveElements.EARTH
        weak_element = weak_elements[0] if weak_elements else FiveElements.WOOD

        # 종합 설명 생성
        description = "근심과 즐거움이 상반하니 세월의 흐름을 잘 읽어보시게"

        return FourPillarDetail(
            strong_element=strong_element,
            weak_element=weak_element,
            description=description,
            year_pillar_detail=year_pillar_detail,
            month_pillar_detail=month_pillar_detail,
            day_pillar_detail=day_pillar_detail,
            time_pillar_detail=time_pillar_detail,
        )
