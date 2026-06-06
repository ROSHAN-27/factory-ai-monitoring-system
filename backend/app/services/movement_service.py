"""
Movement Service - Tracks operator zone transitions and current locations
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging

from app.models.attendance import AttendanceEvent
from app.models.employee import Employee
from app.models.camera import Camera
from app.models.zone import Zone

logger = logging.getLogger(__name__)


class MovementService:
    """Service for tracking operator movements and zone transitions"""
    
    @staticmethod
    def get_operator_current_zone(
        db: Session,
        operator_id: int
    ) -> Optional[Dict]:
        """
        Get operator's current zone based on latest events
        
        Returns:
            Dictionary with current zone info or None
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        last_in_event = db.query(AttendanceEvent).filter(
            and_(
                AttendanceEvent.operator_id == operator_id,
                AttendanceEvent.event_type == "IN",
                AttendanceEvent.event_time >= today_start
            )
        ).order_by(desc(AttendanceEvent.event_time)).first()
        
        if not last_in_event:
            return None
        
        # Check if there's a matching OUT event after this IN
        last_out_event = db.query(AttendanceEvent).filter(
            and_(
                AttendanceEvent.operator_id == operator_id,
                AttendanceEvent.event_type == "OUT",
                AttendanceEvent.event_time > last_in_event.event_time,
                AttendanceEvent.event_time >= today_start
            )
        ).order_by(desc(AttendanceEvent.event_time)).first()
        
        # If there's an OUT after IN, operator is not in this zone
        if last_out_event:
            return None
        
        # Get zone name from camera
        camera = db.query(Camera).filter(Camera.id == last_in_event.camera_id).first()
        
        if not camera:
            return None
        
        time_in_zone = (datetime.utcnow() - last_in_event.event_time).total_seconds() / 60
        
        return {
            "zone_name": camera.zone_type,
            "camera_name": camera.camera_name,
            "location_name": camera.location_name,
            "entry_time": last_in_event.event_time,
            "time_in_zone_minutes": round(time_in_zone, 2)
        }
    
    @staticmethod
    def get_zone_occupancy(
        db: Session,
        zone_type: str
    ) -> Dict:
        """
        Get current occupancy of a specific zone
        
        Returns:
            Dictionary with zone occupancy info
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all cameras in this zone
        cameras = db.query(Camera).filter(Camera.zone_type == zone_type).all()
        camera_ids = [c.id for c in cameras]
        
        if not camera_ids:
            return {
                "zone_type": zone_type,
                "current_occupancy": 0,
                "operators_present": []
            }
        
        # Find operators currently in this zone
        # They have IN event but no subsequent OUT event in this zone today
        
        subquery = db.query(
            AttendanceEvent.operator_id,
            func.max(AttendanceEvent.event_time).label('last_time')
        ).filter(
            and_(
                AttendanceEvent.camera_id.in_(camera_ids),
                AttendanceEvent.event_time >= today_start
            )
        ).group_by(AttendanceEvent.operator_id).subquery()
        
        operators_in_zone = db.query(
            AttendanceEvent.operator_id,
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
        
        operator_ids = [op[0] for op in operators_in_zone]
        operator_names = {op[0]: op[1] for op in operators_in_zone}
        
        return {
            "zone_type": zone_type,
            "current_occupancy": len(operator_ids),
            "operators_present": [
                {"id": op_id, "name": operator_names[op_id]}
                for op_id in operator_ids
            ]
        }
    
    @staticmethod
    def get_all_zones_occupancy(db: Session) -> List[Dict]:
        """
        Get occupancy for all zones
        
        Returns:
            List of zone occupancy information
        """
        # Get all unique zone types
        zones = db.query(Camera.zone_type).distinct().all()
        zone_types = [z[0] for z in zones if z[0]]
        
        occupancy_data = []
        for zone_type in zone_types:
            occupancy_data.append(
                MovementService.get_zone_occupancy(db, zone_type)
            )
        
        return occupancy_data
    
    @staticmethod
    def get_zone_history(
        db: Session,
        operator_id: int,
        days: int = 1
    ) -> List[Dict]:
        """
        Get operator's zone movement history
        
        Returns:
            List of zone transitions chronologically
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        events = db.query(AttendanceEvent).filter(
            and_(
                AttendanceEvent.operator_id == operator_id,
                AttendanceEvent.event_time >= start_date
            )
        ).order_by(AttendanceEvent.event_time).all()
        
        # Pair IN/OUT events to create transitions
        history = []
        i = 0
        while i < len(events):
            if i + 1 < len(events) and events[i].event_type == "IN":
                entry_event = events[i]
                exit_event = events[i + 1] if events[i + 1].event_type == "OUT" else None
                
                # Get zone info
                camera = db.query(Camera).filter(
                    Camera.id == entry_event.camera_id
                ).first()
                
                history.append({
                    "zone_type": camera.zone_type if camera else "unknown",
                    "location_name": camera.location_name if camera else "unknown",
                    "entry_time": entry_event.event_time,
                    "exit_time": exit_event.event_time if exit_event else None,
                    "dwell_time_minutes": (
                        (exit_event.event_time - entry_event.event_time).total_seconds() / 60
                        if exit_event else None
                    )
                })
                
                i += 2 if exit_event else 1
            else:
                i += 1
        
        return history
    
    @staticmethod
    def get_department_occupancy_snapshot(db: Session) -> Dict:
        """
        Get current snapshot of all operators by department
        
        Returns:
            Dictionary mapping department to operator list
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all present operators with their current zone
        subquery = db.query(
            AttendanceEvent.operator_id,
            func.max(AttendanceEvent.event_time).label('last_time')
        ).filter(
            and_(
                AttendanceEvent.event_time >= today_start
            )
        ).group_by(AttendanceEvent.operator_id).subquery()
        
        present_events = db.query(
            AttendanceEvent.operator_id,
            AttendanceEvent.event_type,
            AttendanceEvent.camera_id,
            Employee.department
        ).join(Employee).join(
            subquery,
            and_(
                AttendanceEvent.operator_id == subquery.c.operator_id,
                AttendanceEvent.event_time == subquery.c.last_time
            )
        ).filter(
            AttendanceEvent.event_type == "IN"
        ).all()
        
        # Group by department
        dept_occupancy = {}
        for event in present_events:
            dept = event.department or "Unassigned"
            if dept not in dept_occupancy:
                dept_occupancy[dept] = []
            dept_occupancy[dept].append(event.operator_id)
        
        return {
            "timestamp": datetime.utcnow(),
            "department_occupancy": {
                dept: len(ops) for dept, ops in dept_occupancy.items()
            },
            "total_operators_present": sum(len(ops) for ops in dept_occupancy.values())
        }
    
    @staticmethod
    def detect_zone_transitions(
        db: Session,
        operator_id: int,
        hours: int = 1
    ) -> List[Dict]:
        """
        Detect zone transitions within the specified time window
        Used for compliance rule checking
        
        Returns:
            List of zone transitions
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        events = db.query(
            AttendanceEvent.id,
            AttendanceEvent.event_type,
            AttendanceEvent.event_time,
            Camera.zone_type,
            Camera.camera_name
        ).join(Camera).filter(
            and_(
                AttendanceEvent.operator_id == operator_id,
                AttendanceEvent.event_time >= start_time
            )
        ).order_by(AttendanceEvent.event_time).all()
        
        transitions = []
        for i in range(len(events)):
            event = events[i]
            prev_zone = events[i-1][3] if i > 0 else None
            
            transitions.append({
                "event_id": event.id,
                "event_type": event.event_type,
                "event_time": event.event_time,
                "zone": event.zone_type,
                "camera": event.camera_name,
                "prev_zone": prev_zone,
                "is_transition": i > 0 and events[i-1][3] != event.zone_type
            })
        
        return transitions
