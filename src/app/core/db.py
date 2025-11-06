import asyncio
from contextlib import asynccontextmanager
from multiprocessing import pool
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.settings import settings
from core.logger import get_logger

logger = get_logger()

engine = create_async_engine(
    settings.DATABASE_URL, 
    poolclass=AsyncAdaptedQueuePool, 
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False
)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            if session:
                try:
                    await session.rollback()
                    logger.info("Database session rollback successful")
                except Exception as e:
                    logger.error(f"Database session rollback error: {e}")
            raise
        finally:
            try:
                await session.close()
                logger.debug("Database session closed successfully")
            except Exception as e:
                logger.error(f"Database session close error: {e}")
                raise


async def get_db_dependency() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            if session:
                try:
                    await session.rollback()
                    logger.info("Database session rollback successful")
                except Exception as e:
                    logger.error(f"Database session rollback error: {e}")
            raise
        finally:
            try:
                await session.close()
                logger.debug("Database session closed successfully")
            except Exception as e:
                logger.error(f"Database session close error: {e}")
                raise

async def init_db() -> None:
    try:
        max_tries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_tries):
            try:
                async with engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info("Database connection established successfully")
                break
            except Exception as e:
                logger.error(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_tries - 1:
                    logger.warning(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    logger.critical("All database connection attempts failed")
                    raise
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        raise