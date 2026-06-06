"""
Attendance Event Model
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index, func
from datetime import datetime

from app.models.base import Base, TimestampMixin


class AttendanceEvent(Base):
    """Tracks operator movement events (entry/exit at cameras)"""
    __tablename__ = "attendance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    zone_type = Column(String(50), nullable=True)  # Denormalized for query performance
    event_type = Column(String(20), nullable=False)  # IN, OUT
    confidence_score = Column(Float, nullable=True)  # Face recognition confidence (0-1)
    snapshot_path = Column(Text, nullable=True)
    event_time = Column(DateTime, default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_attendance_operator_time', 'operator_id', 'event_time'),
        Index('idx_attendance_camera_time', 'camera_id', 'event_time'),
        Index('idx_attendance_zone_time', 'zone_type', 'event_time'),
        Index('idx_attendance_event_type', 'event_type'),
    )
    
    def __repr__(self):
        return f"<AttendanceEvent(id={self.id}, operator_id={self.operator_id}, event_type={self.event_type}, event_time={self.event_time})>"
