# Documentation Index – Factory AI System

## Quick Navigation

### 🚀 Getting Started (Start Here)

1. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete Installation Guide
   - PostgreSQL setup (all platforms)
   - Backend configuration
   - Frontend setup
   - Testing the integration
   - Troubleshooting common issues
   - **Read this first to get everything running locally**

2. **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Project Status & Progress
   - Current version and completion status
   - Component checklist
   - Feature coverage
   - Performance metrics
   - Next steps (Phase 2)
   - **Read this to understand what's been built**

### 📚 API Documentation

3. **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API Endpoint Reference
   - All 46 endpoints organized by function
   - Request/response formats
   - Query parameters
   - Example cURL commands
   - Error handling
   - Query examples
   - **Use this as a quick lookup for API details**

4. **[backend/README.md](backend/README.md)** - Backend In-Depth Guide
   - Architecture overview
   - Database schema explanation
   - Service layer documentation
   - Configuration details
   - 8 compliance violation rules explained
   - Performance optimizations
   - **Detailed reference for backend developers**

### 🔗 Integration & Deployment

5. **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Frontend Integration Guide
   - How to connect React frontend to backend APIs
   - Replacing mock data with real API calls
   - React Query integration patterns
   - Response types and structures
   - Error handling examples
   - WebSocket setup (future)
   - **Follow this to update frontend components**

6. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production Deployment
   - Pre-deployment checklist
   - Multiple deployment options (VPS, Docker, AWS, Heroku)
   - Database management and backups
   - Monitoring and health checks
   - Performance optimization
   - Disaster recovery plan
   - **Use this when deploying to production**

---

## Directory Structure

```
factory-ai-system/
│
├── 📄 SETUP_GUIDE.md                 ← START HERE
├── 📄 API_REFERENCE.md               ← API Lookup
├── 📄 INTEGRATION_GUIDE.md            ← Frontend Integration  
├── 📄 DEPLOYMENT_GUIDE.md             ← Production Deployment
├── 📄 PROJECT_STATUS.md               ← Progress & Status
├── 📄 packagfile.md                   ← Project Summary
│
├── backend/                           ← Production Backend
│   ├── app/
│   │   ├── config.py                 Configuration & thresholds
│   │   ├── main.py                   FastAPI application
│   │   ├── schemas.py                Pydantic validation
│   │   ├── database/                 Database connection
│   │   ├── models/                   5 ORM models
│   │   ├── services/                 4 service layers (25+ methods)
│   │   └── api/                      6 route modules (46 endpoints)
│   ├── requirements.txt              Production dependencies
│   ├── README.md                     Backend documentation
│   └── .env.example                  Configuration template
│
├── database/
│   ├── schema_v2.sql                 PostgreSQL DDL (9 tables)
│   └── schema.sql                    Original schema
│
├── frontend/
│   └── frontend-app/                 React application
│       ├── src/
│       │   ├── features/             Feature modules
│       │   ├── shared/               Shared components
│       │   └── app/                  App configuration
│       └── README.md
│
├── ai-engine/
│   ├── recognize.py                  Face recognition
│   ├── smart_attendance.py           Attendance processing
│   └── requirements.txt
│
└── docs/                             Additional documentation

```

---

## Use Case Guides

### Case 1: Developer Setting Up Locally
1. Read: [SETUP_GUIDE.md](SETUP_GUIDE.md) (Part 1-3)
2. Run: `python -m uvicorn app.main:app --reload`
3. Test: `curl http://localhost:8000/docs`
4. Read: [API_REFERENCE.md](API_REFERENCE.md) for endpoint details

### Case 2: Frontend Developer Integrating APIs
1. Read: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. Update: Replace mock hooks with API calls
3. Reference: [API_REFERENCE.md](API_REFERENCE.md) for response formats
4. Test: Verify all pages work with real backend data

### Case 3: DevOps Deploying to Production
1. Read: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) (Pre-Deployment)
2. Choose: Deployment option (VPS/Docker/AWS/Heroku)
3. Configure: .env with production credentials
4. Deploy: Follow option-specific steps
5. Monitor: Check health endpoints and logs

### Case 4: QA Testing the System
1. Read: [SETUP_GUIDE.md](SETUP_GUIDE.md) to set up test environment
2. Reference: [API_REFERENCE.md](API_REFERENCE.md) for all endpoints
3. Use: [backend/README.md](backend/README.md) for business rule explanations
4. Test: Each of 46 endpoints with valid/invalid data
5. Check: [PROJECT_STATUS.md](PROJECT_STATUS.md) for expected coverage

