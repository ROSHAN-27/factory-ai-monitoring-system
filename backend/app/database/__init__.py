"""
Database connection and session management
"""
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections every hour
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configure PostgreSQL connection settings"""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET TIME ZONE 'UTC'")
    cursor.close()


def init_db():
    """Initialize database - create tables if they don't exist"""
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def close_db():
    """Close database connections"""
    engine.dispose()
    logger.info("Database connections closed")
