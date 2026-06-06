# Factory AI Backend – Implementation Guide

## Overview

This is a production-grade FastAPI backend for the Factory AI Operator Movement Compliance Dashboard. It provides a complete REST API for managing attendance events, detecting compliance violations, and providing real-time analytics.

**Status**: Phase 1 Implementation Complete ✅
- All core models, schemas, and services implemented
- 6 major API endpoint groups (40+ endpoints)
- 8 compliance violation rules
- Real-time compliance checking
- Dashboard analytics with actual metrics

---

## Quick Start

### 1. Setup Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database

```bash
# Copy and edit .env file
cp .env.example .env

# Update DATABASE_URL with your PostgreSQL credentials
DATABASE_URL=postgresql://postgres:password@localhost:5432/factory_ai
```

### 3. Initialize Database

```bash
# Run schema creation
psql -U postgres -d factory_ai -f ../database/schema_v2.sql

# Or connect to database and run:
# CREATE TABLE ... (see schema_v2.sql)
```

### 4. Run Backend Server

```bash
# Development (with auto-reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

---

## Project Structure

```
backend/
├── app/
│   ├── config.py                    # Configuration & settings
│   ├── main.py                      # FastAPI application
│   ├── schemas.py                   # Pydantic validation schemas
│   ├── database/
│   │   └── __init__.py              # Database connection & session
│   ├── models/
│   │   ├── base.py                  # Base model class
│   │   ├── employee.py              # Employee/Operator model
│   │   ├── camera.py                # Camera model
│   │   ├── zone.py                  # Zone model
│   │   ├── attendance.py            # Attendance events model
│   │   ├── violation.py             # Violation model
│   │   └── __init__.py              # Models package
│   ├── services/
│   │   ├── attendance_service.py    # Attendance event handling
│   │   ├── movement_service.py      # Zone & location tracking
│   │   ├── violation_service.py     # Compliance violation detection
│   │   ├── dashboard_service.py     # Analytics & metrics
│   │   └── __init__.py              # Services package
│   └── api/
│       ├── attendance.py            # Attendance endpoints
│       ├── violations.py            # Violation endpoints
│       ├── dashboard.py             # Dashboard analytics endpoints
│       ├── employees.py             # Employee management endpoints
│       ├── cameras.py               # Camera management endpoints
│       ├── movement.py              # Movement/location endpoints
│       └── __init__.py              # API package
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration (KEEP SECRET)
├── .env.example                     # Example configuration template
└── README.md                        # This file
```

---

## API Endpoints Overview

### 1. Attendance API (`/api/attendance`)

Manage attendance events and track operator presence.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/events` | Log new attendance event |
| GET | `/events` | Get attendance events (paginated, filtered) |
| GET | `/daily-summary` | Get daily attendance summary |
| GET | `/operator/{id}/status` | Get operator's current presence status |
| GET | `/operator/{id}/history` | Get operator's attendance history |
| GET | `/present-today` | Get list of operators present today |

**Example - Log Event:**
```bash
curl -X POST http://localhost:8000/api/attendance/events \
  -H "Content-Type: application/json" \
  -d '{
    "operator_id": 1,
    "camera_id": 1,
    "event_type": "IN",
    "zone_type": "main_gate",
    "confidence_score": 0.95
  }'
```

### 2. Violations API (`/api/violations`)

Monitor compliance violations and violations statistics.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Get violations (paginated, filtered) |
| GET | `/{id}` | Get violation details |
| PUT | `/{id}` | Update violation status/notes |
| GET | `/stats/summary` | Get violation statistics |
| GET | `/operator/{id}/history` | Get operator's violation history |
| GET | `/repeat-offenders/list` | Get repeat violators |

**Example - Get Violations:**
```bash
curl "http://localhost:8000/api/violations?severity=high&status=open&days=7"
```

### 3. Dashboard API (`/api/dashboard`)

