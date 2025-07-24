from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    role: str
    content: str


class CompletionSettings(BaseModel):
    messages: List[Message]
    topP: Optional[float] = 0.8
    topK: Optional[int] = 0
    maxTokens: Optional[int] = 512
    temperature: Optional[float] = 0.5
    repeatPenalty: Optional[float] = 0.5
    stopBefore: Optional[list] = None
    includeAiFilters: Optional[bool] = True


# ========= 테스트 용 응답 모델 ==========
class FourPillarRequest(BaseModel):
    name: str
    gender: str
    birth_date: str


class FourPillarResponse(BaseModel):
    year_pillar: Optional[str]
    month_pillar: Optional[str]
    day_pillar: Optional[str]
    time_pillar: Optional[str]
    interpretation: Optional[str]
