"""
Camera Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index
from datetime import datetime

from app.models.base import Base, TimestampMixin


class Camera(Base, TimestampMixin):
    """Represents a surveillance camera in the factory"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_name = Column(String(100), nullable=False, index=True)
    rtsp_url = Column(Text, nullable=True)
    location_name = Column(String(100), nullable=True)
    zone_type = Column(String(50), nullable=True)  # main_gate, knitting, linking, etc.
    status = Column(String(20), default="online")  # online, offline, degraded
    fps = Column(Integer, nullable=True)
    accuracy_percent = Column(Integer, nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_cameras_zone_type', 'zone_type'),
        Index('idx_cameras_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Camera(id={self.id}, camera_name={self.camera_name}, zone_type={self.zone_type})>"
