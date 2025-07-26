import httpx
from fastapi import HTTPException

from src.common.logger import logger
from src.config.config import hcx_config
from src.hcx_client.entities.schemas import CompletionSettings


class HCXClient:
    """HCX API 공용 클라이언트 (싱글톤)"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.api_key = hcx_config.HCX_KEY
            cls._instance.url = hcx_config.HCX_URL
            cls._instance.headers = {
                "Authorization": f"Bearer {cls._instance.api_key}",
                "Content-Type": "application/json",
            }
        return cls._instance

    async def call_completion(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> str:
        """HCX API 호출"""
        settings = CompletionSettings(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                headers=self.headers,
                json=settings.model_dump(exclude_none=True),
            )
            result = response.json()
            if result["status"]["code"] != "20000":
                logger.error(f"HCX API 호출 실패: {result['status']['message']}")
                raise HTTPException(
                    status_code=400,
                    detail=f"HCX API 호출 실패: {result['status']['message']}",
                )

            return result["result"]["message"]["content"]
