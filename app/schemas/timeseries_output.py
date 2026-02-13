from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.constants import TimeEnum


class Series(BaseModel):
    """Single time bucket item for timeseries statistics."""

    bucket_start: datetime
    count: int

    model_config = {"from_attributes": True}


class TimeseriesOutput(BaseModel):
    """Response schema for timeseries statistics."""

    interval: TimeEnum
    since: datetime
    until: datetime
    series: list[Series]

    model_config = {"from_attributes": True}
