"""
Base model class for all SQLAlchemy models
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func
from datetime import datetime

# Base class for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
