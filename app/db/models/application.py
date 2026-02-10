from __future__ import annotations

import typing

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.db.models.event import Event


class Application(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    ingest_key: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # relationship
    events: Mapped[list["Event"]] = relationship(back_populates="application")
