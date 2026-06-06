"""
Employee/Operator Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.employee import Employee
from app.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse
)

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new employee/operator
    """
    try:
        # Check if employee_id already exists
        existing = db.query(Employee).filter(
            Employee.employee_id == employee_data.employee_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Employee ID {employee_data.employee_id} already exists"
            )
        
        db_employee = Employee(**employee_data.dict())
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        
        return db_employee
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[EmployeeResponse])
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = None,
    shift_name: Optional[str] = None,
    employment_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of employees with optional filters
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return (default: 100)
    - **department**: Filter by department (optional)
    - **shift_name**: Filter by shift (optional)
    - **employment_status**: Filter by status (active, inactive, terminated) (optional)
    """
    try:
        query = db.query(Employee)
        
        if department:
            query = query.filter(Employee.department == department)
        if shift_name:
            query = query.filter(Employee.shift_name == shift_name)
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status)
        
        employees = query.offset(skip).limit(limit).all()
        return employees
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific employee by ID
    """
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by-employee-id/{emp_id}", response_model=EmployeeResponse)
def get_employee_by_employee_id(
    emp_id: str,
    db: Session = Depends(get_db)
):
    """
    Get employee by employee ID (e.g., EMP001)
    """
    try:
        employee = db.query(Employee).filter(Employee.employee_id == emp_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    update_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update employee information
    """
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(employee, key, value)
        
        db.commit()
        db.refresh(employee)
        
        return employee
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete/deactivate an employee
    """
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Soft delete - mark as terminated
        employee.employment_status = "terminated"
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{employee_id}/attendance-history")
def get_employee_attendance(
    employee_id: int,
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get employee's attendance history
    
    - **days**: Number of days to look back (default: 7)
    - **limit**: Maximum records to return (default: 100)
    """
    try:
        from app.services.attendance_service import AttendanceService
        
        events = AttendanceService.get_operator_history(db, employee_id, days, limit)
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return {
            "employee_id": employee_id,
            "employee_name": employee.full_name,
            "period_days": days,
            "total_records": len(events),
            "events": events
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{employee_id}/violations")
def get_employee_violations(
    employee_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get employee's violation history
    
    - **days**: Number of days to look back (default: 30)
    """
    try:
        from app.services.violation_service import ViolationService
        
        violations, total = ViolationService.get_violations_paginated(
            db,
            operator_id=employee_id,
            days=days,
            limit=1000
        )
        
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return {
            "employee_id": employee_id,
            "employee_name": employee.full_name,
            "period_days": days,
            "total_violations": total,
            "violations": violations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{employee_id}/upload-face", status_code=200)
def upload_employee_face(
    employee_id: int,
    file_path: str,
    db: Session = Depends(get_db)
):
    """
    Upload/update employee face image
    
    - **file_path**: Path to the face image file
    """
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Store the file path
        employee.face_image_path = file_path
        db.commit()
        
        return {
            "employee_id": employee_id,
            "message": "Face image uploaded successfully",
            "face_image_path": file_path
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/summary")
def get_employee_stats(db: Session = Depends(get_db)):
    """
    Get employee statistics
    """
    try:
        total_employees = db.query(Employee).count()
        
        active_employees = db.query(Employee).filter(
            Employee.employment_status == "active"
        ).count()
        
        by_department = db.query(
            Employee.department,
            type(total_employees)(db.query(Employee).filter(
                Employee.department == Employee.department
            ).count())
        ).group_by(Employee.department).all()
        
        by_shift = db.query(
            Employee.shift_name,
            type(total_employees)(db.query(Employee).filter(
                Employee.shift_name == Employee.shift_name
            ).count())
        ).group_by(Employee.shift_name).all()
        
        return {
            "timestamp": datetime.utcnow(),
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": total_employees - active_employees,
            "by_department": {dept or "Unassigned": count for dept, count in by_department if dept},
            "by_shift": {shift or "Unassigned": count for shift, count in by_shift if shift}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
