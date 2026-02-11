from __future__ import annotations

import typing

from sqlalchemy import BigInteger, DateTime
from sqlalchemy import Enum as sql_Enum
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import ErrorLevel
from app.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.db.models.application import Application


class Event(Base):
    __tablename__ = "event"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    application_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("application.id", ondelete="CASCADE"), nullable=False
    )
    occurred_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    received_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    level: Mapped[ErrorLevel] = mapped_column(
        sql_Enum(ErrorLevel, name="error_lvl", create_type=False),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(String(255), nullable=False)

    stack: Mapped[JSONB] = mapped_column(JSONB)
    tags: Mapped[JSONB] = mapped_column(JSONB)

    # relationship
    application: Mapped["Application"] = relationship(back_populates="events")
