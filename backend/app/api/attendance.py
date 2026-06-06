"""
Attendance API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas import (
    AttendanceEventCreate, AttendanceEventResponse,
    AttendanceListResponse, ErrorResponse
)
from app.services.attendance_service import AttendanceService
from app.services.violation_service import ViolationService

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.post("/events", response_model=AttendanceEventResponse, status_code=201)
def create_attendance_event(
    event_data: AttendanceEventCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new attendance event
    """
    try:
        # Create attendance event
        event = AttendanceService.create_event(db, event_data)
        
        # Check for violations
        violations = ViolationService.check_event_for_violations(db, event)
        
        return event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events", response_model=AttendanceListResponse)
def get_attendance_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    operator_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    event_type: Optional[str] = None,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """
    Get attendance events with pagination and filters
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 50, max: 500)
    - **operator_id**: Filter by operator ID (optional)
    - **camera_id**: Filter by camera ID (optional)
    - **event_type**: Filter by IN or OUT (optional)
    - **hours**: Look back hours (default: 24, max: 720 = 30 days)
    """
    try:
        events, total_count = AttendanceService.get_events_paginated(
            db, skip=skip, limit=limit,
            operator_id=operator_id,
            camera_id=camera_id,
            event_type=event_type,
            hours=hours
        )
        
        return AttendanceListResponse(
            total=total_count,
            skip=skip,
            take=limit,
            items=events
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/daily-summary")
def get_daily_summary(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get daily attendance summary
    
    - **date**: Date in YYYY-MM-DD format (optional, default: today)
    """
    try:
        summary_date = None
        if date:
            summary_date = datetime.strptime(date, "%Y-%m-%d")
        
        summary = AttendanceService.get_daily_summary(db, summary_date)
        return summary
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/operator/{operator_id}/status")
def get_operator_current_status(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """
    Get operator's current presence status for today
    """
    try:
        status = AttendanceService.get_operator_current_status(db, operator_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/operator/{operator_id}/history")
def get_operator_history(
    operator_id: int,
    days: int = Query(7, ge=1, le=180),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get operator's attendance history
    
    - **days**: Number of days to look back (default: 7)
    - **limit**: Maximum records to return (default: 100)
    """
    try:
        events = AttendanceService.get_operator_history(db, operator_id, days, limit)
        return {
            "operator_id": operator_id,
            "period_days": days,
            "total_records": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/present-today")
def get_operators_present_today(db: Session = Depends(get_db)):
    """
    Get list of operators currently present in factory
    """
    try:
        operators = AttendanceService.get_operators_present_today(db)
        return {
            "timestamp": datetime.utcnow(),
            "count": len(operators),
            "operators": operators
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))