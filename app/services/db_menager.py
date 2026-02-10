from __future__ import annotations

import secrets
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.application import Application
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

    async def add_application(self, app_name: str) -> Application:
        ingest_key = secrets.token_hex(16)
        app = Application(name=app_name, ingest_key=ingest_key)
        logger.info(f"Adding {app_name} application")
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)

        stmt = select(Application).where(Application.id == app.id)

        return (await self.db.execute(stmt)).scalar_one()