Get real-time metrics and analytics.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/metrics` | Get comprehensive dashboard KPIs |
| GET | `/trends/hourly` | Get hourly event/violation trends |
| GET | `/trends/daily` | Get daily event/violation trends |
| GET | `/departments` | Get per-department statistics |
| GET | `/violations/summary` | Get violation type summary |
| GET | `/top-violators` | Get operators with most violations |
| GET | `/attendance-summary` | Get daily attendance summary |
| GET | `/compliance-score` | Get overall compliance percentage |
| GET | `/zone-occupancy` | Get real-time zone occupancy |

**Example - Get Dashboard Metrics:**
```bash
curl http://localhost:8000/api/dashboard/metrics
```

**Response:**
```json
{
  "timestamp": "2024-06-02T10:30:45.123456",
  "total_operators": 150,
  "operators_present_today": 142,
  "operators_absent_today": 8,
  "violations_today": 12,
  "high_severity_violations": 3,
  "active_cameras": 18,
  "offline_cameras": 2,
  "department_occupancy": {
    "Knitting": 35,
    "Linking": 32,
    "Finishing": 28,
    "Washing": 25,
    "Packing": 22
  },
  "zone_occupancy": {
    "main_gate": 0,
    "knitting": 35,
    "dormitory": 2,
    "canteen": 5,
    "common_area": 3
  },
  "compliance_percentage": 89.53
}
```

### 4. Employees API (`/api/employees`)

Manage employee master data.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `` | Create new employee |
| GET | `` | Get employees (filtered) |
| GET | `/{id}` | Get employee details |
| GET | `/by-employee-id/{emp_id}` | Get employee by employee ID |
| PUT | `/{id}` | Update employee |
| DELETE | `/{id}` | Deactivate employee |
| GET | `/{id}/attendance-history` | Get employee's attendance history |
| GET | `/{id}/violations` | Get employee's violation history |
| POST | `/{id}/upload-face` | Upload employee face image |
| GET | `/stats/summary` | Get employee statistics |

### 5. Cameras API (`/api/cameras`)

Manage camera configuration and health.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `` | Create new camera |
| GET | `` | Get cameras (filtered) |
| GET | `/{id}` | Get camera details |
| PUT | `/{id}` | Update camera config |
| DELETE | `/{id}` | Delete camera |
| GET | `/{id}/health` | Get camera health metrics |
| POST | `/{id}/health-update` | Update camera metrics |
| POST | `/{id}/test` | Test RTSP connection |
| GET | `/stats/summary` | Get camera statistics |

### 6. Movement API (`/api/movement`)

Track operator locations and zone movements.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/operator/{id}/current-zone` | Get operator's current zone |
| GET | `/operator/{id}/zone-history` | Get operator's zone movement history |
| GET | `/zone/{type}/occupancy` | Get zone occupancy |
| GET | `/zones/occupancy` | Get all zones occupancy |
| GET | `/department-occupancy` | Get department occupancy snapshot |
| GET | `/operator/{id}/transitions` | Get zone transitions |

---

## Compliance Violation Rules

The system automatically detects 8 types of compliance violations:

### 1. Missing Department Entry
- **Description**: Employee enters department without first entering factory
- **Severity**: HIGH
- **Rule**: If IN event at department_zone without prior IN at main_gate

### 2. Wrong Department Entry
- **Description**: Employee enters different department than assigned
- **Severity**: HIGH
- **Rule**: If IN event zone ≠ employee's assigned department

### 3. Dormitory Post Entry
- **Description**: Employee goes to dormitory after factory entry
- **Severity**: HIGH
- **Rule**: If IN event at dormitory after factory entry in same day

### 4. Early Department Exit
- **Description**: Employee exits department before shift threshold
- **Severity**: MEDIUM
- **Rule**: If OUT event before 30 mins to shift end (configurable)

### 5. Long Absence from Department
- **Description**: Employee absent from their department > threshold
- **Severity**: MEDIUM
- **Rule**: If gap since dept OUT > 120 mins (configurable)

### 6. Shift Non-Compliance
- **Description**: Factory entry outside normal shift hours
- **Severity**: HIGH
- **Rule**: If factory entry before 7am or after 10am (configurable)

