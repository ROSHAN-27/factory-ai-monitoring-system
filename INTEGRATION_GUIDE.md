# Frontend Integration Guide

## Overview
This guide explains how to connect the React frontend to the new production backend APIs.

## Architecture

```
Frontend (React)                    Backend (FastAPI)
├── src/                           ├── app/
│   ├── features/                  │   ├── api/
│   │   ├── dashboard/             │   │   ├── attendance.py
│   │   │   └── hooks/             │   │   ├── violations.py
│   │   ├── violations/            │   │   ├── dashboard.py
│   │   ├── live-monitoring/       │   │   ├── employees.py
│   │   └── reports/               │   │   ├── cameras.py
│   └── shared/api/                │   │   └── movement.py
│       └── httpClient.ts          │   ├── services/
│                                  │   └── models/

HTTP Client (Axios)  ←─────────→  FastAPI + SQLAlchemy
                                    (37 endpoints)
```

## API Base URL

```typescript
// src/app/config/env.ts
export const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';
```

Add to `.env`:
```
VITE_API_URL=http://localhost:8000
```

## Key API Integration Points

### 1. Dashboard Metrics

**Before (Mock Data)**:
```typescript
// src/features/dashboard/hooks/useDashboardModel.ts
const metrics = {
  total_operators: 150,  // ← Mock value
  operators_present_today: 142,
  violations_today: 12,
  // ... etc
};
```

**After (Real Data)**:
```typescript
import { API_BASE_URL } from '@/app/config/env';

export const useDashboardMetrics = () => {
  return useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/dashboard/metrics`);
      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30s
  });
};
```

### 2. Live Monitoring (Real-time Zone Occupancy)

```typescript
// src/features/live-monitoring/hooks/useZoneOccupancy.ts
export const useZoneOccupancy = () => {
  return useQuery({
    queryKey: ['zone-occupancy'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/movement/zones/occupancy`);
      return response.json();
    },
    refetchInterval: 5000, // Update every 5 seconds
  });
};
```

### 3. Violations List with Filtering

```typescript
// src/features/violations/hooks/useViolations.ts
interface ViolationFilters {
  severity?: 'low' | 'medium' | 'high' | 'critical';
  status?: 'open' | 'acknowledged' | 'resolved';
  days?: number;
  page?: number;
  limit?: number;
}

export const useViolations = (filters: ViolationFilters) => {
  const query = new URLSearchParams();
  query.append('skip', String((filters.page || 0) * (filters.limit || 50)));
  query.append('limit', String(filters.limit || 50));
  
  if (filters.severity) query.append('severity', filters.severity);
  if (filters.status) query.append('status', filters.status);
  if (filters.days) query.append('days', String(filters.days));

  return useQuery({
    queryKey: ['violations', filters],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/violations?${query}`);
      return response.json();
    },
  });
};
```

### 4. Attendance Events

```typescript
// src/features/dashboard/api/attendanceApi.ts
export const fetchAttendanceEvents = async (filters?: {
  hours?: number;
  operator_id?: number;
  camera_id?: number;
  event_type?: 'IN' | 'OUT';
}) => {
  const query = new URLSearchParams();
  if (filters?.hours) query.append('hours', String(filters.hours));
  if (filters?.operator_id) query.append('operator_id', String(filters.operator_id));
  if (filters?.camera_id) query.append('camera_id', String(filters.camera_id));
  if (filters?.event_type) query.append('event_type', filters.event_type);

  const response = await fetch(`${API_BASE_URL}/api/attendance/events?${query}`);
  return response.json();
};
```

### 5. Dashboard Trends

```typescript
// src/features/dashboard/api/dashboardApi.ts

// Hourly trends
export const fetchHourlyTrends = async (hours = 24) => {
  const response = await fetch(`${API_BASE_URL}/api/dashboard/trends/hourly?hours=${hours}`);
  return response.json();
};

// Daily trends
export const fetchDailyTrends = async (days = 30) => {
  const response = await fetch(`${API_BASE_URL}/api/dashboard/trends/daily?days=${days}`);
  return response.json();
};

// Department stats
export const fetchDepartmentStats = async () => {
  const response = await fetch(`${API_BASE_URL}/api/dashboard/departments`);
  return response.json();
};
```

### 6. Operator Movement History

```typescript
// src/features/live-monitoring/api/movementApi.ts
export const fetchOperatorZoneHistory = async (operatorId: number, days = 1) => {
  const response = await fetch(
    `${API_BASE_URL}/api/movement/operator/${operatorId}/zone-history?days=${days}`
  );
  return response.json();
};

