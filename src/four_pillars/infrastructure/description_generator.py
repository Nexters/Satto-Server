from src.four_pillars.api.schemas import FourPillarDetail
from src.four_pillars.domain.entities.enums import FiveElements
from src.hcx_client.client import HCXClient
from src.hcx_client.common.utils import HCXUtils


class FourPillarDescriptionGenerator:
    """사주 설명 생성 클래스 (HCX API 호출)"""

    async def generate(
        self, four_pillar_detail: FourPillarDetail, strong_element: FiveElements
    ) -> str:
        """HCX API를 호출하여 사주 설명을 생성합니다."""
        try:
            hcx_client = HCXClient()

            # FourPillarDetail에서 사주 정보 추출
            year_pillar = ""
            month_pillar = ""
            day_pillar = ""
            time_pillar = ""

            if four_pillar_detail.year_pillar_detail:
                year_pillar = (
                    f"{four_pillar_detail.year_pillar_detail.stem}"
                    f"{four_pillar_detail.year_pillar_detail.branch}"
                )

            if four_pillar_detail.month_pillar_detail:
                month_pillar = (
                    f"{four_pillar_detail.month_pillar_detail.stem}"
                    f"{four_pillar_detail.month_pillar_detail.branch}"
                )

            if four_pillar_detail.day_pillar_detail:
                day_pillar = (
                    f"{four_pillar_detail.day_pillar_detail.stem}"
                    f"{four_pillar_detail.day_pillar_detail.branch}"
                )

            if four_pillar_detail.time_pillar_detail:
                time_pillar = (
                    f"{four_pillar_detail.time_pillar_detail.stem}"
                    f"{four_pillar_detail.time_pillar_detail.branch}"
                )

            # 사주 정보 준비
            four_pillar_data = {
                "year_pillar": year_pillar,
                "month_pillar": month_pillar,
                "day_pillar": day_pillar,
                "time_pillar": time_pillar,
                "strong_element": strong_element.value,
            }

            # HCXUtils를 사용하여 프롬프트 가져오기
            system_prompt, user_prompt_template = HCXUtils.get_prompt_pair(
                "fortune.yaml", "four_pillar"
            )

            user_prompt = user_prompt_template.format(**four_pillar_data)

            # HCX API 호출
            response = await hcx_client.call_completion(
                system_prompt=system_prompt, user_prompt=user_prompt
            )

            return response.strip()

        except Exception:
            # API 호출 실패 시 기본 설명 반환
            return "근심과 즐거움이 상반하니 세월의 흐름을 잘 읽어보시게"