### Case 5: Understanding Compliance Rules
1. Read: [backend/README.md](backend/README.md#compliance-violation-rules) - 8 rules explained
2. Reference: `app/services/violation_service.py` - Rule implementation
3. Test: Use [API_REFERENCE.md](API_REFERENCE.md) to view violations
4. Verify: Rules trigger on expected conditions

### Case 6: Database Administration
1. Read: [SETUP_GUIDE.md](SETUP_GUIDE.md#part-5-database-verification)
2. Reference: `database/schema_v2.sql` - Schema documentation
3. Backup: Scripts in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#database-management)
4. Monitor: Health checks in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#monitoring--maintenance)

---

## Key Documents by Role

### Backend Developers
- [backend/README.md](backend/README.md) - Architecture & services
- [API_REFERENCE.md](API_REFERENCE.md) - All endpoints
- [database/schema_v2.sql](../database/schema_v2.sql) - Database schema
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Local development setup

### Frontend Developers
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - How to use APIs
- [API_REFERENCE.md](API_REFERENCE.md) - Endpoint details
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Local setup
- [backend/README.md](backend/README.md) - Response formats

### DevOps / System Administrators
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment options
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Environment setup
- [backend/README.md](backend/README.md) - Configuration
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - System overview

### Product Managers / Business Analysts
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Progress & metrics
- [backend/README.md](backend/README.md#compliance-violation-rules) - Business rules
- [API_REFERENCE.md](API_REFERENCE.md) - Feature coverage
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#metrics--kpis) - KPIs

### QA / Testing Team
- [API_REFERENCE.md](API_REFERENCE.md) - All endpoints to test
- [backend/README.md](backend/README.md) - Business rules
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Test environment setup
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Coverage checklist

### Technical Writers / Documentation
- [backend/README.md](backend/README.md) - Technical details
- [API_REFERENCE.md](API_REFERENCE.md) - API specs
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Implementation guide
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Architecture overview

---

## Quick Reference Links

### Most Requested Information

**"How do I set up the system locally?"**
→ [SETUP_GUIDE.md](SETUP_GUIDE.md)

**"What endpoints are available?"**
→ [API_REFERENCE.md](API_REFERENCE.md)

**"How do I connect the frontend?"**
→ [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

**"How do I deploy to production?"**
→ [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**"What's the current status?"**
→ [PROJECT_STATUS.md](PROJECT_STATUS.md)

**"What are the compliance rules?"**
→ [backend/README.md](backend/README.md#compliance-violation-rules)

**"How do I query the database?"**
→ [API_REFERENCE.md](API_REFERENCE.md#quick-filter-examples)

**"What's the database schema?"**
→ [database/schema_v2.sql](../database/schema_v2.sql)

**"How do I configure alerts?"**
→ [backend/README.md](backend/README.md#configuration) & [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#database-management)

**"What's the next phase?"**
→ [PROJECT_STATUS.md](PROJECT_STATUS.md#phase-2-priorities-next-4-6-weeks)

---

## API Quick Reference

### Available Endpoints Summary

| Group | Count | Endpoints |
|-------|-------|-----------|
| **Attendance** | 6 | Events, daily summary, operator status/history, present today |
| **Violations** | 6 | List, detail, update, stats, operator history, repeat offenders |
| **Dashboard** | 9 | Metrics, trends, departments, violations, top violators, compliance score |
| **Employees** | 10 | CRUD, attendance history, violations, upload face, stats |
| **Cameras** | 9 | CRUD, health monitoring, RTSP test, stats |
| **Movement** | 6 | Current zone, zone history, occupancy, transitions |
| **System** | 1 | Health check |
| **Total** | **47** | Complete REST API |

**Base URL**: `http://localhost:8000`  
**Documentation**: `http://localhost:8000/docs`  
**OpenAPI Spec**: `http://localhost:8000/openapi.json`

---

## Common Tasks & How-Tos

### Task: Start Backend Server

**Option 1: Development (auto-reload)**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Option 2: Production**
```bash
cd backend
python -m uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

**See**: [SETUP_GUIDE.md - Part 2](SETUP_GUIDE.md#part-2-backend-setup)

### Task: Connect Frontend to Backend

1. Update `frontend/frontend-app/src/app/config/env.ts`
2. Replace mock data hooks with API calls
3. See: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

### Task: Create a Test Employee

```bash
curl -X POST http://localhost:8000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "full_name": "Test User",
    "department": "Knitting",
    "shift_name": "Morning"
  }'
```

**See**: [API_REFERENCE.md - Employee Endpoints](API_REFERENCE.md#employee-endpoints)

### Task: Add Database Backup

```bash
pg_dump -U postgres -d factory_ai > backup.sql
```

**See**: [DEPLOYMENT_GUIDE.md - Database Management](DEPLOYMENT_GUIDE.md#automated-backups)

### Task: Check Compliance Violations

```bash
curl "http://localhost:8000/api/violations?severity=high&days=7"
```

**See**: [API_REFERENCE.md - Violations Endpoints](API_REFERENCE.md#violations-endpoints)

---

## Glossary

**Terms Used Throughout Documentation**:

| Term | Definition |
|------|-----------|
| **API** | Application Programming Interface - endpoints for frontend/apps |
| **Attendance Event** | Log entry when operator enters/exits factory zones |
| **Violation** | Detected non-compliance with factory rules |
| **Compliance Rule** | Business rule (8 total) for detecting violations |
| **Zone** | Physical location (main gate, department, dormitory) |
| **Occupancy** | Current number of operators in a zone |
| **ORM** | Object-Relational Mapping (SQLAlchemy) |
| **Pydantic** | Python validation library used for API schemas |
| **FastAPI** | Web framework for building APIs |
| **PostgreSQL** | Relational database system |
| **Redis** | In-memory cache (for Phase 2) |

---

## Support & Troubleshooting

### Something Not Working?

**Check These in Order**:

1. **Is Backend Running?**
   ```bash
   curl http://localhost:8000/health
   ```
   If not, see [SETUP_GUIDE.md#part-2-backend-setup](SETUP_GUIDE.md#part-2-backend-setup)

2. **Is Database Connected?**
   ```bash
   psql -U postgres -d factory_ai
   ```
   If not, see [SETUP_GUIDE.md#part-1-postgresql-setup](SETUP_GUIDE.md#part-1-postgresql-setup)

3. **Is API Endpoint Correct?**
   Check [API_REFERENCE.md](API_REFERENCE.md) for endpoint paths

4. **Is Response Format Correct?**
   Review [INTEGRATION_GUIDE.md#response-types](INTEGRATION_GUIDE.md#response-types)

5. **Is There an Error Message?**
   See [SETUP_GUIDE.md#part-6-troubleshooting](SETUP_GUIDE.md#part-6-troubleshooting)

### Still Need Help?

- **Technical**: Review [backend/README.md](backend/README.md) troubleshooting
- **API Issues**: Check [API_REFERENCE.md](API_REFERENCE.md) examples
- **Setup Problems**: Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) step-by-step
- **Integration**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

---

## Document Maintenance

**Version**: 1.0.0  
**Last Updated**: June 2, 2024  
**Next Review**: June 15, 2024  

**Maintained By**: Development Team  
**Contact**: tech-lead@factory-ai.com

---

## Quick Stats

| Stat | Value |
|------|-------|
| Total API Endpoints | 47 |
| Compliance Rules | 8 |
| Database Tables | 9 |
| Backend Code Lines | 2,500+ |
| Configuration Options | 25+ |
| Documentation Pages | 6 |
| Estimated Setup Time | 30 minutes |
| Deployment Time | 15-30 minutes |

---

## Your Next Steps

**Choose your path:**

👨‍💻 **Developer?** → Start with [SETUP_GUIDE.md](SETUP_GUIDE.md)  
🎨 **Frontend?** → Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)  
🚀 **DevOps?** → Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)  
📊 **Manager?** → Review [PROJECT_STATUS.md](PROJECT_STATUS.md)  
🧪 **QA?** → Use [API_REFERENCE.md](API_REFERENCE.md)

---

## Document Structure

This documentation package includes:

```
📚 Documentation (6 files)
├── 📄 This file (INDEX.md)
├── 📄 SETUP_GUIDE.md (installation)
├── 📄 API_REFERENCE.md (endpoints)
├── 📄 INTEGRATION_GUIDE.md (frontend)
├── 📄 DEPLOYMENT_GUIDE.md (production)
├── 📄 PROJECT_STATUS.md (progress)
└── 📄 backend/README.md (technical)

✅ All documentation is current for v1.0.0
✅ Updated for Phase 1 completion
✅ Ready for production deployment
```

---

**Welcome to Factory AI! 🚀**

Choose a guide above and start building!
