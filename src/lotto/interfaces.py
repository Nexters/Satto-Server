from datetime import datetime
from typing import Protocol

from src.lotto.entities.enums import SortType
from src.lotto.entities.models import (
    LottoDraws,
    LottoRecommendations,
    LottoStatistics,
)


class ILottoRepository(Protocol):
    """로또 리포지토리 인터페이스"""

    async def get_lotto_draws(
        self,
        user_id: str | None = None,
        cursor: int | None = None,
        limit: int = 10,
    ) -> tuple[list[LottoDraws], int | None]:
        """로또 추첨 데이터 목록을 조회합니다."""
        ...

    async def get_lotto_statistics(
        self,
        sort_type: SortType = SortType.FREQUENCY,
        include_bonus: bool = True,
    ) -> list[LottoStatistics]:
        """로또 통계 데이터를 조회합니다."""
        ...

    async def get_latest_round(self) -> int | None:
        """가장 최신 로또 회차를 조회합니다."""
        ...

    async def create_lotto_draw(self, lotto_data: dict) -> LottoDraws:
        """로또 추첨 데이터를 생성합니다."""
        ...

    async def get_lotto_draw_by_round(self, round: int) -> LottoDraws | None:
        """특정 회차의 로또 추첨 데이터를 조회합니다."""
        ...

    async def update_lotto_statistics(self, lotto_data: dict) -> None:
        """로또 통계 데이터를 업데이트합니다."""
        ...

    async def create_lotto_recommendation(
        self, user_id: str, round: int, content: dict
    ) -> LottoRecommendations:
        """로또 추천을 생성합니다."""
        ...

    async def get_lotto_recommendation_by_user_id(
        self,
        user_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> LottoRecommendations | None:
        """사용자의 최신 로또 추천을 조회합니다."""
        ...

    async def get_frequent_numbers(self, limit: int = 10) -> list[int]:
        """빈도 순으로 가장 많이 나온 번호들을 조회합니다."""
        ...

    async def get_excluded_numbers(self, limit: int = 2) -> list[int]:
        """last_round 기준 오름차순으로 정렬했을 때 가장 마지막 2개 번호를 조회합니다."""
        ...

    async def get_recommendation_by_user_and_round(
        self, user_id: str, round: int
    ) -> LottoRecommendations | None:
        """사용자와 회차로 추천을 조회합니다."""
        ...

    async def mark_all_recommendations_read_by_user_and_round(
        self, user_id: str, round: int, read_at: datetime
    ) -> None:
        """특정 사용자와 회차의 모든 추천을 읽음 처리합니다."""
        ...
