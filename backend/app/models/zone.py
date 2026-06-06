"""
Zone Model
"""
from sqlalchemy import Column, Integer, String, Text, Index

from app.models.base import Base, TimestampMixin


class Zone(Base, TimestampMixin):
    """Represents a physical zone in the factory"""
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(100), unique=True, nullable=False, index=True)
    zone_type = Column(String(50), nullable=False)  # entry, department, common
    description = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('idx_zones_type', 'zone_type'),
    )
    
    def __repr__(self):
        return f"<Zone(id={self.id}, zone_name={self.zone_name}, zone_type={self.zone_type})>"
