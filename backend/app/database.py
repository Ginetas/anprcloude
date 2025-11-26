"""
Database Connection Management
Handles PostgreSQL connection using SQLModel with async support.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.config import settings


# Synchronous engine for Alembic migrations
sync_engine = create_engine(
    settings.database_url,
    echo=settings.postgres_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,  # Verify connections before using them
)

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.postgres_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
    future=True,
)

# Async session factory
async_session_factory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def create_db_and_tables():
    """
    Create all database tables.
    Should only be used for development/testing.
    Use Alembic migrations in production.
    """
    SQLModel.metadata.create_all(sync_engine)


def drop_db_and_tables():
    """
    Drop all database tables.
    Should only be used for development/testing.
    """
    SQLModel.metadata.drop_all(sync_engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        @app.get("/items")
        async def read_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
        ```
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for getting async database session.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        async with get_session_context() as session:
            result = await session.execute(select(Item))
            items = result.scalars().all()
        ```
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database connection.
    Called on application startup.
    """
    # Test connection
    async with async_engine.begin() as conn:
        # You can run initial setup here if needed
        pass


async def close_db():
    """
    Close database connection.
    Called on application shutdown.
    """
    await async_engine.dispose()


# Redis connection
class RedisManager:
    """Redis connection manager."""

    def __init__(self):
        self._redis: Optional[any] = None

    async def connect(self):
        """Initialize Redis connection."""
        import redis.asyncio as aioredis

        self._redis = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()

    @property
    def client(self):
        """Get Redis client instance."""
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._redis

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in Redis with optional expiration."""
        return await self.client.set(
            key,
            value,
            ex=expire or settings.redis_ttl
        )

    async def delete(self, key: str) -> int:
        """Delete key from Redis."""
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        return await self.client.exists(key) > 0

    async def publish(self, channel: str, message: str) -> int:
        """Publish message to Redis channel."""
        return await self.client.publish(channel, message)

    async def subscribe(self, channel: str):
        """Subscribe to Redis channel."""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis():
    """
    Dependency to get Redis client.

    Yields:
        Redis client instance
    """
    return redis_manager.client
