import traceback
from typing import List, Optional

from fastapi import Depends, HTTPException

from src.common.logger import logger
from src.hcx_client.client import HCXClient
from src.hcx_client.common.parser import Parser
from src.hcx_client.common.utils import HCXUtils
from src.lotto.entities.enums import SortType
from src.lotto.entities.schemas import (
    LottoDraw,
    LottoDrawList,
    LottoStatistic,
    LottoRecommendation,
    LottoRecommendationContent,
)
from src.lotto.repository import LottoRepository
from src.users.repository import UserRepository


class LottoService:
    def __init__(
        self,
        lotto_repository: LottoRepository = Depends(),
        user_repository: UserRepository = Depends(),
    ):

        self.lotto_repository = lotto_repository
        self.user_repository = user_repository

    async def get_lotto_draws(
        self, cursor: Optional[int] = None, limit: int = 10
    ) -> LottoDrawList:
        draws, next_cursor = await self.lotto_repository.get_lotto_draws(
            cursor=cursor, limit=limit
        )
        draw_list = [LottoDraw.model_validate(draw) for draw in draws]
        return LottoDrawList(draws=draw_list, next_cursor=next_cursor)

    async def get_lotto_statistics(
        self, sort_type: SortType = SortType.FREQUENCY, include_bonus: bool = True
    ) -> List[LottoStatistic]:
        statistics = await self.lotto_repository.get_lotto_statistics(
            sort_type=sort_type, include_bonus=include_bonus
        )

        # include_bonus에 따라 적절한 count 값 설정
        statistic_list = []
        for stat in statistics:
            count = stat.total_count if include_bonus else stat.main_count
            statistic_list.append(LottoStatistic(num=stat.num, count=count))

        return statistic_list

    async def create_lotto_recommendation(self, user_id: str) -> LottoRecommendation:
        """사용자별 로또 추천을 생성합니다."""
        # 1. 사용자 정보 조회 (사주 정보 포함)
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 2. 최신 로또 회차 조회
        latest_round = await self.lotto_repository.get_latest_round()
        if not latest_round:
            raise HTTPException(
                status_code=404, detail="로또 회차 정보를 찾을 수 없습니다."
            )

        # 3. 통계 데이터 조회
        frequent_nums = await self.lotto_repository.get_frequent_numbers(limit=10)
        infrequent_nums = await self.lotto_repository.get_excluded_numbers(limit=2)

        # 4. HCX API 호출하여 로또 추천 생성
        hcx_client = HCXClient()

        # 사용자 사주 정보 사용
        four_pillar = user.four_pillar
        lotto_prompt_data = {
            "year_pillar": four_pillar.get("year_pillar"),
            "month_pillar": four_pillar.get("month_pillar"),
            "day_pillar": four_pillar.get("day_pillar"),
            "time_pillar": four_pillar.get("time_pillar"),
            "strong_element": (
                four_pillar.get("strong_elements")[0]
                if four_pillar.get("strong_elements")
                else None
            ),
            "weak_element": (
                four_pillar.get("weak_elements")[0]
                if four_pillar.get("weak_elements")
                else None
            ),
        }

        # HCXUtils를 사용하여 프롬프트 가져오기
        system_prompt, user_prompt_template = HCXUtils.get_prompt_pair(
            "fortune.yaml", "lotto"
        )

        # 시스템 프롬프트에 통계 데이터 추가
        system_prompt = system_prompt.format(
            frequent_nums=",".join(map(str, frequent_nums)),
            excluded_nums=",".join(map(str, infrequent_nums)),
        )
        user_prompt = user_prompt_template.format(**lotto_prompt_data)

        try:
            response = await hcx_client.call_completion(
                system_prompt=system_prompt, user_prompt=user_prompt
            )

            # JSON 응답 파싱
            parsed_content = Parser.parse_json(response)

            content = LottoRecommendationContent(
                reason=parsed_content["reason"],
                num1=parsed_content["num1"],
                num2=parsed_content["num2"],
                num3=parsed_content["num3"],
                num4=parsed_content["num4"],
                num5=parsed_content["num5"],
                num6=parsed_content["num6"],
                cold_nums=parsed_content["cold_nums"],
                infrequent_nums=infrequent_nums,
                strong_element=lotto_prompt_data["strong_element"],
                weak_element=lotto_prompt_data["weak_element"],
            )

        except Exception as e:
            logger.info(f"로또 추천 생성 실패: {traceback.format_exc()}")
            raise HTTPException(
                status_code=400, detail=f"로또 추천 생성 실패: {str(e)}"
            )

        # 5. 데이터베이스에 저장
        recommendation = await self.lotto_repository.create_lotto_recommendation(
            user_id=user_id, round=latest_round + 1, content=content.model_dump()
        )

        return LottoRecommendation.model_validate(recommendation)

    async def get_lotto_recommendation(
        self, user_id: str
    ) -> Optional[LottoRecommendation]:
        """사용자의 최신 로또 추천을 조회합니다."""
        recommendation = (
            await self.lotto_repository.get_lotto_recommendation_by_user_id(user_id)
        )
        if recommendation:
            content = LottoRecommendationContent.model_validate(recommendation.content)
            return LottoRecommendation(
                id=recommendation.id,
                user_id=recommendation.user_id,
                round=recommendation.round,
                content=content,
                created_at=recommendation.created_at,
                updated_at=recommendation.updated_at
            )
        return None
