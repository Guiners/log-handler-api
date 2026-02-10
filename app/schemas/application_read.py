from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.event_read import EventRead


class ApplicationRead(BaseModel):
    id: int
    name: str
    ingest_key: str
    created_at: datetime
    events: Optional[EventRead] = None

    model_config = {"from_attributes": True}
