"""
Attendance Service - Handles attendance event logging and retrieval
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import logging

from app.models.attendance import AttendanceEvent
from app.models.employee import Employee
from app.models.camera import Camera
from app.schemas import AttendanceEventCreate, AttendanceEventResponse

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service for managing attendance events"""
    
    @staticmethod
    def create_event(
        db: Session,
        event_data: AttendanceEventCreate
    ) -> AttendanceEvent:
        """
        Create a new attendance event
        """
        db_event = AttendanceEvent(
            operator_id=event_data.operator_id,
            camera_id=event_data.camera_id,
            zone_type=event_data.zone_type,
            event_type=event_data.event_type,
            confidence_score=event_data.confidence_score,
            snapshot_path=event_data.snapshot_path,
            event_time=datetime.utcnow()
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Created attendance event: {db_event}")
        return db_event
    
    @staticmethod
    def get_events_paginated(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        operator_id: Optional[int] = None,
        camera_id: Optional[int] = None,
        event_type: Optional[str] = None,
        hours: int = 24
    ) -> Tuple[List[AttendanceEvent], int]:
        """
        Get attendance events with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return
            operator_id: Filter by operator
            camera_id: Filter by camera
            event_type: Filter by IN/OUT
            hours: Look back hours (default 24)
        
        Returns:
            Tuple of (events list, total count)
        """
        time_filter = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(AttendanceEvent).filter(
            AttendanceEvent.event_time >= time_filter
        )
        
        if operator_id:
            query = query.filter(AttendanceEvent.operator_id == operator_id)
        if camera_id:
            query = query.filter(AttendanceEvent.camera_id == camera_id)
        if event_type:
            query = query.filter(AttendanceEvent.event_type == event_type)
        
        total_count = query.count()
        
        events = query.order_by(
            desc(AttendanceEvent.event_time)
        ).offset(skip).limit(limit).all()
        
        return events, total_count
    
    @staticmethod
    def get_daily_summary(
        db: Session,
        date: Optional[datetime] = None
    ) -> dict:
        """
        Get daily attendance summary
        
        Args:
            db: Database session
            date: Date to summarize (default today)
        
        Returns:
            Dictionary with daily statistics
        """
        if not date:
            date = datetime.utcnow().date()
        else:
            date = date.date()
        
        # Define date range for UTC dates
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())
        
        query = db.query(AttendanceEvent).filter(
            and_(
                AttendanceEvent.event_time >= day_start,
                AttendanceEvent.event_time <= day_end
            )
        )
        
        total_events = query.count()
        in_events = query.filter(AttendanceEvent.event_type == "IN").count()
        out_events = query.filter(AttendanceEvent.event_type == "OUT").count()
        
        # Get unique operators who logged in
        unique_operators = db.query(
            func.count(func.distinct(AttendanceEvent.operator_id))
        ).filter(
            and_(
                AttendanceEvent.event_time >= day_start,
                AttendanceEvent.event_time <= day_end,
                AttendanceEvent.event_type == "IN"
            )
        ).scalar()
        
        return {
            "date": date.isoformat(),
            "total_events": total_events,
            "in_events": in_events,
            "out_events": out_events,
            "unique_operators": unique_operators or 0,
            "average_confidence": db.query(
                func.avg(AttendanceEvent.confidence_score)
            ).filter(
                and_(
                    AttendanceEvent.event_time >= day_start,
                    AttendanceEvent.event_time <= day_end,
                    AttendanceEvent.confidence_score.isnot(None)
                )
            ).scalar() or 0.0
        }
    
    @staticmethod
    def get_operator_current_status(
        db: Session,
        operator_id: int
    ) -> dict:
        """
        Get operator's current presence status
        
        Args:
            db: Database session
            operator_id: Operator ID
        
        Returns:
            Dictionary with current status
        """
        # Get last event for today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        last_event = db.query(AttendanceEvent).filter(
            and_(
                AttendanceEvent.operator_id == operator_id,
                AttendanceEvent.event_time >= today_start
            )
        ).order_by(desc(AttendanceEvent.event_time)).first()
        
        if not last_event:
            return {
                "operator_id": operator_id,
                "is_present": False,
                "last_event": None,
                "time_in_factory": None
            }
        
        is_present = last_event.event_type == "IN"
        
        # Calculate time at factory if present
        time_in_factory = None
        if is_present:
            time_in_factory = (datetime.utcnow() - last_event.event_time).total_seconds() / 60
        
        return {
            "operator_id": operator_id,
            "is_present": is_present,
            "last_event_type": last_event.event_type,
            "last_event_time": last_event.event_time,
            "time_in_factory_minutes": time_in_factory
        }
    
    @staticmethod
    def get_operator_history(
        db: Session,
        operator_id: int,
        days: int = 7,
        limit: int = 100
    ) -> List[AttendanceEvent]:
        """
        Get operator's attendance history
        
        Args:
            db: Database session
            operator_id: Operator ID
            days: Number of days to look back
            limit: Maximum records to return
        
        Returns:
            List of attendance events
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        events = db.query(AttendanceEvent).filter(
            and_(
                AttendanceEvent.operator_id == operator_id,
                AttendanceEvent.event_time >= start_date
            )
        ).order_by(desc(AttendanceEvent.event_time)).limit(limit).all()
        
        return events
    
    @staticmethod
    def get_operators_present_today(db: Session) -> List[dict]:
        """
        Get list of operators currently present in factory
        
        Returns:
            List of operator dictionaries with current status
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get operators with IN as their last event today
        subquery = db.query(
            AttendanceEvent.operator_id,
            func.max(AttendanceEvent.event_time).label('last_time')
        ).filter(
            AttendanceEvent.event_time >= today_start
        ).group_by(AttendanceEvent.operator_id).subquery()
        
        present_operators = db.query(
            AttendanceEvent.operator_id,
            AttendanceEvent.event_type,
            AttendanceEvent.event_time,
            Employee.full_name
        ).join(Employee).join(
            subquery,
            and_(
                AttendanceEvent.operator_id == subquery.c.operator_id,
                AttendanceEvent.event_time == subquery.c.last_time
            )
        ).filter(
            AttendanceEvent.event_type == "IN"
        ).all()
        
        result = []
        for event in present_operators:
            result.append({
                "operator_id": event.operator_id,
                "operator_name": event.full_name,
                "status": "present",
                "last_event_time": event.event_time
            })
        
        return result
