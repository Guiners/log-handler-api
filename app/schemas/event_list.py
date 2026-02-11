from __future__ import annotations

from pydantic import BaseModel

from app.schemas.event_read import EventRead


class EventList(BaseModel):
    items: list[EventRead]
    next_offset: int | None = None

    model_config = {"from_attributes": True}
