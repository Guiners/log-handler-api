from datetime import datetime

from pydantic import BaseModel

from app.constants import ErrorLevel


class ByLevelItem(BaseModel):
    level: ErrorLevel
    count: int


class ByLevelOutput(BaseModel):
    since: datetime
    until: datetime
    items: list[ByLevelItem]
