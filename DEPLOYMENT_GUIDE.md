# Deployment & Operations Guide

## Overview

This guide covers deploying the Factory AI system to production, monitoring health, and maintaining performance at scale.

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing: `pytest app/`
- [ ] No linting errors: `flake8 app/`
- [ ] Type checking passes: `mypy app/`
- [ ] Code formatting: `black app/`

### Security Review
- [ ] No hardcoded secrets in code
- [ ] `.env` file NOT included in git
- [ ] All inputs validated with Pydantic
- [ ] CORS origins configured for production
- [ ] Database user has minimal required permissions
- [ ] SSL/TLS enabled for HTTPS
- [ ] API keys rotated and stored securely

### Performance Baseline
- [ ] Dashboard loads in < 2 seconds
- [ ] Violations query returns in < 1 second
- [ ] Attendance event creation in < 500ms
- [ ] Camera health check every 30 seconds
- [ ] Database queries have appropriate indexes

### Documentation
- [ ] API documentation reviewed
- [ ] Deployment runbook prepared
- [ ] Monitoring alerts configured
- [ ] Backup/recovery procedures tested
- [ ] Architecture diagrams updated

---

## Local to Production Environment

### Configuration Differences

| Setting | Development | Production |
|---------|-------------|-----------|
| DEBUG | True | False |
| Database | localhost:5432 | RDS/Cloud DB |
| CORS Origins | localhost:5173 | yourdomain.com |
| Log Level | DEBUG | INFO |
| Workers | 1 | 4-8 |
| Connection Pool | 10 | 20-50 |
| Cache TTL | 0 | 60s |
| SSL | None | Required |

### Environment File (Production)

```bash
# .env (Production)
ENVIRONMENT=production
DEBUG=False

# Database (use managed service)
DATABASE_URL=postgresql://user:password@prod-db.rds.amazonaws.com:5432/factory_ai
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Security
SECRET_KEY=generate-random-64-char-key
ALGORITHM=HS256

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Compliance Thresholds (configurable)
LONG_ABSENCE_THRESHOLD_MINUTES=120
REPEAT_VIOLATION_THRESHOLD=3
REPEAT_VIOLATION_DAYS=7

# Performance
ENABLE_CACHING=True
REDIS_URL=redis://cache-server:6379/0
```

---

## Deployment Options

### Option 1: Traditional VPS (Linux Server)

**Prerequisites**:
- Ubuntu 20.04 LTS or later
- SSH access to server
- PostgreSQL 13+ installed
- 2+ CPU cores, 4+ GB RAM

**Steps**:

```bash
# 1. Connect to server
ssh user@your-server.com

# 2. Clone repository
git clone https://github.com/your-repo/factory-ai.git
cd factory-ai

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 4. Copy production .env
cp backend/.env.example backend/.env
# Edit .env with production values

# 5. Initialize database
psql -U postgres -d factory_ai -f database/schema_v2.sql

# 6. Install system service
sudo cp deployment/factory-ai-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable factory-ai-backend
sudo systemctl start factory-ai-backend

# 7. Setup nginx reverse proxy
sudo cp deployment/nginx.conf /etc/nginx/sites-available/factory-ai
sudo ln -s /etc/nginx/sites-available/factory-ai /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

**nginx Configuration** (`deployment/nginx.conf`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: Docker Containerization

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: factory_ai
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./database/schema_v2.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/factory_ai
      CORS_ORIGINS: ${CORS_ORIGINS}
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./backend/app:/app/app

  frontend:
    build: ./frontend/frontend-app
    environment:
      VITE_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  db_data:
```

**Deploy**:
```bash
docker-compose up -d
docker-compose logs -f backend
```

### Option 3: AWS Elastic Beanstalk

**Create application**:
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.10 factory-ai

# Create environment
eb create factory-ai-prod

# Deploy
git push
eb deploy

# Monitor
eb open
```

### Option 4: Heroku

```bash
# Login
heroku login

# Create app
heroku create factory-ai-prod

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set CORS_ORIGINS=yourdomain.com

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## Health Monitoring

### Key Metrics to Monitor

```
Backend:
- CPU usage: < 70%
- Memory usage: < 80%
- API response time: < 2s
- Error rate: < 1%
- Request throughput: events/sec

Database:
- Connection count: < pool_size * 0.8
- Query time: < 1s (p95)
- Transaction log size: < 10GB
- Replication lag: < 1s

System:
- Disk usage: < 80%
- Network latency: < 100ms
- SSL certificate expiry: > 30 days
```

### Health Check Endpoint

