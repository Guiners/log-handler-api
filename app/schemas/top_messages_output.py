from datetime import datetime

from pydantic import BaseModel


class TopMessageItem(BaseModel):
    """Single item representing a top occurring message."""

    message: str
    count: int
    last_seen: datetime


class TopMessagesOutput(BaseModel):
    """Response schema for top messages statistics."""

    limit: int
    items: list[TopMessageItem]
