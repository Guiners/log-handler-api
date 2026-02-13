from __future__ import annotations

from datetime import datetime
from typing import Annotated

from annotated_types import Ge, Gt, Le
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.constants import ErrorLevel, TimeEnum
from app.db.database import get_db
from app.schemas.by_level_output import ByLevelItem, ByLevelOutput
from app.schemas.error_response import ErrorResponse
from app.schemas.timeseries_output import Series, TimeseriesOutput
from app.schemas.top_messages_output import TopMessageItem, TopMessagesOutput
from app.services.db_menager import DataBaseManager


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
) -> TimeseriesOutput | JSONResponse:
    """Return time-bucketed event counts for an application.

    Args:
        app_id: Application identifier.
        since: Lower bound for received time.
        until: Upper bound for received time.
        interval: Bucket size (e.g., hour/day).
        level: Optional error level filter.
        db: Database session dependency.

    Returns:
        Timeseries response or validation error response when time range is invalid.
    """
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
) -> ByLevelOutput | JSONResponse:
    """Return event counts grouped by severity level for an application.

    Args:
        app_id: Application identifier.
        since: Lower bound for received time.
        until: Upper bound for received time.
        db: Database session dependency.

    Returns:
        By-level distribution or validation error response when time range is invalid.
    """
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
) -> TopMessagesOutput | JSONResponse:
    """Return the most frequent event messages for an application.

    Args:
        app_id: Application identifier.
        since: Lower bound for received time.
        until: Upper bound for received time.
        limit: Maximum number of messages to return.
        level: Optional error level filter.
        db: Database session dependency.

    Returns:
        Top messages response or validation error response when time range is invalid.
    """
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
