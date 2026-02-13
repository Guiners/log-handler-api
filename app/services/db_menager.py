from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ErrorLevel, TimeEnum
from app.db.models import Event
from app.db.models.application import Application
from app.schemas.event_creation_input import EventCreationInput
from app.tools.custom_exceptions import IngestForbiddenError
from app.tools.logger import logger


class DataBaseManager:
    """Database access layer for application and event operations."""

    def __init__(self, db: AsyncSession):
        """Create a new database manager.

        Args:
            db: SQLAlchemy async session.
        """
        self.db = db

    async def _read_by_id(self, model: Any, obj_id: int) -> Any | None:
        """Read a single row by primary key.

        Args:
            model: SQLAlchemy mapped model class.
            obj_id: Primary key value.

        Returns:
            ORM instance if found, otherwise None.
        """
        stmt = select(model).where(model.id == obj_id)
        results = await self.db.execute(stmt)
        return results.scalar_one_or_none()

    async def read_app_by_id(self, app_id: int) -> Application | None:
        """Read an application by id.

        Args:
            app_id: Application identifier.

        Returns:
            Application instance if found, otherwise None.
        """
        return await self._read_by_id(Application, app_id)

    @staticmethod
    def _create_event_where_condition(
        app_id: int,
        since: datetime | None,
        until: datetime | None,
        level: ErrorLevel | None,
    ) -> list[Any]:
        """Build WHERE conditions for event queries.

        Args:
            app_id: Application identifier.
            since: Optional lower bound for received time.
            until: Optional upper bound for received time.
            level: Optional error level filter.

        Returns:
            List of SQLAlchemy boolean expressions for WHERE clause.
        """
        where_conditions: list[Any] = [Event.application_id == app_id]

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
        """Read paginated events for an application.

        Args:
            app_id: Application identifier.
            limit: Maximum number of rows to return.
            offset: Pagination offset.
            level: Optional error level filter.
            since: Optional lower bound for received time.
            until: Optional upper bound for received time.

        Returns:
            List of event ORM instances.
        """
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
        self,
        app_id: int,
        payload: EventCreationInput,
        ingest_key: str,
    ) -> Event | None:
        """Create a new event after verifying ingest credentials.

        Args:
            app_id: Application identifier.
            payload: Event payload.
            ingest_key: Ingest key provided by the client.

        Returns:
            Created event ORM instance.

        Raises:
            IngestForbiddenError: If application does not exist or ingest key is invalid.
        """
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

    async def create_application(self, app_name: str) -> Application | None:
        """Create a new application with a generated ingest key.

        Args:
            app_name: Unique application name.

        Returns:
            Created application ORM instance.
        """
        ingest_key = secrets.token_hex(16)
        app = Application(name=app_name, ingest_key=ingest_key)
        logger.info(f"Adding {app_name} application")
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return await self._read_by_id(Application, app.id)

    async def read_all_apps(self) -> list[Application]:
        """Read all applications.

        Returns:
            List of application ORM instances.
        """
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
        """Return time-bucketed counts for an application.

        Args:
            app_id: Application identifier.
            since: Lower bound for received time.
            until: Upper bound for received time.
            interval: Bucket size (e.g., hour/day).
            level: Optional error level filter.
        """
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
        """Return event counts grouped by severity level.

        Args:
            app_id: Application identifier.
            since: Lower bound for received time.
            until: Upper bound for received time.
        """
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
        """Return the most frequent messages with their counts and last seen time.

        Args:
            app_id: Application identifier.
            since: Lower bound for received time.
            until: Upper bound for received time.
            limit: Maximum number of messages to return.
            level: Optional error level filter.
        """
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
