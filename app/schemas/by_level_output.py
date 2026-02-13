from datetime import datetime

from pydantic import BaseModel

from app.constants import ErrorLevel


class ByLevelItem(BaseModel):
    """Single severity-level aggregate item."""

    level: ErrorLevel
    count: int


class ByLevelOutput(BaseModel):
    """Response schema for severity-level distribution statistics."""

    since: datetime
    until: datetime
    items: list[ByLevelItem]
