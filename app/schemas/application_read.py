from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ApplicationRead(BaseModel):
    """Response schema for reading an application."""

    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
