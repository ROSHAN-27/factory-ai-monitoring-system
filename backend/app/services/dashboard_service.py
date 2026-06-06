"""
Dashboard Service - Provides real metrics for dashboard analytics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

from app.models.attendance import AttendanceEvent
from app.models.violation import Violation
from app.models.employee import Employee
from app.models.camera import Camera
from app.services.movement_service import MovementService

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for providing dashboard metrics and analytics"""
    
    @staticmethod
    def get_dashboard_metrics(db: Session) -> Dict:
        """
        Get comprehensive dashboard metrics
        
        Returns:
            Dictionary with all dashboard KPIs
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        now = datetime.utcnow()
        
        # Total operators
        total_operators = db.query(func.count(Employee.id)).filter(
            Employee.employment_status == "active"
        ).scalar()
        
        # Operators present today
        operators_present = db.query(func.count(func.distinct(AttendanceEvent.operator_id))).filter(
            and_(
                AttendanceEvent.event_time >= today_start,
                AttendanceEvent.event_type == "IN"
            )
        ).scalar() or 0
        
        # Operators absent (no entry today)
        operators_absent = total_operators - operators_present
        
        # Violations today
        violations_today = db.query(func.count(Violation.id)).filter(
            Violation.created_at >= today_start
        ).scalar() or 0
        
        # High severity violations today
        high_severity_violations = db.query(func.count(Violation.id)).filter(
            and_(
                Violation.created_at >= today_start,
                Violation.severity.in_(["high", "critical"])
            )
        ).scalar() or 0
        
        # Active cameras
        active_cameras = db.query(func.count(Camera.id)).filter(
            Camera.status == "online"
        ).scalar() or 0
        
        # Offline cameras
        offline_cameras = db.query(func.count(Camera.id)).filter(
            Camera.status != "online"
        ).scalar() or 0
        
        # Department occupancy
        dept_occupancy = DashboardService.get_department_occupancy(db)
        
        # Zone occupancy
        zone_occupancy = DashboardService.get_zone_occupancy(db)
        
        # Compliance percentage
        compliance_percentage = DashboardService.calculate_compliance_percentage(db)
        
        return {
            "timestamp": now,
            "total_operators": total_operators,
            "operators_present_today": operators_present,
            "operators_absent_today": operators_absent,
            "violations_today": violations_today,
            "high_severity_violations": high_severity_violations,
            "active_cameras": active_cameras,
            "offline_cameras": offline_cameras,
            "department_occupancy": dept_occupancy,
            "zone_occupancy": zone_occupancy,
            "compliance_percentage": compliance_percentage
        }
    
    @staticmethod
    def get_department_occupancy(db: Session) -> Dict:
        """
        Get current occupancy by department
        
        Returns:
            Dictionary mapping department to occupant count
        """
        occupancy_snapshot = MovementService.get_department_occupancy_snapshot(db)
        return occupancy_snapshot.get("department_occupancy", {})
    
    @staticmethod
    def get_zone_occupancy(db: Session) -> Dict:
        """
        Get current occupancy by zone
        
        Returns:
            Dictionary mapping zone to occupant count
        """
        zone_data = MovementService.get_all_zones_occupancy(db)
        
        occupancy = {}
        for zone in zone_data:
            occupancy[zone["zone_type"]] = zone["current_occupancy"]
        
        return occupancy
    
    @staticmethod
    def calculate_compliance_percentage(db: Session) -> float:
        """
        Calculate overall compliance percentage
        
        Formula: (Total operators - Operators with violations today) / Total operators
        
        Returns:
            Compliance percentage (0-100)
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_present = db.query(func.count(func.distinct(AttendanceEvent.operator_id))).filter(
            and_(
                AttendanceEvent.event_time >= today_start,
                AttendanceEvent.event_type == "IN"
            )
        ).scalar() or 0
        
        if total_present == 0:
            return 100.0
        
        operators_with_violations = db.query(func.count(func.distinct(Violation.operator_id))).filter(
            Violation.created_at >= today_start
        ).scalar() or 0
        
        compliant_operators = total_present - operators_with_violations
        compliance = (compliant_operators / total_present) * 100 if total_present > 0 else 100
        
        return round(compliance, 2)
    
    @staticmethod
    def get_hourly_trends(db: Session, hours: int = 24) -> List[Dict]:
        """
        Get hourly event and violation trends
        
        Returns:
            List of hourly trend data
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get hourly event counts
        event_query = db.query(
            func.date_trunc('hour', AttendanceEvent.event_time).label('hour'),
            func.count(AttendanceEvent.id).label('total_events'),
            func.sum(
                func.cast(
                    (AttendanceEvent.event_type == 'IN'),
                    type_=type(1)
                )
            ).label('in_events'),
            func.sum(
                func.cast(
                    (AttendanceEvent.event_type == 'OUT'),
                    type_=type(1)
                )
            ).label('out_events')
        ).filter(
            AttendanceEvent.event_time >= start_time
        ).group_by('hour').order_by('hour').all()
        
        # Get hourly violation counts
        violation_query = db.query(
            func.date_trunc('hour', Violation.created_at).label('hour'),
            func.count(Violation.id).label('violation_count')
        ).filter(
            Violation.created_at >= start_time
        ).group_by('hour').all()
        
        # Merge data
        violations_by_hour = {v[0]: v[1] for v in violation_query}
        
        trends = []
        for event in event_query:
            hour = event[0]
            trends.append({
                "hour": hour.isoformat() if hour else None,
                "event_count": event[1] or 0,
                "in_events": event[2] or 0,
                "out_events": event[3] or 0,
                "violation_count": violations_by_hour.get(hour, 0)
            })
        
        return trends
    
    @staticmethod
    def get_daily_trends(db: Session, days: int = 30) -> List[Dict]:
        """
        Get daily event and violation trends
        
        Returns:
            List of daily trend data
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily event counts
        event_query = db.query(
            func.date(AttendanceEvent.event_time).label('day'),
            func.count(AttendanceEvent.id).label('total_events'),
            func.sum(
                func.cast(
                    (AttendanceEvent.event_type == 'IN'),
                    type_=type(1)
                )
            ).label('in_events'),
            func.sum(
                func.cast(
                    (AttendanceEvent.event_type == 'OUT'),
                    type_=type(1)
                )
            ).label('out_events')
        ).filter(
            AttendanceEvent.event_time >= start_date
        ).group_by('day').order_by('day').all()
        
        # Get daily violation counts
        violation_query = db.query(
            func.date(Violation.created_at).label('day'),
            func.count(Violation.id).label('violation_count')
        ).filter(
            Violation.created_at >= start_date
        ).group_by('day').all()
        
        # Merge data
        violations_by_day = {v[0]: v[1] for v in violation_query}
        
        trends = []
        for event in event_query:
            day = event[0]
            trends.append({
                "date": day.isoformat() if day else None,
                "event_count": event[1] or 0,
                "in_events": event[2] or 0,
                "out_events": event[3] or 0,
                "violation_count": violations_by_day.get(day, 0)
            })
        
        return trends
    
    @staticmethod
    def get_department_stats(db: Session) -> Dict:
        """
        Get statistics per department
        
        Returns:
            Dictionary with per-department metrics
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get present operators by department
        dept_stats = db.query(
            Employee.department,
            func.count(func.distinct(AttendanceEvent.operator_id)).label('present_count'),
            func.count(Violation.id).label('violation_count')
        ).join(AttendanceEvent, AttendanceEvent.operator_id == Employee.id).outerjoin(
            Violation,
            and_(
                Violation.operator_id == Employee.id,
                Violation.created_at >= today_start
            )
        ).filter(
            and_(
                AttendanceEvent.event_time >= today_start,
                AttendanceEvent.event_type == "IN"
            )
        ).group_by(Employee.department).all()
        
        stats = {}
        for dept, present, violations in dept_stats:
            dept_name = dept or "Unassigned"
            compliance = max(0, 100 - (violations / present * 100)) if present > 0 else 100
            stats[dept_name] = {
                "operators_present": present,
                "violations_today": violations,
                "compliance_percentage": round(compliance, 2)
            }
        
        return stats
    
    @staticmethod
    def get_violation_summary(db: Session) -> Dict:
        """
        Get violation type summary with counts
        
        Returns:
            Dictionary with violation breakdown
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        violation_summary = db.query(
            Violation.violation_type,
            Violation.severity,
            func.count(Violation.id).label('count')
        ).filter(
            Violation.created_at >= today_start
        ).group_by(Violation.violation_type, Violation.severity).all()
        
        summary = {}
        for vtype, severity, count in violation_summary:
            if vtype not in summary:
                summary[vtype] = {}
            summary[vtype][severity] = count
        
        return summary
    
    @staticmethod
    def get_top_violators(db: Session, limit: int = 10, days: int = 7) -> List[Dict]:
        """
        Get operators with most violations
        
        Returns:
            List of operator violation records
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        top_violators = db.query(
            Violation.operator_id,
            Employee.full_name,
            Employee.department,
            func.count(Violation.id).label('violation_count'),
            func.max(Violation.created_at).label('last_violation')
        ).join(Employee).filter(
            Violation.created_at >= start_date
        ).group_by(
            Violation.operator_id, Employee.full_name, Employee.department
        ).order_by(
            desc(func.count(Violation.id))
        ).limit(limit).all()
        
        return [
            {
                "operator_id": v[0],
                "operator_name": v[1],
                "department": v[2],
                "violation_count": v[3],
                "last_violation": v[4]
            }
            for v in top_violators
        ]
    
    @staticmethod
    def get_attendance_summary(db: Session, date: datetime = None) -> Dict:
        """
        Get attendance summary for a specific date
        
        Returns:
            Dictionary with attendance statistics
        """
        if not date:
            date = datetime.utcnow()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        total_operators = db.query(func.count(Employee.id)).filter(
            Employee.employment_status == "active"
        ).scalar() or 0
        
        operators_present = db.query(func.count(func.distinct(AttendanceEvent.operator_id))).filter(
            and_(
                AttendanceEvent.event_time >= date_start,
                AttendanceEvent.event_time <= date_end,
                AttendanceEvent.event_type == "IN"
            )
        ).scalar() or 0
        
        total_events = db.query(func.count(AttendanceEvent.id)).filter(
            and_(
                AttendanceEvent.event_time >= date_start,
                AttendanceEvent.event_time <= date_end
            )
        ).scalar() or 0
        
        avg_confidence = db.query(func.avg(AttendanceEvent.confidence_score)).filter(
            and_(
                AttendanceEvent.event_time >= date_start,
                AttendanceEvent.event_time <= date_end,
                AttendanceEvent.confidence_score.isnot(None)
            )
        ).scalar() or 0.0
        
        return {
            "date": date.date().isoformat(),
            "total_operators": total_operators,
            "operators_present": operators_present,
            "operators_absent": total_operators - operators_present,
            "attendance_percentage": round((operators_present / total_operators * 100) if total_operators > 0 else 0, 2),
            "total_events": total_events,
            "average_confidence": round(avg_confidence, 4)
        }
