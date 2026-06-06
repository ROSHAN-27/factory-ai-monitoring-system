# API Reference – Quick Guide

## Base URL
```
http://localhost:8000
```

## API Documentation
```
http://localhost:8000/docs         (Interactive Swagger UI)
http://localhost:8000/redoc        (ReDoc documentation)
```

---

## Attendance Endpoints

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| POST | `/api/attendance/events` | 201 | Create new event, trigger violation check |
| GET | `/api/attendance/events` | 200 | Get events (paginated, filtered by hours/operator/camera/type) |
| GET | `/api/attendance/daily-summary` | 200 | Daily summary for date (default today) |
| GET | `/api/attendance/operator/{operator_id}/status` | 200 | Is operator present in factory today? |
| GET | `/api/attendance/operator/{operator_id}/history` | 200 | Operator's attendance history (days, limit params) |
| GET | `/api/attendance/present-today` | 200 | All operators present in factory today |

**Create Event Request**:
```json
POST /api/attendance/events
{
  "operator_id": 1,
  "camera_id": 1,
  "event_type": "IN",
  "confidence_score": 0.95,
  "zone_type": "main_gate"
}
```

**Query Parameters**:
- `skip`: Pagination offset (default: 0)
- `limit`: Records per page (default: 50)
- `operator_id`: Filter by operator
- `camera_id`: Filter by camera
- `event_type`: Filter by IN/OUT
- `hours`: Last N hours (default: 24)
- `days`: Last N days (default: 7)
- `date`: Specific date (YYYY-MM-DD)

---

## Violations Endpoints

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| GET | `/api/violations` | 200 | Get violations (paginated, filtered) |
| GET | `/api/violations/{violation_id}` | 200 | Get violation details |
| PUT | `/api/violations/{violation_id}` | 200 | Update status, notes, acknowledgement |
| GET | `/api/violations/stats/summary` | 200 | Violation statistics by type/severity |
| GET | `/api/violations/operator/{operator_id}/history` | 200 | Operator's violation history |
| GET | `/api/violations/repeat-offenders/list` | 200 | Operators with N+ violations in M days |

**Update Violation**:
```json
PUT /api/violations/{violation_id}
{
  "status": "acknowledged",
  "acknowledged_by": "supervisor_name",
  "notes": "Discussed with employee"
}
```

**Query Parameters**:
- `skip`, `limit`: Pagination
- `operator_id`: Filter by operator
- `severity`: low | medium | high | critical
- `status`: open | acknowledged | resolved
- `days`: Filter to last N days (default: 7)
- `threshold`: Repeat offender count (default: 3)

---

## Dashboard Endpoints

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| GET | `/api/dashboard/metrics` | 200 | Main KPI dashboard (10 metrics) |
| GET | `/api/dashboard/trends/hourly` | 200 | Events/violations per hour (last 24h) |
| GET | `/api/dashboard/trends/daily` | 200 | Events/violations per day (last 30d) |
| GET | `/api/dashboard/departments` | 200 | Department-level stats |
| GET | `/api/dashboard/violations/summary` | 200 | Violations grouped by type/severity |
| GET | `/api/dashboard/top-violators` | 200 | Top 10 repeat violators |
| GET | `/api/dashboard/attendance-summary` | 200 | Daily attendance stats |
| GET | `/api/dashboard/compliance-score` | 200 | Overall compliance percentage |
| GET | `/api/dashboard/zone-occupancy` | 200 | Real-time zone occupancy snapshot |

**Metrics Response**:
```json
{
  "timestamp": "2024-06-02T10:30:45Z",
  "total_operators": 150,
  "operators_present_today": 142,
  "operators_absent_today": 8,
  "violations_today": 12,
  "high_severity_violations": 3,
  "active_cameras": 18,
  "offline_cameras": 2,
  "department_occupancy": {"Knitting": 35, "Linking": 32},
  "zone_occupancy": {"main_gate": 0, "knitting": 35, "dormitory": 2},
  "compliance_percentage": 89.53
}
```

---

## Employee Endpoints

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| POST | `/api/employees` | 201 | Create new employee |
| GET | `/api/employees` | 200 | List employees (filter: dept, shift, status) |
| GET | `/api/employees/{employee_id}` | 200 | Get employee by numeric ID |
| GET | `/api/employees/by-employee-id/{emp_id}` | 200 | Get employee by employee_id (e.g., EMP001) |
| PUT | `/api/employees/{employee_id}` | 200 | Update employee fields |
| DELETE | `/api/employees/{employee_id}` | 200 | Deactivate employee (soft delete) |
| GET | `/api/employees/{employee_id}/attendance-history` | 200 | Employee's attendance records |
| GET | `/api/employees/{employee_id}/violations` | 200 | Employee's violation history |
| POST | `/api/employees/{employee_id}/upload-face` | 200 | Upload face image |
| GET | `/api/employees/stats/summary` | 200 | Employee statistics |

**Create Employee**:
```json
POST /api/employees
{
  "employee_id": "EMP001",
  "full_name": "John Doe",
  "department": "Knitting",
  "shift_name": "Morning",
  "supervisor_id": null,
  "employment_status": "active"
}
```

---

