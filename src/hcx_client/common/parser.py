import re
from src.hcx_client.entities.schemas import FourPillarResponse


class Parser:
    @staticmethod
    def parse_four_pillar(content: str) -> FourPillarResponse:
        pattern = (
            r"년주:\s*([^\n]+)\n"
            r"월주:\s*([^\n]+)\n"
            r"일주:\s*([^\n]+)\n"
            r"시주:\s*([^\n]+)\n\n?"
            r"사주 해석:\s*([\s\S]+)"
        )
        match = re.search(pattern, content, re.DOTALL)
        if match:
            year, month, day, time, interp = match.groups()
            return FourPillarResponse(
                year_pillar=year.strip(),
                month_pillar=month.strip(),
                day_pillar=day.strip(),
                time_pillar=time.strip(),
                interpretation=interp.strip(),
            )

        # 일부만 추출하는 경우
        def extract(key):
            m = re.search(rf"{key}:\s*([^\n]+)", content)
            return m.group(1).strip() if m else None

        return FourPillarResponse(
            year_pillar=extract("년주"),
            month_pillar=extract("월주"),
            day_pillar=extract("일주"),
            time_pillar=extract("시주"),
            interpretation=extract("사주 해석"),
        )
