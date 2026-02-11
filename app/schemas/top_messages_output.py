from datetime import datetime

from pydantic import BaseModel


class TopMessageItem(BaseModel):
    message: str
    count: int
    last_seen: datetime


class TopMessagesOutput(BaseModel):
    limit: int
    items: list[TopMessageItem]
