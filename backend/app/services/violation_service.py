"""
Violation Service - Detects compliance violations based on business rules
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import logging

from app.models.attendance import AttendanceEvent
from app.models.employee import Employee
from app.models.camera import Camera
from app.models.violation import Violation
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Define which zones are entry points vs departments
ENTRY_ZONES = {"main_gate"}
DEPARTMENT_ZONES = {"knitting", "linking", "finishing", "washing", "packing"}
DORMITORY_ZONE = "dormitory"
COMMON_ZONES = {"dormitory", "canteen", "common_area"}


class ViolationService:
    """Service for detecting and managing compliance violations"""
    
    @staticmethod
    def check_event_for_violations(
        db: Session,
        event: AttendanceEvent
    ) -> List[Violation]:
        """
        Check a new event for all possible violations
        
        Args:
            db: Database session
            event: The attendance event to check
        
        Returns:
            List of violations detected (empty if none)
        """
        violations = []
        operator = db.query(Employee).filter(Employee.id == event.operator_id).first()
        camera = db.query(Camera).filter(Camera.id == event.camera_id).first()
        
        if not operator or not camera:
            return violations
        
        # Rule 1: Missing Department Entry (Factory entry but no department entry)
        if event.event_type == "IN" and camera.zone_type in DEPARTMENT_ZONES:
            v = ViolationService._check_missing_department_entry(db, operator, event, camera)
            if v:
                violations.append(v)
        
        # Rule 2: Wrong Department Entry
        if event.event_type == "IN" and camera.zone_type in DEPARTMENT_ZONES:
            v = ViolationService._check_wrong_department_entry(db, operator, event, camera)
            if v:
                violations.append(v)
        
        # Rule 3: Dormitory movement after factory entry
        if event.event_type == "IN" and camera.zone_type == DORMITORY_ZONE:
            v = ViolationService._check_dormitory_post_entry(db, operator, event)
            if v:
                violations.append(v)
        
        # Rule 4: Early Department Exit
        if event.event_type == "OUT" and camera.zone_type in DEPARTMENT_ZONES:
            v = ViolationService._check_early_exit(db, operator)
            if v:
                violations.append(v)
        
        # Rule 5: Long Absence from Department
        if event.event_type == "IN" and camera.zone_type in DEPARTMENT_ZONES:
            v = ViolationService._check_long_absence(db, operator, event)
            if v:
                violations.append(v)
        
        # Rule 6: Shift Compliance
        v = ViolationService._check_shift_compliance(db, operator, event, camera)
        if v:
            violations.append(v)
        
        # Rule 7: Late Reporting
        if event.event_type == "IN" and camera.zone_type in ENTRY_ZONES:
            v = ViolationService._check_late_reporting(db, operator)
            if v:
                violations.append(v)
        
        # Rule 8: Repeated Violations
        v = ViolationService._check_repeat_violations(db, operator)
        if v:
            violations.append(v)
        
        # Save violations to database
        for violation in violations:
            violation.related_event_id = event.id
            db.add(violation)
        
        db.commit()
        return violations
    
    @staticmethod
    def _check_missing_department_entry(
        db: Session,
        operator: Employee,
        event: AttendanceEvent,
        camera: Camera
    ) -> Optional[Violation]:
        """
        Rule 1: Factory entry but no department entry
        Check if operator entered a department without first entering factory at gate
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if there's a factory ENTRY today before this event
        factory_entry = db.query(AttendanceEvent).join(Camera).filter(
            and_(
                AttendanceEvent.operator_id == operator.id,
                AttendanceEvent.event_time >= today_start,
                AttendanceEvent.event_time < event.event_time,
                AttendanceEvent.event_type == "IN",
                or_(
                    Camera.zone_type == "main_gate",
                    Camera.zone_type == "gate"
                )
            )
        ).first()
        
        if not factory_entry:
            return Violation(
                operator_id=operator.id,
                violation_type="missing_department_entry",
                violation_message=f"Department entry at {camera.zone_type} without factory entry",
                severity="high",
                status="open"
            )
        
        return None
    
    @staticmethod
    def _check_wrong_department_entry(
        db: Session,
        operator: Employee,
        event: AttendanceEvent,
        camera: Camera
    ) -> Optional[Violation]:
        """
        Rule 2: Wrong department entry
        Check if operator enters different department than assigned
        """
        if not operator.department:
            return None
        
        # If zone is a department and doesn't match operator's assigned dept
        if camera.zone_type != operator.department:
            return Violation(
                operator_id=operator.id,
                violation_type="wrong_department_entry",
                violation_message=f"Entry to {camera.zone_type} but assigned to {operator.department}",
                severity="high",
                status="open"
            )
        
        return None
    
    @staticmethod
    def _check_dormitory_post_entry(
        db: Session,
        operator: Employee,
        event: AttendanceEvent
    ) -> Optional[Violation]:
        """
        Rule 3: Dormitory movement after factory entry
        Check if operator goes to dormitory after they already entered factory
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if there's a factory entry today before this dormitory entry
        factory_entries = db.query(AttendanceEvent).join(Camera).filter(
            and_(
                AttendanceEvent.operator_id == operator.id,
                AttendanceEvent.event_time >= today_start,
                AttendanceEvent.event_time < event.event_time,
                AttendanceEvent.event_type == "IN",
                or_(
                    Camera.zone_type == "main_gate",
                    Camera.zone_type.in_(DEPARTMENT_ZONES)
                )
            )
        ).first()
        
        if factory_entries:
            return Violation(
                operator_id=operator.id,
                violation_type="dormitory_post_entry",
                violation_message="Unauthorized dormitory access after factory entry",
                severity="high",
                status="open"
            )
        
        return None
    
    @staticmethod
    def _check_early_exit(
        db: Session,
        operator: Employee
    ) -> Optional[Violation]:
        """
        Rule 4: Early Department Exit
        Check if operator exits department before threshold time
        """
        if not operator.shift_name:
            return None
        
        # This is simplified - in production, would look up actual shift times
        # For now, check if exit is more than 30 min before typical shift end (6 PM)
        current_hour = datetime.utcnow().hour
        
        # If it's before 5 PM and operator is exiting a department
        if current_hour < 17:
            return Violation(
                operator_id=operator.id,
                violation_type="early_department_exit",
                violation_message="Department exit before scheduled shift end time",
                severity="medium",
                status="open"
            )
        
        return None
    
    @staticmethod
    def _check_long_absence(
        db: Session,
        operator: Employee,
        event: AttendanceEvent
    ) -> Optional[Violation]:
        """
        Rule 5: Long absence from department (>2 hours)
        Check if operator has been away from their department too long
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        threshold = settings.LONG_ABSENCE_THRESHOLD_MINUTES
        
        # Find last OUT event in department
        last_dept_out = db.query(AttendanceEvent).join(Camera).filter(
            and_(
                AttendanceEvent.operator_id == operator.id,
                AttendanceEvent.event_time >= today_start,
                AttendanceEvent.event_time < event.event_time,
                AttendanceEvent.event_type == "OUT",
                Camera.zone_type.in_(DEPARTMENT_ZONES)
            )
        ).order_by(desc(AttendanceEvent.event_time)).first()
        
        if not last_dept_out:
            return None
        
        # Calculate time gap
        time_gap = (event.event_time - last_dept_out.event_time).total_seconds() / 60
        
        if time_gap > threshold:
            return Violation(
                operator_id=operator.id,
                violation_type="long_absence_department",
                violation_message=f"Absence from department for {int(time_gap)} minutes (threshold: {threshold})",
                severity="medium",
                status="open"
            )
        
        return None
    
    @staticmethod
    def _check_shift_compliance(
        db: Session,
        operator: Employee,
        event: AttendanceEvent,
        camera: Camera
    ) -> Optional[Violation]:
        """
        Rule 6: Shift Compliance
        Check if event occurs within operator's shift hours
        """
        if not operator.shift_name:
            return None
        
        # Simplified: Check if factory entry is outside normal hours
        if event.event_type == "IN" and camera.zone_type in ENTRY_ZONES:
            current_hour = event.event_time.hour
            
            # Typical shift: 8 AM - 6 PM, flag if entry before 7 AM or after 10 AM
            if current_hour < 7 or current_hour > 10:
                return Violation(
                    operator_id=operator.id,
                    violation_type="shift_non_compliance",
                    violation_message=f"Factory entry at {current_hour}:00, outside normal shift hours",
                    severity="high",
                    status="open"
                )
        
        return None
    
    @staticmethod
    def _check_late_reporting(
        db: Session,
        operator: Employee
    ) -> Optional[Violation]:
        """
        Rule 7: Late Reporting
        Check if operator's first entry of the day is late
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        threshold = settings.LATE_REPORTING_THRESHOLD_MINUTES
        
        # Get first entry of the day
        first_entry = db.query(AttendanceEvent).filter(
            and_(
                AttendanceEvent.operator_id == operator.id,
                AttendanceEvent.event_time >= today_start,
                AttendanceEvent.event_type == "IN"
            )
        ).order_by(AttendanceEvent.event_time).first()
        
        if not first_entry:
            return None
        
        # Typical shift start: 8 AM
        shift_start = today_start.replace(hour=8, minute=0)
        time_late = (first_entry.event_time - shift_start).total_seconds() / 60
        
        # Only flag if more than threshold minutes late
        if time_late > threshold:
            return Violation(
                operator_id=operator.id,
                violation_type="late_reporting",
                violation_message=f"Reported {int(time_late)} minutes late",
                severity="low",
                status="open"
            )
        
        return None
    
    @staticmethod
    def _check_repeat_violations(
        db: Session,
        operator: Employee
    ) -> Optional[Violation]:
        """
        Rule 8: Repeated Violations
        Check if operator has more than threshold violations in recent period
        """
        threshold = settings.REPEAT_VIOLATION_THRESHOLD
        days = settings.REPEAT_VIOLATION_DAYS
        start_date = datetime.utcnow() - timedelta(days=days)
        
        violation_count = db.query(func.count(Violation.id)).filter(
            and_(
                Violation.operator_id == operator.id,
                Violation.created_at >= start_date
            )
        ).scalar()
        
        if violation_count >= threshold:
            return Violation(
                operator_id=operator.id,
                violation_type="repeat_violation",
                violation_message=f"Repeat offender: {violation_count} violations in {days} days",
                severity="high",
                status="open"
            )
        
        return None
    
    @staticmethod
    def get_violations_paginated(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        operator_id: Optional[int] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        days: int = 7
    ) -> Tuple[List[Violation], int]:
        """
        Get violations with pagination and filters
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(Violation).filter(
            Violation.created_at >= start_date
        )
        
        if operator_id:
            query = query.filter(Violation.operator_id == operator_id)
        if severity:
            query = query.filter(Violation.severity == severity)
        if status:
            query = query.filter(Violation.status == status)
        
        total_count = query.count()
        
        violations = query.order_by(
            desc(Violation.created_at)
        ).offset(skip).limit(limit).all()
        
        return violations, total_count
    
    @staticmethod
    def get_violation_stats(db: Session, days: int = 7) -> Dict:
        """
        Get violation statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(Violation).filter(
            Violation.created_at >= start_date
        )
        
        total = query.count()
        
        # By severity
        severity_stats = db.query(
            Violation.severity,
            func.count(Violation.id).label('count')
        ).filter(Violation.created_at >= start_date).group_by(
            Violation.severity
        ).all()
        
        # By type
        type_stats = db.query(
            Violation.violation_type,
            func.count(Violation.id).label('count')
        ).filter(Violation.created_at >= start_date).group_by(
            Violation.violation_type
        ).all()
        
        # Today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(func.count(Violation.id)).filter(
            Violation.created_at >= today_start
        ).scalar()
        
        # Repeat offenders (3+ violations in period)
        repeat_threshold = 3
        repeat_offenders = db.query(
            Violation.operator_id,
            Employee.full_name,
            func.count(Violation.id).label('violation_count')
        ).join(Employee).filter(
            Violation.created_at >= start_date
        ).group_by(
            Violation.operator_id, Employee.full_name
        ).having(
            func.count(Violation.id) >= repeat_threshold
        ).all()
        
        return {
            "period_days": days,
            "total_violations": total,
            "violations_today": today_count,
            "by_severity": {s[0]: s[1] for s in severity_stats},
            "by_type": {t[0]: t[1] for t in type_stats},
            "repeat_offenders": [
                {"operator_id": r[0], "name": r[1], "violation_count": r[2]}
                for r in repeat_offenders
            ]
        }
