from __future__ import annotations

from datetime import datetime
from typing import Annotated

from annotated_types import Ge, Gt, Le, Lt, MinLen
from fastapi import APIRouter, Depends, FastAPI, Header, Request, status
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.constants import ErrorLevel
from app.db.database import get_db
from app.schemas.application_creation_response import \
    ApplicationCreationResponse
from app.schemas.application_read import ApplicationRead
from app.schemas.error_response import ErrorResponse
from app.schemas.event_creation_input import EventCreationInput
from app.schemas.event_creation_output import EventCreationOutput
from app.schemas.event_list import EventList
from app.schemas.event_read import EventRead
from app.services.db_menager import DataBaseManager
from app.tools.custom_exceptions import IngestForbiddenError

event_router = APIRouter(tags=["Events"])


@event_router.get(
    "/{app_id}/events",
    response_model=EventList,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_events_by_application_id(
    app_id: int,
    limit: Annotated[int, Gt(0), Le(50)],
    offset: Annotated[int, Ge(0)],
    level: ErrorLevel | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        events = await DataBaseManager(db).read_events_by_application_id(
            app_id, limit, offset, level, since, until
        )
        converted_items = [EventRead.model_validate(event) for event in events]
        return EventList(items=converted_items, next_offset=offset + limit)

    except NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error="ERROR", message="event with this application id does not exist"
            ).model_dump(),
        )


@event_router.post(
    "/{app_id}/events",
    response_model=EventCreationOutput,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    app_id: int,
    payload: EventCreationInput,
    ingest_key: str = Header(..., alias="X-INGEST-KEY"),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await DataBaseManager(db).create_event(app_id, payload, ingest_key)

    except IngestForbiddenError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error="ERROR", message="Invalid application or ingest key"
            ).model_dump(),
        )
