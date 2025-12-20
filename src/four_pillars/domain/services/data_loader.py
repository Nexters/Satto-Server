from pathlib import Path
from typing import Tuple

from src.four_pillars.domain.constants import JIKKAN, JYUNISHI


class FourPillarsDataLoader:
    """사주 계산에 필요한 데이터를 로드하는 클래스"""

    def __init__(self):
        self.kanshi_array: list[str] = []
        self.setsuiri_data: dict[int, Tuple[int, int]] = {}
        self._init_kanshi_data()
        self._init_setsuiri_data()

    def _init_kanshi_data(self):
        """60간지 배열 초기화"""
        self.kanshi_array = []
        for i in range(60):
            j1 = JIKKAN[i % 10]
            j2 = JYUNISHI[i % 12]
            self.kanshi_array.append(j1 + j2)
    def _init_setsuiri_data(self):
        """절입 데이터 초기화"""
        self.setsuiri_data = {}

        # four_pillars 패키지의 static 폴더에서 파일 읽기
        package_dir = Path(__file__).parent.parent.parent
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

    def get_setsuiri(self, year: int, month: int) -> Tuple[int, int, int]:
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

    def get_kanshi(self, index: int) -> str:
        """간지 배열에서 인덱스로 간지 가져오기"""
        return self.kanshi_array[index % 60]

