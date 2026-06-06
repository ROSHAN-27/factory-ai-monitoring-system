"""
Employee/Operator Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func, UniqueConstraint, Index
from datetime import datetime

from app.models.base import Base, TimestampMixin


class Employee(Base, TimestampMixin):
    """Represents an operator/employee in the factory"""
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    shift_name = Column(String(50), nullable=True)
    face_image_path = Column(Text, nullable=True)
    supervisor_id = Column(Integer, nullable=True)
    employment_status = Column(String(20), default="active")  # active, inactive, terminated
    line_section = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    
    __table_args__ = (
        Index('idx_operators_dept_shift', 'department', 'shift_name'),
        Index('idx_operators_status', 'employment_status'),
    )
    
    def __repr__(self):
        return f"<Employee(id={self.id}, employee_id={self.employee_id}, full_name={self.full_name})>"
