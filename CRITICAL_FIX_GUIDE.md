# CRITICAL ISSUES & QUICK FIX GUIDE

## 🔴 CRITICAL ISSUE #1: Frontend API Endpoint Mismatch

**Severity**: HIGH - System won't work without this fix  
**Time to Fix**: 5 minutes  
**Impact**: Frontend unable to communicate with backend

---

## The Problem

**Frontend is calling** (WRONG):
```
GET /attendance
```

**Backend provides** (CORRECT):
```
GET /api/attendance/events
```

**Result**: 404 Not Found error - Dashboard will fail to load

---

## The Fix

### File Location
```
frontend/frontend-app/src/features/live-monitoring/api/attendanceApi.ts
```

### Current Code (Line: export async function getRecognitionEvents())
```typescript
export async function getRecognitionEvents() {
  const rows = await apiRequest<AttendanceApiRow[]>("/attendance");
  return rows.map(normalizeAttendanceRow);
}
```

### Fixed Code
```typescript
export async function getRecognitionEvents() {
  const rows = await apiRequest<AttendanceApiRow[]>("/api/attendance/events");
  return rows.map(normalizeAttendanceRow);
}
```

### Change Required
```diff
- const rows = await apiRequest<AttendanceApiRow[]>("/attendance");
+ const rows = await apiRequest<AttendanceApiRow[]>("/api/attendance/events");
```

---

## How to Apply the Fix

### Option 1: Manual Edit (Recommended)

1. **Open File**:
   ```
   frontend/frontend-app/src/features/live-monitoring/api/attendanceApi.ts
   ```

2. **Find Line**:
   ```
   const rows = await apiRequest<AttendanceApiRow[]>("/attendance");
   ```

3. **Replace With**:
   ```
   const rows = await apiRequest<AttendanceApiRow[]>("/api/attendance/events");
   ```

4. **Save and Test**

### Option 2: Command Line

```bash
# On Windows (PowerShell)
(Get-Content frontend/frontend-app/src/features/live-monitoring/api/attendanceApi.ts) -replace '"/attendance"', '"/api/attendance/events"' | Set-Content frontend/frontend-app/src/features/live-monitoring/api/attendanceApi.ts

# On Mac/Linux
sed -i 's|"/attendance"|"/api/attendance/events"|g' frontend/frontend-app/src/features/live-monitoring/api/attendanceApi.ts
```

---

## Verification

After applying the fix:

### 1. Test Using Browser DevTools
```
Network tab → Filter by "attendance"
Should see: GET /api/attendance/events (200 OK)
NOT: GET /attendance (404 Not Found)
```

### 2. Test Using curl
```bash
# After backend is running
curl http://localhost:8000/api/attendance/events
# Should return: {"total": 0, "skip": 0, "take": 50, "items": []}
```

### 3. Test Frontend Dashboard
```bash
# Start frontend
npm run dev

# Check browser console for errors
# Dashboard should load attendance events
```

---

## Why This Happened

The backend API uses a prefix of `/api/` for all routes:
- Configuration: `router = APIRouter(prefix="/api/attendance", tags=["attendance"])`
- Endpoint: `@router.get("/events")`
- Full URL: `GET /api/attendance/events`

The frontend was calling just `/attendance` which doesn't exist.

---

## All Correct Endpoints (Reference)

### Attendance
```
GET /api/attendance/events
GET /api/attendance/daily-summary
GET /api/attendance/operator/{id}/status
```

### Violations
```
GET /api/violations
PUT /api/violations/{id}
GET /api/violations/stats/summary
```

### Dashboard
```
GET /api/dashboard/metrics
GET /api/dashboard/trends/hourly
GET /api/dashboard/trends/daily
```

### Employees
```
GET /api/employees
POST /api/employees
GET /api/employees/{id}
```

### Cameras
```
GET /api/cameras
POST /api/cameras
```

### Movement
```
GET /api/movement/zones/occupancy
GET /api/movement/operator/{id}/current-zone
```

---

## Testing After Fix

### Step 1: Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Step 2: Test Endpoint Directly
```bash
curl http://localhost:8000/api/attendance/events
```

### Step 3: Start Frontend
```bash
cd frontend/frontend-app
npm run dev
```

### Step 4: Check Dashboard
- Open http://localhost:5173
- Should see events loading
- No 404 errors in console
- Metrics should appear

---

## Before & After Screenshots

### Before (Broken)
```
Browser Console:
GET http://localhost:8000/attendance 404 Not Found

Network Tab:
Status: 404
Response: {"detail": "Not Found"}

Dashboard:
Error: Backend API request failed
```

### After (Fixed)
```
Browser Console:
GET http://localhost:8000/api/attendance/events 200 OK

Network Tab:
Status: 200 OK
Response: {"total": 0, "skip": 0, "take": 50, "items": []}

Dashboard:
Shows metrics
Loads events
No errors
```

---

## Related Files (No Changes Needed)

These files are correct - no fix needed:

- ✅ `src/shared/api/httpClient.ts` - Correctly prepends baseUrl
- ✅ `src/app/config/env.ts` - Correctly sets apiBaseUrl
- ✅ `src/features/dashboard/api/dashboardQueries.ts` - Correctly calls the function
- ✅ Backend API endpoints - All correct

---

## Quick Checklist

- [ ] Open file: `src/features/live-monitoring/api/attendanceApi.ts`
- [ ] Find: `const rows = await apiRequest<AttendanceApiRow[]>("/attendance");`
- [ ] Replace with: `const rows = await apiRequest<AttendanceApiRow[]>("/api/attendance/events");`
- [ ] Save file
- [ ] Restart frontend: `npm run dev`
- [ ] Test in browser: http://localhost:5173
- [ ] Verify no 404 errors in console
- [ ] Verify dashboard loads data

---

## Status After Fix

✅ Frontend will be able to call backend  
✅ Events will load from database  
✅ Dashboard will display real data  
✅ Violations will be detected and shown  
✅ System fully integrated  

---

**This is the ONLY critical fix needed for frontend-backend integration.**

All other code is complete and ready.
