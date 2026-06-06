"""
Violation Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, func

from app.models.base import Base


class Violation(Base):
    """Records compliance violations detected by the system"""
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    violation_type = Column(String(100), nullable=False)  # Rule name
    violation_message = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    related_event_id = Column(Integer, ForeignKey("attendance_logs.id"), nullable=True)  # Event that triggered violation
    status = Column(String(20), default="open")  # open, acknowledged, resolved
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_violations_operator', 'operator_id', 'created_at'),
        Index('idx_violations_severity', 'severity', 'created_at'),
        Index('idx_violations_type', 'violation_type'),
        Index('idx_violations_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Violation(id={self.id}, operator_id={self.operator_id}, violation_type={self.violation_type}, severity={self.severity})>"