export const fetchOperatorCurrentZone = async (operatorId: number) => {
  const response = await fetch(
    `${API_BASE_URL}/api/movement/operator/${operatorId}/current-zone`
  );
  return response.json();
};
```

## Response Types

### DashboardMetrics Response
```typescript
interface DashboardMetrics {
  timestamp: string;
  total_operators: number;
  operators_present_today: number;
  operators_absent_today: number;
  violations_today: number;
  high_severity_violations: number;
  active_cameras: number;
  offline_cameras: number;
  department_occupancy: Record<string, number>;
  zone_occupancy: Record<string, number>;
  compliance_percentage: number;
}
```

### Violations List Response
```typescript
interface ViolationListResponse {
  total: number;
  skip: number;
  take: number;
  items: Array<{
    id: number;
    operator_id: number;
    violation_type: string;
    violation_message: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    status: 'open' | 'acknowledged' | 'resolved';
    related_event_id: number;
    acknowledged_by?: string;
    acknowledged_at?: string;
    notes?: string;
    created_at: string;
    updated_at: string;
  }>;
}
```

### Attendance Events Response
```typescript
interface AttendanceListResponse {
  total: number;
  skip: number;
  take: number;
  items: Array<{
    id: number;
    operator_id: number;
    camera_id: number;
    event_type: 'IN' | 'OUT';
    zone_type: string;
    confidence_score: number;
    snapshot_path?: string;
    event_time: string;
    created_at: string;
  }>;
}
```

## Error Handling

All API endpoints return standard error responses:

```typescript
// Error handling in query hooks
export const useViolations = (filters: ViolationFilters) => {
  return useQuery({
    queryKey: ['violations', filters],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/violations?...`);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch violations');
      }
      
      return response.json();
    },
  });
};
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error

Error Response:
```json
{
  "detail": "Invalid event_type. Must be 'IN' or 'OUT'"
}
```

## Real-time Updates (WebSocket - Future)

Current implementation uses polling. For true real-time:

```typescript
// src/shared/websocket/useWebSocket.ts
export const useViolationsWebsocket = () => {
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/api/ws/violations`);
    
    ws.onmessage = (event) => {
      const violation = JSON.parse(event.data);
      // Update violations state
    };
    
    return () => ws.close();
  }, []);
};
```

## Local Development Setup

### 1. Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

### 2. Start Frontend
```bash
cd frontend/frontend-app
npm install
npm run dev
```

Frontend: `http://localhost:5173`

### 3. Test Integration
- Dashboard shows real metrics (not mock values)
- Violations list is populated from database
- Zone occupancy updates in real-time
- Attendance events appear immediately after logging

## Common Integration Issues

### Issue: CORS Error
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution**: Backend CORS is configured in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Make sure `http://localhost:5173` is in `CORS_ORIGINS` environment variable.

### Issue: 404 Not Found
```
404: {"detail":"Not Found"}
```

**Solution**: Check endpoint path spelling and verify model IDs exist in database.

### Issue: 400 Bad Request
```
400: {"detail":"Invalid event_type. Must be 'IN' or 'OUT'"}
```

**Solution**: Validate request data matches schema. Check `app/schemas.py` for required fields.

## Migration Checklist

- [ ] Remove all mock data functions from hooks
- [ ] Replace `useMockXXX` with database query hooks
- [ ] Update query refetch intervals (30s for metrics, 5s for real-time)
- [ ] Add error boundaries to components
- [ ] Add loading states to queries
- [ ] Test with real database
- [ ] Verify CORS configuration
- [ ] Check API response times
- [ ] Validate error handling
- [ ] Performance test with 1000+ events

## Performance Tips

1. **Use React Query**: Caching and automatic refetch built-in
2. **Pagination**: All list endpoints paginate by default
3. **Filtering**: Use query parameters to filter data server-side
4. **Debouncing**: Debounce search/filter inputs (500ms)
5. **Lazy Loading**: Fetch violations only when tab is active
6. **Memoization**: Use `useMemo` for computed values

## Next Steps

1. Update `src/app/config/env.ts` with API_BASE_URL
2. Create API hook functions in `src/shared/api/`
3. Replace mock data in feature hooks with real API calls
4. Test each page with real backend data
5. Add error boundaries and loading states
6. Configure CORS for production domains

---

**Status**: Ready for Integration ✅
**Backend Version**: 1.0.0
**Frontend Target**: React 18.2.0+
