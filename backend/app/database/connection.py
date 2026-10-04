"""
database/connection.py — การเชื่อมต่อ Database

รองรับ:
- SQLite (local development — ไม่ต้องติดตั้งอะไรเพิ่ม)
- Azure SQL (production)

ใช้ SQLAlchemy async engine เพื่อให้ FastAPI ทำงานแบบ non-blocking
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

settings = get_settings()

# ── สร้าง async engine ──────────────────────────────────────────
# connect_args ต่างกันระหว่าง SQLite และ SQL Server
_connect_args: dict = {}
if "sqlite" in settings.database_url:
    # SQLite ต้องการ check_same_thread=False สำหรับ async
    _connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,        # print SQL queries ใน debug mode
    pool_pre_ping=True,         # ตรวจสอบ connection ก่อนใช้
    connect_args=_connect_args,
)

# ── Session factory ──────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,     # อย่า expire objects หลัง commit
    autoflush=False,
    autocommit=False,
)


# ── Base class สำหรับ ORM models ─────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency สำหรับ FastAPI ────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — ให้ database session ต่อ request
    ปิด session อัตโนมัติหลัง request เสร็จ

    Usage:
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    สร้าง tables ทั้งหมดถ้ายังไม่มี (สำหรับ SQLite dev เท่านั้น)
    Azure SQL production ใช้ schema.sql หรือ Alembic migrations
    """
    if "sqlite" in settings.database_url:
        logger.info("SQLite mode: creating tables...")
        async with engine.begin() as conn:
            from app.models import category, order, product, user  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created ✅")
