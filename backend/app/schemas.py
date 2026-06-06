"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# ==================== EMPLOYEE SCHEMAS ====================

class EmployeeBase(BaseModel):
    """Base employee schema with common fields"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    shift_name: Optional[str] = Field(None, max_length=50)
    face_image_path: Optional[str] = None
    supervisor_id: Optional[int] = None
    employment_status: str = Field("active", max_length=20)
    line_section: Optional[str] = Field(None, max_length=100)


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee"""
    @validator('employee_id')
    def employee_id_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError('employee_id must be alphanumeric with optional dashes/underscores')
        return v


class EmployeeUpdate(BaseModel):
    """Schema for updating employee"""
    full_name: Optional[str] = None
    department: Optional[str] = None
    shift_name: Optional[str] = None
    face_image_path: Optional[str] = None
    supervisor_id: Optional[int] = None
    employment_status: Optional[str] = None
    line_section: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CAMERA SCHEMAS ====================

class CameraBase(BaseModel):
    """Base camera schema"""
    camera_name: str = Field(..., min_length=1, max_length=100)
    rtsp_url: Optional[str] = None
    location_name: Optional[str] = Field(None, max_length=100)
    zone_type: Optional[str] = Field(None, max_length=50)


class CameraCreate(CameraBase):
    """Schema for creating a camera"""
    pass


class CameraUpdate(BaseModel):
    """Schema for updating camera"""
    camera_name: Optional[str] = None
    rtsp_url: Optional[str] = None
    location_name: Optional[str] = None
    zone_type: Optional[str] = None
    status: Optional[str] = None


class CameraResponse(CameraBase):
    """Schema for camera response"""
    id: int
    status: str
    fps: Optional[int] = None
    accuracy_percent: Optional[int] = None
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ZONE SCHEMAS ====================

class ZoneBase(BaseModel):
    """Base zone schema"""
    zone_name: str = Field(..., min_length=1, max_length=100)
    zone_type: str = Field(..., max_length=50)  # entry, department, common
    description: Optional[str] = None


class ZoneCreate(ZoneBase):
    """Schema for creating a zone"""
    pass


class ZoneUpdate(BaseModel):
    """Schema for updating zone"""
    zone_name: Optional[str] = None
    zone_type: Optional[str] = None
    description: Optional[str] = None


class ZoneResponse(ZoneBase):
    """Schema for zone response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ATTENDANCE SCHEMAS ====================

class AttendanceEventBase(BaseModel):
    """Base attendance event schema"""
    operator_id: int
    camera_id: int
    event_type: str = Field(..., regex="^(IN|OUT)$")
    zone_type: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    snapshot_path: Optional[str] = None


class AttendanceEventCreate(AttendanceEventBase):
    """Schema for creating attendance event"""
    pass


class AttendanceEventResponse(AttendanceEventBase):
    """Schema for attendance event response"""
    id: int
    event_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    """Schema for list of attendance events with pagination"""
    total: int
    skip: int
    take: int
    items: List[AttendanceEventResponse]


# ==================== VIOLATION SCHEMAS ====================

class ViolationBase(BaseModel):
    """Base violation schema"""
    operator_id: int
    violation_type: str = Field(..., max_length=100)
    violation_message: Optional[str] = None
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    related_event_id: Optional[int] = None
    notes: Optional[str] = None


class ViolationCreate(ViolationBase):
    """Schema for creating violation"""
    pass


class ViolationUpdate(BaseModel):
    """Schema for updating violation"""
    status: Optional[str] = Field(None, regex="^(open|acknowledged|resolved)$")
    acknowledged_by: Optional[str] = None
    notes: Optional[str] = None


class ViolationResponse(ViolationBase):
    """Schema for violation response"""
    id: int
    status: str
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ViolationListResponse(BaseModel):
    """Schema for list of violations with pagination"""
    total: int
    skip: int
    take: int
    items: List[ViolationResponse]


class ViolationStatsResponse(BaseModel):
    """Schema for violation statistics"""
    total_violations: int
    violations_by_type: dict
    violations_by_severity: dict
    violations_today: int
    repeat_offenders: List[dict]


# ==================== DASHBOARD SCHEMAS ====================

class DashboardMetricsResponse(BaseModel):
    """Schema for dashboard metrics"""
    total_operators: int
    operators_present_today: int
    operators_absent_today: int
    violations_today: int
    high_severity_violations: int
    active_cameras: int
    offline_cameras: int
    department_occupancy: dict  # {dept_name: count}
    zone_occupancy: dict  # {zone_name: count}
    compliance_percentage: float
    timestamp: datetime


class DashboardTrendResponse(BaseModel):
    """Schema for trend data (hourly/daily)"""
    hour: Optional[int] = None
    date: Optional[str] = None
    event_count: int
    violation_count: int
    in_events: int
    out_events: int


class DashboardTrendsResponse(BaseModel):
    """Schema for trends response"""
    period: str  # hourly, daily
    trends: List[DashboardTrendResponse]


# ==================== MOVEMENT SCHEMAS ====================

class OperatorMovementResponse(BaseModel):
    """Schema for operator current location"""
    operator_id: int
    operator_name: str
    current_zone: Optional[str] = None
    current_zone_type: Optional[str] = None
    last_event_type: Optional[str] = None
    last_event_time: Optional[datetime] = None
    time_in_zone_minutes: Optional[int] = None


class ZoneOccupancyResponse(BaseModel):
    """Schema for zone occupancy"""
    zone_id: int
    zone_name: str
    zone_type: str
    current_occupancy: int
    operators_present: List[int]  # operator IDs


# ==================== ERROR SCHEMAS ====================

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    """Schema for validation errors"""
    detail: str
    errors: List[dict]
    timestamp: datetime