### 7. Late Reporting
- **Description**: Employee's first entry is late
- **Severity**: LOW
- **Rule**: If first entry > 15 mins after 8am shift start (configurable)

### 8. Repeat Violation
- **Description**: Employee has repeated violations
- **Severity**: HIGH
- **Rule**: If violation_count >= 3 in 7 days

---

## Data Models

### Employee
```python
{
    "id": 1,
    "employee_id": "EMP001",
    "full_name": "John Doe",
    "department": "Knitting",
    "shift_name": "Morning",
    "employment_status": "active",
    "supervisor_id": null,
    "face_image_path": "/path/to/image.jpg",
    "line_section": "Line 1",
    "created_at": "2024-06-01T08:00:00"
}
```

### AttendanceEvent
```python
{
    "id": 1,
    "operator_id": 1,
    "camera_id": 1,
    "event_type": "IN",
    "zone_type": "main_gate",
    "confidence_score": 0.95,
    "snapshot_path": "/snapshots/123.jpg",
    "event_time": "2024-06-02T08:15:30",
    "created_at": "2024-06-02T08:15:31"
}
```

### Violation
```python
{
    "id": 1,
    "operator_id": 1,
    "violation_type": "wrong_department_entry",
    "violation_message": "Entry to linking but assigned to knitting",
    "severity": "high",
    "status": "open",
    "related_event_id": 5,
    "acknowledged_by": null,
    "notes": null,
    "created_at": "2024-06-02T08:16:00",
    "updated_at": "2024-06-02T08:16:00"
}
```

---

## Service Layer

### AttendanceService
Handles attendance event logging and retrieval.

**Key Methods:**
- `create_event()` - Log new attendance event
- `get_events_paginated()` - Get events with filters
- `get_daily_summary()` - Daily attendance statistics
- `get_operator_current_status()` - Current presence status
- `get_operators_present_today()` - All present operators

### MovementService
Tracks zone transitions and current locations.

**Key Methods:**
- `get_operator_current_zone()` - Operator's current location
- `get_zone_occupancy()` - Zone occupancy snapshot
- `get_all_zones_occupancy()` - All zones occupancy
- `get_zone_history()` - Operator's zone movement history
- `get_department_occupancy_snapshot()` - Department distribution

### ViolationService
Detects compliance violations using business rules.

**Key Methods:**
- `check_event_for_violations()` - Check new event for all violations
- `get_violations_paginated()` - Get violations with filters
- `get_violation_stats()` - Violation statistics
- Internal rule checkers for each violation type

### DashboardService
Provides real metrics for dashboard analytics.

**Key Methods:**
- `get_dashboard_metrics()` - All KPIs
- `get_hourly_trends()` - Hourly trends
- `get_daily_trends()` - Daily trends
- `get_department_stats()` - Per-department metrics
- `calculate_compliance_percentage()` - Compliance score
- `get_top_violators()` - Repeat offender list

---

## Configuration

All settings are in `app/config.py` and loaded from `.env` file.

### Key Thresholds (Configurable)

```python
LONG_ABSENCE_THRESHOLD_MINUTES = 120      # 2 hours
REPEAT_VIOLATION_THRESHOLD = 3            # 3 violations
REPEAT_VIOLATION_DAYS = 7                 # in 7 days
EARLY_EXIT_THRESHOLD_MINUTES = 30         # 30 mins before shift end
LATE_REPORTING_THRESHOLD_MINUTES = 15     # 15 mins after shift start
MIN_CONFIDENCE_SCORE = 0.65               # Face recognition confidence
```

To change thresholds, update `.env` file:

```
LONG_ABSENCE_THRESHOLD_MINUTES=180
REPEAT_VIOLATION_THRESHOLD=5
```

---

## Database Schema

### Tables Created

1. **operators** - Employee master data
2. **cameras** - Camera configuration
3. **zones** - Zone definitions
4. **attendance_logs** - Event logging (renamed from events)
5. **violations** - Compliance violation records
6. **alerts** - Alert notifications
7. **audit_logs** - Audit trail
8. **camera_metrics** - Camera health metrics
9. **compliance_rules** - Rule definitions

