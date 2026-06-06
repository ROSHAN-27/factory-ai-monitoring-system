"""
Movement/Location API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.schemas import OperatorMovementResponse, ZoneOccupancyResponse
from app.services.movement_service import MovementService

router = APIRouter(prefix="/api/movement", tags=["movement"])


@router.get("/operator/{operator_id}/current-zone")
def get_operator_current_zone(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """
    Get operator's current zone/location
    """
    try:
        zone_info = MovementService.get_operator_current_zone(db, operator_id)
        
        if not zone_info:
            return {
                "operator_id": operator_id,
                "current_zone": None,
                "location_name": None,
                "entry_time": None,
                "time_in_zone_minutes": None,
                "is_present": False
            }
        
        return {
            "operator_id": operator_id,
            "current_zone": zone_info["zone_name"],
            "location_name": zone_info["location_name"],
            "camera_name": zone_info["camera_name"],
            "entry_time": zone_info["entry_time"],
            "time_in_zone_minutes": zone_info["time_in_zone_minutes"],
            "is_present": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/operator/{operator_id}/zone-history")
def get_operator_zone_history(
    operator_id: int,
    days: int = Query(1, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get operator's zone movement history
    
    - **days**: Number of days to look back (default: 1)
    """
    try:
        history = MovementService.get_zone_history(db, operator_id, days)
        
        return {
            "operator_id": operator_id,
            "period_days": days,
            "total_transitions": len(history),
            "movements": history
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/zone/{zone_type}/occupancy")
def get_zone_occupancy(
    zone_type: str,
    db: Session = Depends(get_db)
):
    """
    Get current occupancy for a specific zone
    """
    try:
        occupancy = MovementService.get_zone_occupancy(db, zone_type)
        
        return {
            "timestamp": datetime.utcnow(),
            "zone_type": zone_type,
            "current_occupancy": occupancy["current_occupancy"],
            "operators_present": occupancy["operators_present"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/zones/occupancy")
def get_all_zones_occupancy(db: Session = Depends(get_db)):
    """
    Get current occupancy for all zones
    """
    try:
        occupancy_data = MovementService.get_all_zones_occupancy(db)
        
        total_occupancy = sum(z["current_occupancy"] for z in occupancy_data)
        
        return {
            "timestamp": datetime.utcnow(),
            "total_occupancy": total_occupancy,
            "zones": occupancy_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/department-occupancy")
def get_department_occupancy_snapshot(db: Session = Depends(get_db)):
    """
    Get snapshot of occupancy by department
    """
    try:
        snapshot = MovementService.get_department_occupancy_snapshot(db)
        
        return {
            "timestamp": snapshot["timestamp"],
            "total_operators_present": snapshot["total_operators_present"],
            "department_occupancy": snapshot["department_occupancy"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/operator/{operator_id}/transitions")
def get_operator_zone_transitions(
    operator_id: int,
    hours: int = Query(1, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    Detect zone transitions for an operator in the specified time window
    
    - **hours**: Number of hours to look back (default: 1, max: 168 = 7 days)
    """
    try:
        transitions = MovementService.detect_zone_transitions(db, operator_id, hours)
        
        # Filter only actual transitions
        actual_transitions = [t for t in transitions if t["is_transition"]]
        
        return {
            "operator_id": operator_id,
            "period_hours": hours,
            "total_events": len(transitions),
            "zone_transitions": len(actual_transitions),
            "transitions": actual_transitions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
