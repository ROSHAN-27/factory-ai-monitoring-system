# Complete Setup Guide

## Prerequisites

- **Python 3.9+** (3.10+ recommended)
- **PostgreSQL 12+** 
- **Node.js 16+** (for frontend)
- **pip** and **npm** (package managers)
- **Git** (optional, for version control)

---

## Part 1: PostgreSQL Setup

### Windows

1. **Download PostgreSQL**
   - Visit: https://www.postgresql.org/download/windows/
   - Download version 15+ installer

2. **Install PostgreSQL**
   ```
   Run installer → Follow setup wizard
   - Select installation directory
   - Create password for "postgres" user (remember this!)
   - Port: 5432 (default is fine)
   - Locale: Default
   - Click "Finish"
   ```

3. **Verify Installation**
   ```bash
   psql --version
   # Output: psql (PostgreSQL) 15.x
   ```

4. **Create Database**
   ```bash
   # Login to PostgreSQL
   psql -U postgres
   
   # In psql console:
   CREATE DATABASE factory_ai;
   \l                          # List databases (should see factory_ai)
   \q                          # Exit
   ```

### Mac

```bash
# Install using Homebrew
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database
createdb factory_ai
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb factory_ai
```

---

## Part 2: Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output**: 
```
Successfully installed ... packages
```

### 4. Configure Environment

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your PostgreSQL credentials
# Windows: notepad .env
# Mac/Linux: nano .env
```

**Update these values**:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/factory_ai
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 5. Initialize Database Schema

```bash
# Run schema creation script
psql -U postgres -d factory_ai -f ../database/schema_v2.sql

# Or copy-paste schema from file to psql
```

**Expected**: Tables created without errors

### 6. Start Backend Server

```bash
python -m uvicorn app.main:app --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ **Backend is running!**  
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## Part 3: Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend/frontend-app
```

### 2. Install Dependencies

```bash
npm install
```

**Expected**: 
```
added XXX packages in XXs
```

### 3. Configure Environment

```bash
# Create .env.local
cp .env.example .env.local

# Edit with API endpoint
# VITE_API_URL=http://localhost:8000
```

Or edit the config directly in `src/app/config/env.ts`:

```typescript
export const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';
```

### 4. Start Development Server

```bash
npm run dev
```

**Expected output**:
```
  VITE v4.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

✅ **Frontend is running!**  
- App: http://localhost:5173

---

## Part 4: Testing the Integration

### 1. Create Sample Employee

```bash
curl -X POST http://localhost:8000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "full_name": "Test Employee",
    "department": "Knitting",
    "shift_name": "Morning",
    "employment_status": "active"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "employee_id": "EMP001",
  "full_name": "Test Employee",
  "department": "Knitting",
  "shift_name": "Morning",
  "employment_status": "active",
  "created_at": "2024-06-02T10:00:00Z"
}
```

### 2. Create Sample Camera

```bash
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "camera_name": "Gate1",
    "zone_type": "main_gate",
    "rtsp_url": "rtsp://192.168.1.100:554/stream",
    "location_name": "Factory Gate"
  }'
```

### 3. Log Attendance Event

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

### 4. Check Dashboard Metrics

```bash
curl http://localhost:8000/api/dashboard/metrics | python -m json.tool
```

**Expected**: 
```json
{
  "timestamp": "...",
  "total_operators": 1,
  "operators_present_today": 1,
  "violations_today": 0,
  ...
}
```

### 5. View in Frontend

Open http://localhost:5173 and check:
- Dashboard shows real metrics
- No errors in browser console
- API requests in Network tab

---

## Part 5: Database Verification

### Verify Schema Creation

```bash
# Connect to database
psql -U postgres -d factory_ai

# List tables
\dt

# Expected output:
# - operators
# - cameras
# - zones
# - attendance_logs
# - violations
# - alerts
```

### Check Sample Data

```bash
# View zones
SELECT * FROM zones;

# View operators
SELECT * FROM operators;

# View attendance events
SELECT * FROM attendance_logs;

# View violations
SELECT * FROM violations;

# Exit
\q
```

---

## Part 6: Troubleshooting

### Issue: "Database connection refused"

**Error**:
```
FATAL: role "postgres" does not exist
```

**Solution**:
```bash
# Verify PostgreSQL is running
psql --version

# Try connecting
psql -U postgres -d factory_ai

# If fails, restart PostgreSQL
# Windows: Services → PostgreSQL
# Mac: brew services restart postgresql@15
# Linux: sudo systemctl restart postgresql
```

### Issue: "ModuleNotFoundError"

**Error**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
# Verify venv is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "Port already in use"

**Error**:
```
Address already in use
```