See [schema_v2.sql](../database/schema_v2.sql) for complete DDL.

---

## Security Best Practices

### ✅ Implemented

- Environment-based configuration (no hardcoded secrets)
- Database connection pooling
- Input validation (Pydantic schemas)
- SQL injection prevention (SQLAlchemy ORM)
- CORS middleware configuration
- Dependency injection for database sessions

### 🔒 Recommended for Production

- Add authentication (JWT/OAuth2)
- Implement rate limiting
- Add request validation middleware
- Use API key for camera health updates
- Encrypt sensitive fields (face_image_path)
- Add request logging/monitoring
- Implement db query timeout limits
- Use SSL/TLS for HTTPS

---

## Performance Optimizations

### Database Indexes
All critical queries have indexes:
- attendance_logs by (operator_id, time)
- violations by (operator_id, time)
- cameras by (zone_type, status)
- operators by (department, shift)

### Connection Pooling
- Pool size: 10 connections
- Max overflow: 20 connections
- Connection timeout: 1 hour
- Pre-ping enabled (validates connections)

### Query Optimization
- Pagination on all list endpoints (default 50 items)
- Efficient aggregations using SQL functions
- Proper joins to avoid N+1 queries
- Denormalized fields for common queries

---

## Integration with Frontend

The backend is designed to work with the existing React frontend:

### CORS Configuration
```python
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
```

### API Response Format
All responses follow consistent JSON structure with proper HTTP status codes:

**Success (200):**
```json
{ "data": {...}, "success": true }
```

**Error (400):**
```json
{ "detail": "Error message" }
```

### WebSocket Integration (Future)
Current implementation uses polling. For real-time updates:
- Use existing WebSocket infrastructure from frontend
- Emit events via broadcast channels
- Subscribe to: `recognition`, `violations`, `camera-health`

---

## Testing the Backend

### Test Attendance Endpoint

```bash
# 1. Create employee
curl -X POST http://localhost:8000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "full_name": "John Doe",
    "department": "Knitting",
    "shift_name": "Morning"
  }'

# 2. Create camera
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "camera_name": "Gate1",
    "zone_type": "main_gate",
    "rtsp_url": "rtsp://..."
  }'

# 3. Log attendance event
curl -X POST http://localhost:8000/api/attendance/events \
  -H "Content-Type: application/json" \
  -d '{
    "operator_id": 1,
    "camera_id": 1,
    "event_type": "IN",
    "confidence_score": 0.95
  }'

# 4. Get dashboard metrics
curl http://localhost:8000/api/dashboard/metrics

# 5. Check violations
curl http://localhost:8000/api/violations
```

---

## Troubleshooting

### Database Connection Error
```
Error: FATAL: role "postgres" does not exist
```
**Solution**: Create PostgreSQL user:
```sql
CREATE USER postgres WITH PASSWORD 'GR1dn9k3';
CREATE DATABASE factory_ai OWNER postgres;
```

### Module Import Error
```
ModuleNotFoundError: No module named 'psycopg2'
```
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Schema Mismatch
```
ProgrammingError: relation "attendance_logs" does not exist
```
**Solution**: Run schema script:
```bash
psql -U postgres -d factory_ai -f database/schema_v2.sql
```

---

## Next Steps (Phase 2)

- [ ] Authentication & Authorization (JWT/OAuth2)
- [ ] Alert delivery system (Email, SMS, WhatsApp)
- [ ] Report generation (Excel, PDF exports)
- [ ] WebSocket real-time notifications
- [ ] Batch import/sync operations
- [ ] Advanced compliance rule builder
- [ ] Machine learning predictions
- [ ] Performance monitoring & metrics

---

## Support & Contact

For issues, questions, or contributions:
- Check [IMPLEMENTATION_ASSESSMENT.md](../IMPLEMENTATION_ASSESSMENT.md) for architecture details
- Review [schema_v2.sql](../database/schema_v2.sql) for database structure
- Test with API documentation: `http://localhost:8000/docs`

---

**Last Updated**: June 2, 2026
**Backend Status**: ✅ Phase 1 Complete - Production Ready for Core Features
