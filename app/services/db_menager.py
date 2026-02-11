from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ErrorLevel, TimeEnum
from app.db.models import Event
from app.db.models.application import Application
from app.schemas.event_creation_input import EventCreationInput
from app.tools.custom_exceptions import IngestForbiddenError
from app.tools.logger import logger


class DataBaseManager:
    """
    Utility class for performing dynamic DDL (Data Definition Language)
    operations on a PostgreSQL database using SQLAlchemy AsyncSession.

    Supports adding, removing, renaming, and altering table columns,
    as well as creating, deleting, and truncating entire tables.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the database manager.

        Args:
            db (AsyncSession): The SQLAlchemy asynchronous session.
        """
        self.db = db

    async def _read_by_id(self, model, obj_id: int):
        stmt = select(model).where(model.id == obj_id)
        results = await self.db.execute(stmt)
        return results.scalar_one_or_none()

    async def read_app_by_id(self, app_id: int):
        return await self._read_by_id(Application, app_id)

    @staticmethod
    def _create_event_where_condition(
        app_id: int,
        since: datetime | None,
        until: datetime | None,
        level: ErrorLevel | None,
    ):
        where_conditions = [Event.application_id == app_id]

        if level:
            where_conditions.append(Event.level == level)

        if since:
            where_conditions.append(Event.received_at >= since)

        if until:
            where_conditions.append(Event.received_at <= until)

        return where_conditions

    async def read_events_by_application_id(
        self,
        app_id: int,
        limit: int,
        offset: int,
        level: ErrorLevel | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:

        where_conditions = self._create_event_where_condition(
            app_id, since, until, level
        )

        stmt = (
            select(Event)
            .where(*where_conditions)
            .limit(limit)
            .offset(offset)
            .order_by(Event.received_at.desc())
        )

        results = await self.db.execute(stmt)

        return results.scalars().all()

    async def create_event(
        self, app_id: int, payload: EventCreationInput, ingest_key: str
    ):
        stmt = select(Application).where(
            Application.id == app_id, Application.ingest_key == ingest_key
        )
        results = await self.db.execute(stmt)
        app = results.scalar_one_or_none()

        if not app:
            raise IngestForbiddenError

        event = Event(application_id=app_id, **payload.model_dump(exclude_none=True))
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return await self._read_by_id(Event, event.id)

    async def create_application(self, app_name: str) -> Application:
        ingest_key = secrets.token_hex(16)
        app = Application(name=app_name, ingest_key=ingest_key)
        logger.info(f"Adding {app_name} application")
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return await self._read_by_id(Application, app.id)

    async def read_all_apps(self) -> list[Application]:
        result = await self.db.execute(select(Application))
        return result.scalars().all()

    async def read_bucket_stats_list(
        self,
        app_id: int,
        since: datetime,
        until: datetime,
        interval: TimeEnum,
        level: ErrorLevel | None,
    ):
        where_conditions = self._create_event_where_condition(
            app_id, since, until, level
        )
        bucket_expr = func.date_trunc(interval.value, Event.received_at).label(
            "bucket_start"
        )

        stmt = (
            select(
                bucket_expr,
                func.count(Event.id).label("count"),
            )
            .where(*where_conditions)
            .group_by(bucket_expr)
            .order_by(bucket_expr)
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def read_stats_by_level(
        self,
        app_id: int,
        since: datetime,
        until: datetime,
    ):
        where_conditions = self._create_event_where_condition(
            app_id, since, until, level=None
        )

        stmt = (
            select(
                Event.level.label("level"),
                func.count(Event.id).label("count"),
            )
            .where(*where_conditions)
            .group_by(Event.level)
            .order_by(func.count(Event.id).desc())
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def read_top_messages(
        self,
        app_id: int,
        since: datetime,
        until: datetime,
        limit: int,
        level: ErrorLevel | None,
    ):
        where_conditions = self._create_event_where_condition(
            app_id, since, until, level
        )

        stmt = (
            select(
                Event.message.label("message"),
                func.count(Event.id).label("count"),
                func.max(Event.received_at).label("last_seen"),
            )
            .where(*where_conditions)
            .group_by(Event.message)
            .order_by(func.count(Event.id).desc(), func.max(Event.received_at).desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.all()
