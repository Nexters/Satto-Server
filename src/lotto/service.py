import traceback
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import httpx
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

    async def fetch_lotto_data_from_api(self, drw_no: int) -> Optional[Dict[str, Any]]:
        """동행복권 API에서 특정 회차의 로또 데이터를 가져옵니다."""
        base_url = "https://www.dhlottery.co.kr/common.do"
        params = {
            "method": "getLottoNumber",
            "drwNo": drw_no
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("returnValue") == "success":
                        return data
                    else:
                        logger.warning(f"회차 {drw_no}: API 응답 오류 - {data}")
                        return None
                else:
                    logger.warning(f"회차 {drw_no}: HTTP 오류 - {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"회차 {drw_no}: 요청 오류 - {e}")
            return None

    def parse_lotto_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """API 응답 데이터를 데이터베이스 모델에 맞게 파싱합니다."""
        return {
            "round": data["drwNo"],
            "draw_date": datetime.strptime(data["drwNoDate"], "%Y-%m-%d").date(),
            "num1": data["drwtNo1"],
            "num2": data["drwtNo2"],
            "num3": data["drwtNo3"],
            "num4": data["drwtNo4"],
            "num5": data["drwtNo5"],
            "num6": data["drwtNo6"],
            "bonus_num": data["bnusNo"],
            "first_prize_amount": data["firstWinamnt"],
            "total_winners": data["firstPrzwnerCo"]
        }

    async def update_next_lotto_draw(self) -> bool:
        """가장 최신 회차 다음 회차의 로또 데이터를 가져와서 저장합니다."""
        try:
            # 1. 현재 데이터베이스의 최신 회차 조회
            latest_round = await self.lotto_repository.get_latest_round()
            if not latest_round:
                logger.error("데이터베이스에 로또 회차 정보가 없습니다.")
                return False
            
            next_round = latest_round + 1
            logger.info(f"다음 회차 {next_round} 데이터 조회 시작")
            
            # 2. 이미 존재하는지 확인
            existing_draw = await self.lotto_repository.get_lotto_draw_by_round(next_round)
            if existing_draw:
                logger.info(f"회차 {next_round}: 이미 존재함")
                return True
            
            # 3. API에서 데이터 가져오기
            api_data = await self.fetch_lotto_data_from_api(next_round)
            if not api_data:
                logger.warning(f"회차 {next_round}: API에서 데이터를 가져올 수 없음")
                return False
            
            # 4. 데이터 파싱
            lotto_data = self.parse_lotto_data(api_data)
            
            # 5. 데이터베이스에 저장
            await self.lotto_repository.create_lotto_draw(lotto_data)
            
            # 6. 통계 업데이트
            await self.lotto_repository.update_lotto_statistics(lotto_data)
            
            logger.info(f"회차 {next_round}: 데이터 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"다음 회차 로또 데이터 업데이트 실패: {e}")
            return False

    def _get_current_lotto_period(self) -> tuple[datetime, datetime]:
        """
        현재 시간 기준으로 로또 추천 유효 기간을 계산합니다.
        지난 토요일 오후 9시(21시)부터 이번주 토요일 오후 9시 전까지
        """
        # 한국 시간대 (UTC+9)
        KST_OFFSET = timedelta(hours=9)
        
        # 현재 UTC 시간을 한국 시간으로 변환
        now_utc = datetime.utcnow()
        now_kst = now_utc + KST_OFFSET
        
        # 이번 주 토요일 오후 9시(21시) 계산
        days_until_saturday = (5 - now_kst.weekday()) % 7  # 5 = 토요일
        
        this_saturday_9pm = now_kst.replace(
            hour=21, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_until_saturday)
        
        # 지난 토요일 오후 9시(21시) 계산
        last_saturday_9pm = this_saturday_9pm - timedelta(days=7)
        
        return last_saturday_9pm, this_saturday_9pm

    async def get_lotto_draws(
        self, user_id: Optional[str] = None, cursor: Optional[int] = None, limit: int = 10
    ) -> LottoDrawList:
        draws, next_cursor = await self.lotto_repository.get_lotto_draws(
            user_id=user_id, cursor=cursor, limit=limit
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
            "strong_element": four_pillar.get("strong_element"),
            "weak_element": four_pillar.get("weak_element"),
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

        # 6. 데이터베이스에 저장
        recommendation = await self.lotto_repository.create_lotto_recommendation(
            user_id=user_id, round=latest_round + 1, content=content.model_dump()
        )

        return LottoRecommendation.model_validate(recommendation)

    async def get_lotto_recommendation(
        self, user_id: str
    ) -> Optional[LottoRecommendation]:
        """사용자의 최신 로또 추천을 조회합니다."""
        # 로또 추천 유효 기간 계산
        start_time, end_time = self._get_current_lotto_period()

        # 유효 기간 내에서만 추천 조회
        recommendation = (
            await self.lotto_repository.get_lotto_recommendation_by_user_id(
                user_id, start_time, end_time
            )
        )

        if recommendation:
            content = LottoRecommendationContent.model_validate(recommendation.content)
            return LottoRecommendation(
                user_id=recommendation.user_id,
                round=recommendation.round,
                content=content,
            )
        else:
            latest_round = await self.lotto_repository.get_latest_round()
            next_round = (latest_round or 0) + 1
            return LottoRecommendation(
                user_id=user_id,
                round=next_round,
                content=None,
            )