```bash
# Check backend health
curl http://localhost:8000/health

# Response
{"status": "healthy", "timestamp": "2024-06-02T10:00:00Z"}
```

### Monitoring Dashboards

**Prometheus + Grafana** (Recommended):

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'factory-ai'
    static_configs:
      - targets: ['localhost:8000/metrics']
    scrape_interval: 15s
```

**CloudWatch** (AWS):
```bash
# View logs
aws logs tail /aws/elasticbeanstalk/factory-ai-prod/var/log/app.log --follow

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name factory-ai-errors \
  --metric-name ErrorCount \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

---

## Database Management

### Regular Maintenance

**Daily**:
```sql
-- Analyze query performance
ANALYZE;

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Monitor slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
```

**Weekly**:
```sql
-- Reindex fragmented indexes
REINDEX INDEX idx_attendance_logs_operator_id;

-- Vacuum to recover space
VACUUM ANALYZE;
```

**Monthly**:
```sql
-- Full database backup
pg_dump -U postgres factory_ai > backup_$(date +%Y%m%d).sql

-- Check and repair any issues
CHECKDB;

-- Archive old logs
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';
```

### Automated Backups

**Backup Script** (`backup_database.sh`):
```bash
#!/bin/bash

BACKUP_DIR="/backups"
DB_NAME="factory_ai"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup
pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql.gz s3://my-backups/factory-ai/
```

**Cron Job**:
```bash
# Run backup daily at 2 AM
0 2 * * * /path/to/backup_database.sh
```

### Database Recovery

```bash
# Review backup
gunzip < backup_20240602_020000.sql.gz | head -20

# Restore from backup
psql -U postgres factory_ai < backup_20240602_020000.sql.gz

# Verify restoration
psql -U postgres -d factory_ai -c "SELECT COUNT(*) FROM attendance_logs;"
```

---

## Performance Optimization

### Query Optimization

**Slow Query Identification**:
```sql
-- Enable slow query logging
SET log_min_duration_statement = 500;  -- Queries > 500ms

-- Find slow queries in logs
grep "Query took" /var/log/postgresql/postgresql.log | tail -20
```

**Index Analysis**:
```sql
-- Missing indexes
SELECT * FROM pg_stat_statements 
WHERE mean_time > 100  -- Queries taking > 100ms
ORDER BY mean_time DESC;

-- Unused indexes
SELECT * FROM pg_stat_user_indexes 
WHERE idx_scan = 0;

-- Add index if missing
CREATE INDEX idx_violations_operator_created 
ON violations(operator_id, created_at DESC);
```

### Caching Strategy

**Redis Integration**:

```python
# app/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=300):  # 5 minutes
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Call function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=60)
def get_dashboard_metrics():
    return DashboardService.get_dashboard_metrics(db)
```

### Connection Pool Tuning

```python
# app/database/__init__.py
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,              # Concurrent connections
    max_overflow=40,           # Queue overflow
    pool_pre_ping=True,        # Verify connections before use
    pool_recycle=3600,         # Recycle after 1 hour
    pool_timeout=30,           # Wait up to 30s for available connection
    echo=False                 # Don't log SQL (performance)
)
```

---

## Scaling Strategies

### Horizontal Scaling (Load Balancing)

**Load Balancer Configuration** (nginx):
```nginx
upstream backend {
    least_conn;  # Load balancing algorithm
    server backend1.local:8000;
    server backend2.local:8000;
    server backend3.local:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

### Vertical Scaling (Increase Resources)

- Increase PostgreSQL max_connections: `max_connections = 200`
- Increase backend worker count: 4 → 8 → 16
- Upgrade VM CPU: 2-core → 4-core → 8-core
- Upgrade VM RAM: 4GB → 8GB → 16GB

### Database Replication

**PostgreSQL Streaming Replication**:

```bash
# Primary server (master)
# Edit postgresql.conf
wal_level = replica
max_wal_senders = 3

# Secondary server (replica)
pg_basebackup -h primary-server -U replication_user -D /var/lib/postgresql/main -Pv -W
```

---

## Incident Response

### Database Down

```bash
# 1. Check status
psql -U postgres -d factory_ai

# 2. Restart service
sudo systemctl restart postgresql

# 3. Check logs
tail -100 /var/log/postgresql/postgresql.log

# 4. If corrupted, restore backup
psql -U postgres factory_ai < latest_backup.sql

# 5. Verify restoration
psql -U postgres -d factory_ai -c "SELECT COUNT(*) FROM attendance_logs;"
```

### Backend Not Responding

```bash
# 1. Check process
ps aux | grep uvicorn

# 2. Check logs
tail -100 /var/log/app.log