## Camera Endpoints

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| POST | `/api/cameras` | 201 | Create new camera |
| GET | `/api/cameras` | 200 | List cameras (filter: zone, status) |
| GET | `/api/cameras/{camera_id}` | 200 | Get camera details |
| PUT | `/api/cameras/{camera_id}` | 200 | Update camera config |
| DELETE | `/api/cameras/{camera_id}` | 200 | Delete camera |
| GET | `/api/cameras/{camera_id}/health` | 200 | Get health metrics |
| POST | `/api/cameras/{camera_id}/health-update` | 200 | Update health metrics |
| POST | `/api/cameras/{camera_id}/test` | 200 | Test RTSP connection |
| GET | `/api/cameras/stats/summary` | 200 | Camera statistics |

**Create Camera**:
```json
POST /api/cameras
{
  "camera_name": "Gate1",
  "zone_type": "main_gate",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location_name": "Factory Gate"
}
```

**Health Update**:
```json
POST /api/cameras/{camera_id}/health-update
{
  "fps": 28,
  "accuracy_percent": 87.5,
  "status": "online"
}
```

---

## Movement Endpoints

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| GET | `/api/movement/operator/{operator_id}/current-zone` | 200 | Operator's current location |
| GET | `/api/movement/operator/{operator_id}/zone-history` | 200 | Operator's zone movement history |
| GET | `/api/movement/zone/{zone_type}/occupancy` | 200 | Single zone current occupancy |
| GET | `/api/movement/zones/occupancy` | 200 | All zones occupancy snapshot |
| GET | `/api/movement/department-occupancy` | 200 | Department occupancy snapshot |
| GET | `/api/movement/operator/{operator_id}/transitions` | 200 | Zone transitions (potential rule violations) |

**Zone Occupancy Response**:
```json
{
  "zone_type": "knitting",
  "occupants": [
    {
      "operator_id": 1,
      "operator_name": "John Doe",
      "department": "Knitting",
      "entry_time": "2024-06-02T08:15:30Z",
      "time_in_zone": "02:30"
    }
  ],
  "total_occupants": 35
}
```

---

## Quick Filter Examples

### Get high-severity violations from last 7 days
```bash
GET /api/violations?severity=high&status=open&days=7
```

### Get attendance events for specific operator in last 24 hours
```bash
GET /api/attendance/events?operator_id=1&hours=24
```

### Get repeat violators (3+ violations in 7 days)
```bash
GET /api/violations/repeat-offenders/list?days=7&threshold=3
```

### Get daily trends for last 30 days
```bash
GET /api/dashboard/trends/daily?days=30
```

### Get department statistics
```bash
GET /api/dashboard/departments
```

### Get employees by department
```bash
GET /api/employees?department=Knitting&employment_status=active
```

### Update violation acknowledgement
```bash
PUT /api/violations/5
Content-Type: application/json

{
  "status": "acknowledged",
  "acknowledged_by": "supervisor_name",
  "notes": "Discussed with operator"
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Request completed |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Data validation failed |
| 500 | Server Error - Internal server error |

---

## Pagination Format

All list endpoints return paginated results:

```json
{
  "total": 500,           // Total records in database
  "skip": 0,              // Records skipped
  "take": 50,             // Records returned per page
  "items": [...]          // Array of records
}
```

**Pagination Example**:
```bash
# Get first 50 records
GET /api/violations?skip=0&limit=50

# Get next 50 records (page 2)
GET /api/violations?skip=50&limit=50

# Get next 50 records (page 3)
GET /api/violations?skip=100&limit=50
```

---

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Validation Error Example**:
```json
HTTP 400
{
  "detail": "Invalid event_type. Must be 'IN' or 'OUT'"
}
```

---

## Common Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 50 | Records per page |
| `hours` | int | 24 | Last N hours |
| `days` | int | 7 | Last N days |
| `date` | string | today | Specific date (YYYY-MM-DD) |
| `operator_id` | int | - | Filter by operator |
| `camera_id` | int | - | Filter by camera |
| `severity` | string | - | low\|medium\|high\|critical |
| `status` | string | - | Event/violation status |
| `department` | string | - | Filter by department |
| `zone_type` | string | - | Filter by zone |

---

## Performance Guidelines

- **Batch Operations**: Process 100 events/second recommended
- **Query Timeout**: 30 second limit on long queries
- **Connection Pool**: 10 concurrent connections
- **Pagination Recommended**: Keep limit ≤ 100 for large datasets
- **Caching**: Consider 30-60 second cache for dashboard metrics
- **Refetch Intervals**: 
  - Metrics: 30 seconds
  - Real-time occupancy: 5 seconds
  - Violations list: 10 seconds

---

## Testing with cURL

### Test Server Health
```bash
curl http://localhost:8000/health
```

### Create Test Event
```bash
curl -X POST http://localhost:8000/api/attendance/events \
  -H "Content-Type: application/json" \
  -d '{
    "operator_id": 1,
    "camera_id": 1,
    "event_type": "IN",
    "confidence_score": 0.95,
    "zone_type": "main_gate"
  }'
```

### Check Dashboard Metrics
```bash
curl http://localhost:8000/api/dashboard/metrics | python -m json.tool
```

### Filter Violations
```bash
curl "http://localhost:8000/api/violations?severity=high&days=7" | python -m json.tool
```

---

## Version Information

- **API Version**: 1.0.0
- **Backend**: FastAPI 0.104.1
- **Database**: PostgreSQL 12+
- **Python**: 3.9+
- **Last Updated**: June 2, 2024

---

For detailed information, see [backend/README.md](backend/README.md)
