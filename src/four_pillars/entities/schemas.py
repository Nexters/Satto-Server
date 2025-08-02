from typing import Optional

from typing_extensions import TypedDict


class FourPillar(TypedDict):
    year_pillar: str
    month_pillar: str
    day_pillar: str
    time_pillar: Optional[str] = None