# 3. Kill and restart
pkill -f uvicorn
python -m uvicorn app.main:app

# 4. Check memory
free -h
top

# 5. Clear memory if needed
sync && echo 3 > /proc/sys/vm/drop_caches
```

### API Slow

```sql
-- Identify bottleneck
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 5;

-- Check missing indexes
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Add index
CREATE INDEX idx_name ON table(column);

-- Analyze plans
EXPLAIN ANALYZE SELECT * FROM attendance_logs 
WHERE operator_id = 1 AND created_at > NOW() - INTERVAL '7 days';
```

---

## Maintenance Windows

### Scheduled Maintenance

**Monthly Maintenance** (Sundays 2-3 AM):

```
1. Database optimization
   - VACUUM ANALYZE
   - REINDEX
   
2. Log cleanup
   - Delete logs > 90 days old
   - Compress oldest backups

3. Certificate renewal
   - Check SSL expiry
   - Auto-renew if < 30 days

4. Security updates
   - Apply PostgreSQL patches
   - Update Python dependencies
```

### Planned Downtime Communication

```
Email template:

Subject: Scheduled Maintenance - Factory AI System

Dear Users,

Factory AI will be unavailable for scheduled maintenance on:
- Date: Sunday, June 9, 2024
- Time: 2:00 AM - 3:00 AM EST
- Duration: ~1 hour

During this time:
- Dashboard will not be accessible
- New events will not be logged
- Reports cannot be generated

Thank you for your patience.

--Factory AI Team
```

---

## Disaster Recovery

### Recovery Time Objectives (RTO)
- **Critical databases**: < 1 hour
- **Backend services**: < 30 minutes
- **Frontend application**: < 15 minutes

### Recovery Point Objective (RPO)
- **Databases**: Hourly backups, < 1 hour data loss
- **Application code**: Git repository, < 1 hour
- **Configuration**: Version controlled, < 30 minutes

### Disaster Recovery Plan

```
1. DETECTION (0-5 minutes)
   - Alerting system triggers
   - On-call team notified
   - Incident Slack channel created

2. ASSESSMENT (5-15 minutes)
   - Determine scope and severity
   - Activate disaster recovery team
   - Begin communications

3. RECOVERY (15-60 minutes)
   - Failover to standby database
   - Restart backend services
   - Verify data integrity
   - Perform smoke tests

4. VALIDATION (60-90 minutes)
   - Gradual traffic restoration
   - Full system testing
   - Final sign-off

5. COMMUNICATION
   - Status updates every 30 minutes
   - Post-incident retrospective within 24 hours
```

---

## Compliance & Security

### Audit Logging

```python
# app/audit.py
from datetime import datetime

def log_audit(user_id, action, resource, status):
    audit_entry = {
        'timestamp': datetime.utcnow(),
        'user_id': user_id,
        'action': action,  # CREATE, UPDATE, DELETE
        'resource': resource,  # employees, violations, etc
        'resource_id': id,
        'status': status,  # success, failure
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent')
    }
    db.execute(AuditLog.insert().values(**audit_entry))
```

### Data Privacy

- **PII Masking**: Face images stored encrypted
- **Data Retention**: Delete events > 2 years old
- **Access Control**: Role-based permissions (Phase 2)
- **Encryption**: TLS for transit, AES-256 at rest

### Compliance Checks

```bash
# Regular security scans
python -m bandit -r app/          # Check for security issues
pip-audit --desc                   # Check dependencies
safety check                       # Verify no known vulnerabilities
```

---

## Metrics & KPIs

### System Health

| Metric | Target | Alert Level |
|--------|--------|-------------|
| Uptime | 99.9% | < 99.5% |
| Response Time | < 2s | > 5s |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 60% | > 80% |
| Memory Usage | < 70% | > 85% |
| Disk Usage | < 70% | > 85% |

### Business Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| Events Logged/Day | COUNT(attendance_logs) | > 1000 |
| Violations Detected/Day | COUNT(violations) | Varies |
| Compliance Score | (Compliant / Total) * 100 | > 85% |
| System Availability | Uptime / Total Time | 99.9% |

---

## Documentation Checklist

- [ ] Architecture diagrams updated
- [ ] Database schema documented
- [ ] API endpoints documented
- [ ] Deployment procedures documented
- [ ] Runbooks created for common issues
- [ ] Change log maintained
- [ ] Security policies documented

---

**Deployment Ready**: ✅
**Version**: 1.0.0
**Last Updated**: June 2, 2024

For questions or issues, see [backend/README.md](backend/README.md) or contact DevOps team.
