from typing import List, Optional

from pydantic import BaseModel


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
