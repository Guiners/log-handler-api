from __future__ import annotations

from datetime import datetime
from typing import Annotated

from annotated_types import Ge, Gt, Le, Lt, MinLen
from fastapi import APIRouter, Depends, FastAPI, Header, Request, status
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.constants import ErrorLevel, TimeEnum
from app.db.database import get_db
from app.schemas.application_creation_response import \
    ApplicationCreationResponse
from app.schemas.application_read import ApplicationRead
from app.schemas.by_level_output import ByLevelItem, ByLevelOutput
from app.schemas.error_response import ErrorResponse
from app.schemas.event_creation_input import EventCreationInput
from app.schemas.event_creation_output import EventCreationOutput
from app.schemas.event_list import EventList
from app.schemas.event_read import EventRead
from app.schemas.timeseries_output import Series, TimeseriesOutput
from app.schemas.top_messages_output import TopMessageItem, TopMessagesOutput
from app.services.db_menager import DataBaseManager
from app.tools.custom_exceptions import IngestForbiddenError

status_router = APIRouter(tags=["Status"])


@status_router.get(
    "/{app_id}/stats/timeseries",
    response_model=TimeseriesOutput,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_timeseries(
    app_id: Annotated[int, Gt(0)],
    since: datetime,
    until: datetime,
    interval: TimeEnum = TimeEnum.HOUR,
    level: ErrorLevel | None = None,
    db: AsyncSession = Depends(get_db),
):
    if since >= until:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="CONFLICT", message="since must be earlier than until"
            ).model_dump(),
        )
    result = await DataBaseManager(db).read_bucket_stats_list(
        app_id, since, until, interval, level
    )
    return TimeseriesOutput(
        interval=interval,
        since=since,
        until=until,
        series=[
            Series(bucket_start=bucket_start, count=count)
            for bucket_start, count in result
        ],
    )


@status_router.get(
    "/{app_id}/stats/by-level",
    response_model=ByLevelOutput,
    response_model_exclude_none=True,
)
async def get_by_level(
    app_id: Annotated[int, Gt(0)],
    since: datetime,
    until: datetime,
    db: AsyncSession = Depends(get_db),
):
    if since >= until:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="CONFLICT", message="since must be earlier than until"
            ).model_dump(),
        )

    rows = await DataBaseManager(db).read_stats_by_level(app_id, since, until)

    return ByLevelOutput(
        since=since,
        until=until,
        items=[ByLevelItem(level=level, count=count) for level, count in rows],
    )


@status_router.get(
    "/{app_id}/stats/top-messages",
    response_model=TopMessagesOutput,
    response_model_exclude_none=True,
)
async def get_top_messages(
    app_id: Annotated[int, Gt(0)],
    since: datetime,
    until: datetime,
    limit: Annotated[int, Ge(1), Le(100)] = 10,
    level: ErrorLevel | None = None,
    db: AsyncSession = Depends(get_db),
):
    if since >= until:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="CONFLICT", message="since must be earlier than until"
            ).model_dump(),
        )

    rows = await DataBaseManager(db).read_top_messages(
        app_id, since, until, limit, level
    )

    return TopMessagesOutput(
        limit=limit,
        items=[
            TopMessageItem(message=msg, count=count, last_seen=last_seen)
            for msg, count, last_seen in rows
        ],
    )
