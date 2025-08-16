from datetime import date
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from src.fortune.entities.enums import FortuneType
from src.fortune.entities.schemas import (
    DailyFortuneResource,
    DailyFortuneResourceCreate,
    DailyFortuneResourceUpdate,
    DailyFortuneResourceList,
    UserDailyFortuneDetail,
)
from src.fortune.entities.schemas import UserDailyFortuneSummary
from src.fortune.repository import FortuneRepository
from src.fortune.entities.constants import DAILY_FORTUNE_FALLBACK_DATA
from src.hcx_client.client import HCXClient
from src.hcx_client.common.parser import Parser
from src.hcx_client.common.utils import HCXUtils
from src.users.repository import UserRepository
from src.common.logger import logger
from src.storage_client.client import ObjectStorageClient, ALLOWED_CONTENT_TYPES


class FortuneService:
    def __init__(
        self,
        storage: ObjectStorageClient = Depends(ObjectStorageClient),
        fortune_repository: FortuneRepository = Depends(),
        user_repository: UserRepository = Depends(),
    ):
        self.repository = fortune_repository
        self.user_repository = user_repository
        self.storage = storage


    async def list_fortunes(
        self,
        cursor: Optional[int],
        limit: int,
        publish_date: Optional[date],
        fortune_type: Optional[FortuneType],
    ) -> DailyFortuneResourceList:
        items, next_cursor = await self.repository.get_fortunes(
            cursor=cursor,
            limit=limit,
            publish_date=publish_date,
            fortune_type=fortune_type,
        )
        return DailyFortuneResourceList(
            items=[DailyFortuneResource.model_validate(i) for i in items],
            next_cursor=next_cursor,
        )

    async def create_fortune(
        self, dto: DailyFortuneResourceCreate
    ) -> DailyFortuneResource:
        # DTO에서 개별 필드를 추출하여 리포지토리 메서드 호출
        model = await self.repository.create_fortune(
            publish_date=dto.publish_date,
            fortune_type=dto.fortune_type,
            image_url=dto.image_url,
            description=dto.description,
        )

        # DB 모델을 DTO로 변환하여 반환
        return DailyFortuneResource.model_validate(model)

    async def create_fortune_with_image(
        self, dto: DailyFortuneResourceCreate, *, upload_file  # UploadFile | None
    ) -> DailyFortuneResource:
        image_url = ""

        # 이미지가 올라오면 Object Storage에 먼저 업로드
        if upload_file:
            if upload_file.content_type not in ALLOWED_CONTENT_TYPES:
                raise HTTPException(status_code=400, detail="허용되지 않는 이미지 형식입니다.")
            key = self.storage.make_key(prefix=f"fortunes/{dto.publish_date}", filename=upload_file.filename)
            # boto3는 sync → threadpool
            image_url = await run_in_threadpool(
                self.storage.upload_fileobj,
                upload_file.file,
                key=key,
                content_type=upload_file.content_type,
            )

        model = await self.repository.create_fortune(
            publish_date=dto.publish_date,
            fortune_type=dto.fortune_type,
            image_url=image_url,
            description=dto.description,
        )
        return DailyFortuneResource.model_validate(model)

    async def update_fortune(
        self, resource_id: int, dto: DailyFortuneResourceUpdate
    ) -> DailyFortuneResource:
        model = await self.repository.update_fortune(
            resource_id=resource_id,
            publish_date=dto.publish_date,
            fortune_type=dto.fortune_type,
            image_url=dto.image_url,
            description=dto.description,
        )

        return DailyFortuneResource.model_validate(model)

    async def delete_fortune(self, resource_id: int) -> None:
        try:
            await self.repository.delete_fortune(resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="리소스를 찾을 수 없습니다.",
            )

    async def get_user_daily_fortune_summaries(
        self, user_id: str, fortune_date: date
    ) -> List[UserDailyFortuneSummary]:
        summaries = await self.repository.get_user_daily_fortune_summaries(
            user_id, fortune_date
        )
        if not summaries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="오늘의 운세 데이터를 찾을 수 없습니다.",
            )
        return summaries  # Return the list directly

    async def get_user_daily_fortune_detail(
        self, user_id: str, fortune_date: date
    ) -> UserDailyFortuneDetail:
        """사용자의 특정 날짜 운세 상세 정보를 조회하거나 생성합니다."""
        # 1. 기존 운세 상세 정보 조회
        existing_detail = await self.repository.get_user_daily_fortune_detail(
            user_id, fortune_date
        )

        if existing_detail:
            return UserDailyFortuneDetail.model_validate(existing_detail)

        # 2. 기존 정보가 없으면 HCX API 호출하여 생성
        return await self._create_daily_fortune_detail(user_id, fortune_date)

    async def _create_daily_fortune_detail(
        self, user_id: str, fortune_date: date
    ) -> UserDailyFortuneDetail:
        """HCX API를 호출하여 운세 상세 정보를 생성합니다."""
        # 1. 사용자 정보 조회 (사주 정보 포함)
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        if not user.four_pillar:
            raise HTTPException(
                status_code=400, detail="사용자의 사주 정보가 없습니다."
            )

        # 2. HCX API 호출
        hcx_client = HCXClient()

        # 사용자 사주 정보 사용
        four_pillar = user.four_pillar
        fortune_prompt_data = {
            "year_pillar": four_pillar.get("year_pillar"),
            "month_pillar": four_pillar.get("month_pillar"),
            "day_pillar": four_pillar.get("day_pillar"),
            "time_pillar": four_pillar.get("time_pillar"),
            "strong_element": four_pillar.get("strong_element"),
            "weak_element": four_pillar.get("weak_element"),
        }

        # HCXUtils를 사용하여 프롬프트 가져오기
        system_prompt, user_prompt_template = HCXUtils.get_prompt_pair(
            "fortune.yaml", "daily_fortune"
        )

        user_prompt = user_prompt_template.format(**fortune_prompt_data)

        # HCX API 호출 및 fallback 처리
        fortune_data = None
        try:
            response_content = await hcx_client.call_completion(
                system_prompt=system_prompt, user_prompt=user_prompt
            )

            # 3. 응답 파싱
            fortune_data = Parser.parse_json(response_content)
            logger.info(f"HCX API 호출 성공: 사용자 {user_id}의 운세 데이터 생성 완료")

        except Exception as e:
            logger.warning(
                f"HCX API 호출 또는 파싱 실패, fallback 데이터 사용: {str(e)}"
            )
            # fallback 데이터 사용
            fortune_data = DAILY_FORTUNE_FALLBACK_DATA

        # 4. fortune_details 구성
        fortune_details = {
            "재물운": fortune_data.get("money_fortune", ""),
            "취업운": fortune_data.get("job_fortune", ""),
            "연애운": fortune_data.get("love_fortune", ""),
        }

        # 5. DB에 저장
        model = await self.repository.create_user_daily_fortune_detail(
            user_id=user_id,
            fortune_date=fortune_date,
            fortune_score=fortune_data.get("score", 0),
            fortune_comment=fortune_data.get("comment", ""),
            fortune_details=fortune_details,
        )

        return UserDailyFortuneDetail.model_validate(model)
