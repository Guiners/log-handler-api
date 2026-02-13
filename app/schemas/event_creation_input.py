from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.constants import ErrorLevel


class EventCreationInput(BaseModel):
    """Request schema for creating a new event."""

    occurred_at: datetime
    level: ErrorLevel
    message: str
    stack: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}
