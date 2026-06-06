"""
Dashboard API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.schemas import (
    DashboardMetricsResponse, DashboardTrendsResponse, DashboardTrendResponse
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard metrics and KPIs
    
    Returns:
    - Total operators and present count
    - Violations (today and high severity)
    - Camera status
    - Occupancy by department and zone
    - Overall compliance percentage
    """
    try:
        metrics = DashboardService.get_dashboard_metrics(db)
        
        return DashboardMetricsResponse(
            timestamp=metrics["timestamp"],
            total_operators=metrics["total_operators"],
            operators_present_today=metrics["operators_present_today"],
            operators_absent_today=metrics["operators_absent_today"],
            violations_today=metrics["violations_today"],
            high_severity_violations=metrics["high_severity_violations"],
            active_cameras=metrics["active_cameras"],
            offline_cameras=metrics["offline_cameras"],
            department_occupancy=metrics["department_occupancy"],
            zone_occupancy=metrics["zone_occupancy"],
            compliance_percentage=metrics["compliance_percentage"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trends/hourly", response_model=DashboardTrendsResponse)
def get_hourly_trends(
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """
    Get hourly event and violation trends
    
    - **hours**: Number of hours to look back (default: 24, max: 720 = 30 days)
    """
    try:
        trends = DashboardService.get_hourly_trends(db, hours)
        
        return DashboardTrendsResponse(
            period="hourly",
            trends=[DashboardTrendResponse(**t) for t in trends]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trends/daily", response_model=DashboardTrendsResponse)
def get_daily_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get daily event and violation trends
    
    - **days**: Number of days to look back (default: 30, max: 365)
    """
    try:
        trends = DashboardService.get_daily_trends(db, days)
        
        trend_responses = []
        for t in trends:
            tr = DashboardTrendResponse(
                date=t.get("date"),
                event_count=t.get("event_count", 0),
                violation_count=t.get("violation_count", 0),
                in_events=t.get("in_events", 0),
                out_events=t.get("out_events", 0)
            )
            trend_responses.append(tr)
        
        return DashboardTrendsResponse(
            period="daily",
            trends=trend_responses
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/departments")
def get_department_stats(db: Session = Depends(get_db)):
    """
    Get per-department statistics
    
    Returns occupancy, violations, and compliance percentage by department
    """
    try:
        stats = DashboardService.get_department_stats(db)
        
        return {
            "timestamp": datetime.utcnow(),
            "departments": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/violations/summary")
def get_violation_summary(db: Session = Depends(get_db)):
    """
    Get violation type summary with severity breakdown
    """
    try:
        summary = DashboardService.get_violation_summary(db)
        
        return {
            "timestamp": datetime.utcnow(),
            "violation_types": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/top-violators")
def get_top_violators(
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get operators with most violations
    
    - **limit**: Number of violators to return (default: 10)
    - **days**: Period to check (default: 7 days)
    """
    try:
        violators = DashboardService.get_top_violators(db, limit, days)
        
        return {
            "timestamp": datetime.utcnow(),
            "period_days": days,
            "count": len(violators),
            "top_violators": violators
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/attendance-summary")
def get_attendance_summary(
    date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get attendance summary for a specific date
    
    - **date**: Date in YYYY-MM-DD format (optional, default: today)
    """
    try:
        summary_date = None
        if date:
            try:
                summary_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        summary = DashboardService.get_attendance_summary(db, summary_date)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compliance-score")
def get_compliance_score(db: Session = Depends(get_db)):
    """
    Get overall compliance percentage
    """
    try:
        compliance = DashboardService.calculate_compliance_percentage(db)
        
        return {
            "timestamp": datetime.utcnow(),
            "compliance_percentage": compliance,
            "status": (
                "excellent" if compliance >= 95
                else "good" if compliance >= 80
                else "fair" if compliance >= 60
                else "poor"
            )
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/zone-occupancy")
def get_zone_occupancy(db: Session = Depends(get_db)):
    """
    Get real-time occupancy across all zones
    """
    try:
        from app.services.movement_service import MovementService
        occupancy = MovementService.get_all_zones_occupancy(db)
        
        return {
            "timestamp": datetime.utcnow(),
            "zones": occupancy,
            "total_occupancy": sum(z["current_occupancy"] for z in occupancy)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