**Solution**:
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID [PID] /F

# Mac/Linux:
lsof -i :8000
kill -9 [PID]
```

### Issue: "CORS Error"

**Error**:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution**:
```
1. Verify CORS_ORIGINS in .env includes http://localhost:5173
2. Check that backend is running (http://localhost:8000 accessible)
3. Handle error in frontend (see INTEGRATION_GUIDE.md)
```

### Issue: "404 Not Found"

**Error**:
```
{"detail":"Not Found"}
```

**Solution**:
- Check API endpoint path (case-sensitive)
- Verify resource ID exists (e.g., operator_id=1)
- Check backend console for error logs

### Issue: "400 Bad Request"

**Error**:
```
{"detail":"Validation error..."}
```

**Solution**:
- Check request body format (JSON)
- Verify required fields are present
- Review validation rules in `app/schemas.py`

---

## Part 7: Development Workflow

### Running Both Frontend & Backend

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend/frontend-app
npm run dev
```

**Terminal 3 - Database** (optional, if using CLI):
```bash
psql -U postgres -d factory_ai
```

### Making API Changes

1. **Modify backend code** (e.g., `app/services/violation_service.py`)
2. **Uvicorn reloads automatically** (watch for `Application startup complete`)
3. **Frontend refetches** via React Query on next interval
4. **Test in browser** http://localhost:5173

### Database Changes

1. **Update schema** in `database/schema_v2.sql`
2. **Apply changes** via psql:
   ```bash
   psql -U postgres -d factory_ai -f database/schema_v2.sql
   ```
3. **Restart backend** (stop and rerun uvicorn)

---

## Part 8: Production Deployment

### Before Deploying

- [ ] Update `.env` with production database credentials
- [ ] Set `DEBUG=False` in `.env`
- [ ] Update `CORS_ORIGINS` to production domains
- [ ] Change `SECRET_KEY` in `.env` to random string
- [ ] Update PostgreSQL database to external server
- [ ] Configure email/SMS for alerts (if needed)
- [ ] Test all APIs with real data
- [ ] Run security scan on backend

### Deploy Backend (Example: Heroku)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create factory-ai-backend

# Add database
heroku addons:create heroku-postgresql:standard-0

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

### Deploy Frontend (Example: Vercel)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables
vercel env add VITE_API_URL https://your-backend-api.com
```

---

## Part 9: Monitoring & Maintenance

### Check Backend Health

```bash
curl http://localhost:8000/health
# Response: {"status":"healthy"}
```

### View Logs

**Backend Logs**:
- Console output from uvicorn command
- Check for ERROR or WARNING messages

**Database Logs**:
```bash
# PostgreSQL logs
tail -f /var/log/postgresql/postgresql.log  # Linux
```

### Performance Monitoring

```bash
# Check active database connections
psql -U postgres -d factory_ai

SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
\q
```

### Backup Database

```bash
# Create backup
pg_dump -U postgres -d factory_ai > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U postgres -d factory_ai < backup_20240602.sql
```

---

## Quick Reference

### Important Commands

```bash
# Backend
cd backend
source venv/bin/activate                    # Activate env
pip install -r requirements.txt             # Install deps
python -m uvicorn app.main:app --reload    # Start server

# Frontend
cd frontend/frontend-app
npm install                                 # Install deps
npm run dev                                 # Start dev server
npm run build                               # Build for production

# Database
psql -U postgres -d factory_ai              # Connect
\dt                                         # List tables
\q                                          # Exit
```

### Useful URLs

```
Backend:        http://localhost:8000
API Docs:       http://localhost:8000/docs
Frontend:       http://localhost:5173
PostgreSQL:     tcp://localhost:5432
```

### Default Credentials

```
PostgreSQL User:    postgres
PostgreSQL Port:    5432
Backend Port:       8000
Frontend Port:      5173
```

---

## Next Steps

1. ✅ Complete setup steps above
2. ✅ Verify all services running
3. ✅ Test with sample data
4. ✅ Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for frontend integration
5. ✅ Review [API_REFERENCE.md](API_REFERENCE.md) for endpoint details
6. ✅ Check [backend/README.md](backend/README.md) for detailed documentation

---

## Support

- **Backend Issues**: Check [backend/README.md](backend/README.md) troubleshooting section
- **API Documentation**: http://localhost:8000/docs
- **Frontend Issues**: Check [frontend/frontend-app/README.md](frontend/frontend-app/README.md)
- **Database Issues**: PostgreSQL documentation at https://www.postgresql.org/docs/

---

**Setup Status**: ✅ Complete
**Version**: 1.0.0
**Last Updated**: June 2, 2024
