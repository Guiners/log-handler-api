from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EventCreationOutput(BaseModel):
    """Response schema returned after successful event creation."""

    id: int
    application_id: int
    received_at: datetime

    model_config = {"from_attributes": True}
