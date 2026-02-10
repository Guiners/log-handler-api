from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any, List

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ErrorLevel
from app.db.models import Event
from app.db.models.application import Application
from app.schemas.event_creation_input import EventCreationInput
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

    async def read_events_by_application_id(
        self,
        app_id: int,
        limit: int,
        offset: int,
        level: ErrorLevel | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:

        where_conditions = [Event.application_id == app_id]

        if level:
            where_conditions.append(Event.level == level)

        if since:
            where_conditions.append(Event.received_at >= since)

        if until:
            where_conditions.append(Event.received_at <= until)

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
            raise Exception("Application id or ingest_key does not match")

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
