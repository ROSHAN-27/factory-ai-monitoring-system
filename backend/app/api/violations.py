"""
Violations API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas import (
    ViolationResponse, ViolationListResponse,
    ViolationUpdate, ViolationStatsResponse
)
from app.services.violation_service import ViolationService

router = APIRouter(prefix="/api/violations", tags=["violations"])


@router.get("", response_model=ViolationListResponse)
def get_violations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    operator_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get violations with pagination and filters
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return (default: 50)
    - **operator_id**: Filter by operator ID (optional)
    - **severity**: Filter by severity (low, medium, high, critical) (optional)
    - **status**: Filter by status (open, acknowledged, resolved) (optional)
    - **days**: Look back days (default: 7)
    """
    try:
        violations, total_count = ViolationService.get_violations_paginated(
            db,
            skip=skip,
            limit=limit,
            operator_id=operator_id,
            severity=severity,
            status=status,
            days=days
        )
        
        return ViolationListResponse(
            total=total_count,
            skip=skip,
            take=limit,
            items=violations
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{violation_id}", response_model=ViolationResponse)
def get_violation(
    violation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific violation with details
    """
    try:
        from app.models.violation import Violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        
        if not violation:
            raise HTTPException(status_code=404, detail="Violation not found")
        
        return violation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{violation_id}", response_model=ViolationResponse)
def update_violation(
    violation_id: int,
    update_data: ViolationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update violation status and notes
    """
    try:
        from app.models.violation import Violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        
        if not violation:
            raise HTTPException(status_code=404, detail="Violation not found")
        
        # Update fields if provided
        if update_data.status:
            violation.status = update_data.status
        if update_data.acknowledged_by:
            violation.acknowledged_by = update_data.acknowledged_by
            violation.acknowledged_at = datetime.utcnow()
        if update_data.notes:
            violation.notes = update_data.notes
        
        db.commit()
        db.refresh(violation)
        
        return violation
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/summary", response_model=ViolationStatsResponse)
def get_violation_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get violation statistics and summary
    
    - **days**: Period for statistics (default: 7 days)
    """
    try:
        stats = ViolationService.get_violation_stats(db, days)
        
        return ViolationStatsResponse(
            total_violations=stats["total_violations"],
            violations_by_type=stats["by_type"],
            violations_by_severity=stats["by_severity"],
            violations_today=stats["violations_today"],
            repeat_offenders=stats["repeat_offenders"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/operator/{operator_id}/history")
def get_operator_violations(
    operator_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get violation history for a specific operator
    
    - **days**: Look back days (default: 30)
    """
    try:
        violations, total_count = ViolationService.get_violations_paginated(
            db,
            operator_id=operator_id,
            days=days,
            limit=1000
        )
        
        return {
            "operator_id": operator_id,
            "period_days": days,
            "total_violations": total_count,
            "violations": violations
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repeat-offenders/list")
def get_repeat_offenders(
    days: int = Query(7, ge=1, le=365),
    threshold: int = Query(3, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of repeat offenders
    
    - **days**: Period to check (default: 7 days)
    - **threshold**: Minimum violations to be considered repeat offender (default: 3)
    """
    try:
        stats = ViolationService.get_violation_stats(db, days)
        
        # Filter by threshold
        offenders = [
            r for r in stats["repeat_offenders"]
            if r["violation_count"] >= threshold
        ]
        
        return {
            "period_days": days,
            "threshold": threshold,
            "count": len(offenders),
            "offenders": offenders
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
