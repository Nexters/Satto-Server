from collections import Counter
from typing import List, Tuple

from src.four_pillars.domain.entities.enums import FiveElements, TenGods
from src.four_pillars.domain.entities.schemas import PillarInfo


class FiveElementsAnalyzer:
    """오행 분석 클래스"""

    # 천간 오행 매핑
    JIKKAN_FIVE_ELEMENTS = {
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
    JYUNISHI_FIVE_ELEMENTS = {
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

    def analyze(self, pillars: List[str]) -> Tuple[List[FiveElements], List[FiveElements]]:
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
            if jikkan in self.JIKKAN_FIVE_ELEMENTS:
                element_counts[self.JIKKAN_FIVE_ELEMENTS[jikkan]] += 1

            # 지지 오행 추가
            if jyunishi in self.JYUNISHI_FIVE_ELEMENTS:
                element_counts[self.JYUNISHI_FIVE_ELEMENTS[jyunishi]] += 1

        # 가장 많은 오행과 가장 적은 오행 찾기
        max_count = max(element_counts.values())
        min_count = min(element_counts.values())

        strong_elements = [
            element
            for element, count in element_counts.items()
            if count == max_count
        ]
        weak_elements = [
            element
            for element, count in element_counts.items()
            if count == min_count
        ]

        return strong_elements, weak_elements


class TenGodsAnalyzer:
    """십신 분석 클래스"""

    # 일간(日干)을 기준으로 한 십신 매핑
    TEN_GODS_MAPPING = {
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

    # 지지별 숨겨진 천간 (장간)
    HIDDEN_STEMS = {
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

    def get_ten_god(self, day_stem: str, target_stem: str) -> TenGods:
        """일간을 기준으로 특정 천간의 십신을 구함"""
        if (
            day_stem in self.TEN_GODS_MAPPING
            and target_stem in self.TEN_GODS_MAPPING[day_stem]
        ):
            return self.TEN_GODS_MAPPING[day_stem][target_stem]
        else:
            # 기본값으로 비견 반환 (같은 천간일 때)
            return TenGods.COMPARISON

    def get_hidden_stem(self, earthly_branch: str) -> str:
        """지지의 숨겨진 천간을 구함"""
        return self.HIDDEN_STEMS.get(earthly_branch, "甲")

    def get_pillar_detail(self, pillar: str, day_stem: str) -> PillarInfo | None:
        """각 기둥의 상세 정보를 생성"""
        if not pillar or len(pillar) != 2:
            return None

        heavenly_stem = pillar[0]  # 천간
        earthly_branch = pillar[1]  # 지지

        # 천간의 십신
        heavenly_stem_ten_god = self.get_ten_god(day_stem, heavenly_stem)

        # 지지의 십신 (지지의 숨겨진 천간을 기준으로 계산)
        hidden_stem = self.get_hidden_stem(earthly_branch)
        earthly_branch_ten_god = self.get_ten_god(day_stem, hidden_stem)

        return PillarInfo(
            stem=heavenly_stem,
            branch=earthly_branch,
            stem_ten_god=heavenly_stem_ten_god,
            branch_ten_god=earthly_branch_ten_god,
        )

