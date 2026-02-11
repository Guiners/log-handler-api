from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.constants import TimeEnum


class Series(BaseModel):
    bucket_start: datetime
    count: int

    model_config = {"from_attributes": True}


class TimeseriesOutput(BaseModel):
    interval: TimeEnum
    since: datetime
    until: datetime
    series: list[Series]

    model_config = {"from_attributes": True}
