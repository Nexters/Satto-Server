from datetime import date, datetime
from typing import List, Optional

from src.four_pillars.domain.constants import BASE_YEAR, JIKKAN, JYUNISHI
from src.four_pillars.domain.entities.enums import FiveElements
from src.four_pillars.domain.entities.schemas import (
    FourPillar,
    FourPillarDetail,
)
from src.four_pillars.domain.services.analyzer import (
    FiveElementsAnalyzer,
    TenGodsAnalyzer,
)
from src.four_pillars.domain.services.data_loader import FourPillarsDataLoader


class FourPillarsCalculator:
    """사주 계산 클래스"""

    def __init__(self, description_generator=None):
        """
        Args:
            description_generator: 설명 생성기 (선택적). 제공되면 calculate_four_pillars_detailed에서 설명 생성
        """
        self.data_loader = FourPillarsDataLoader()
        self.five_elements_analyzer = FiveElementsAnalyzer()
        self.ten_gods_analyzer = TenGodsAnalyzer()
        self.description_generator = description_generator

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
        result: FourPillar = {
            "year_pillar": pillars[0],  # 년주
            "month_pillar": pillars[1],  # 월주
            "day_pillar": pillars[2],  # 일주
            "time_pillar": pillars[3],  # 시주
        }

        return result

    async def calculate_four_pillars_detailed(
        self, birth_date: datetime
    ) -> FourPillarDetail:
        """십신 정보를 포함한 상세한 사주 계산

        description_generator가 제공된 경우 설명을 생성하고,
        그렇지 않으면 description은 빈 문자열입니다.
        """
        # 기본 사주 계산
        basic_result = self.calculate_four_pillars(birth_date)

        # 일간 추출 (일주의 천간)
        day_stem = (
            basic_result["day_pillar"][0]
            if basic_result["day_pillar"]
            else "甲"
        )

        # 각 기둥의 상세 정보 생성
        year_pillar_detail = self.ten_gods_analyzer.get_pillar_detail(
            basic_result["year_pillar"], day_stem
        )
        month_pillar_detail = self.ten_gods_analyzer.get_pillar_detail(
            basic_result["month_pillar"], day_stem
        )
        day_pillar_detail = self.ten_gods_analyzer.get_pillar_detail(
            basic_result["day_pillar"], day_stem
        )
        time_pillar_detail = (
            self.ten_gods_analyzer.get_pillar_detail(
                basic_result["time_pillar"], day_stem
            )
            if basic_result["time_pillar"]
            else None
        )

        # 가장 강한 오행과 약한 오행
        strong_elements, weak_elements = self.five_elements_analyzer.analyze(
            [
                basic_result["year_pillar"],
                basic_result["month_pillar"],
                basic_result["day_pillar"],
                basic_result["time_pillar"],
            ]
        )

        # 기본값 설정
        strong_element = (
            strong_elements[0] if strong_elements else FiveElements.EARTH
        )
        weak_element = weak_elements[0] if weak_elements else FiveElements.WOOD

        # FourPillarDetail 객체 생성
        result = FourPillarDetail(
            strong_element=strong_element,
            weak_element=weak_element,
            description="",  # 기본값
            year_pillar_detail=year_pillar_detail,
            month_pillar_detail=month_pillar_detail,
            day_pillar_detail=day_pillar_detail,
            time_pillar_detail=time_pillar_detail,
        )

        # description_generator가 있으면 설명 생성
        if self.description_generator:
            description = await self.description_generator.generate(
                result, strong_element
            )
            result.description = description

        return result

    def _calculate_kanshi(
        self,
        year: int,
        month: int,
        day: int,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
    ) -> List[str]:
        """간지 계산"""
        # 절입일 계산
        setsuiri_day, setsuiri_hour, setsuiri_minute = (
            self.data_loader.get_setsuiri(year, month)
        )
        setsuiri_time = setsuiri_hour * 60 + setsuiri_minute

        # 년주 계산
        yd = year - BASE_YEAR
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
        year_pillar = self.data_loader.get_kanshi(yd)

        # 월주 계산
        md = (year - 1863) * 12 + (month - 12)
        if day < setsuiri_day or (
            day == setsuiri_day
            and (hour is None or hour * 60 + (minute or 0) < setsuiri_time)
        ):
            md -= 1
        month_pillar = self.data_loader.get_kanshi(md)

        # 일주 계산
        dd = (date(year, month, day) - date(1863, 12, 31)).days
        day_pillar = self.data_loader.get_kanshi(dd)

        if hour is not None and minute is not None:
            if hour == 23:
                jyunishi_idx = 0
            else:
                jyunishi_idx = (hour + 1) // 2

            jikkan_idx = (
                (JIKKAN.index(day_pillar[0]) % 5) * 2 + jyunishi_idx
            ) % 10
            time_pillar = JIKKAN[jikkan_idx] + JYUNISHI[jyunishi_idx]
        else:
            time_pillar = None

        return [year_pillar, month_pillar, day_pillar, time_pillar]
