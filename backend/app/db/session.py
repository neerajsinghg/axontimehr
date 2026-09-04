from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.core.logging import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

# Determine database engine (PostgreSQL or local SQLite fallback)
db_url = settings.DATABASE_URL
if "@postgres:" in db_url:
    import socket
    try:
        socket.gethostbyname("postgres")
        engine = create_async_engine(db_url, echo=settings.APP_DEBUG, future=True, poolclass=NullPool)
    except Exception:
        logger.info("Docker PostgreSQL host not resolved. Using SQLite database file (axontimehr.db)...")
        engine = create_async_engine("sqlite+aiosqlite:///./axontimehr.db", echo=settings.APP_DEBUG, future=True, poolclass=NullPool)
else:
    engine = create_async_engine(db_url, echo=settings.APP_DEBUG, future=True, poolclass=NullPool)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        statements = [
            "ALTER TABLE attendances ADD COLUMN IF NOT EXISTS location_status VARCHAR(50) DEFAULT 'NOT_REQUIRED'",
            "ALTER TABLE attendances ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'NOT_REQUIRED'",
            "ALTER TABLE attendances ADD COLUMN IF NOT EXISTS has_exception BOOLEAN DEFAULT FALSE",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS latitude FLOAT",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS longitude FLOAT",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS accuracy FLOAT",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS distance_meters FLOAT",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS captured_at TIMESTAMP WITH TIME ZONE",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS geofence_status VARCHAR(50)",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50)",
            "ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS verification_id UUID",
            "ALTER TABLE learning_courses ADD COLUMN IF NOT EXISTS course_url VARCHAR(500)"
        ]
        for stmt in statements:
            try:
                await conn.execute(text(stmt))
            except Exception as e:
                logger.debug(f"Init DB statement skipped: {stmt} -> {e}")


async def check_database_connection() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
