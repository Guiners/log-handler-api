import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

import app.db.models

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for dependency injection.

    Yields:
        AsyncSession: An active SQLAlchemy async session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
