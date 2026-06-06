-- ==============================
-- Factory AI Database Schema
-- Production-Ready Version
-- ==============================

-- Drop existing tables if needed (use with caution)
-- DROP TABLE IF EXISTS violations CASCADE;
-- DROP TABLE IF EXISTS attendance_logs CASCADE;
-- DROP TABLE IF EXISTS cameras CASCADE;
-- DROP TABLE IF EXISTS operators CASCADE;
-- DROP TABLE IF EXISTS zones CASCADE;


-- ==============================
-- OPERATORS TABLE (Employee Master)
-- ==============================
CREATE TABLE IF NOT EXISTS operators (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    shift_name VARCHAR(50),
    face_image_path TEXT,
    supervisor_id INTEGER,
    employment_status VARCHAR(20) DEFAULT 'active',
    line_section VARCHAR(100),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operators_dept_shift ON operators(department, shift_name);
CREATE INDEX idx_operators_status ON operators(employment_status);
CREATE INDEX idx_operators_employee_id ON operators(employee_id);


-- ==============================
-- CAMERAS TABLE (Camera Management)
-- ==============================
CREATE TABLE IF NOT EXISTS cameras (
    id SERIAL PRIMARY KEY,
    camera_name VARCHAR(100) NOT NULL,
    rtsp_url TEXT,
    location_name VARCHAR(100),
    zone_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'online',
    fps INTEGER,
    accuracy_percent INTEGER,
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cameras_zone_type ON cameras(zone_type);
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_cameras_name ON cameras(camera_name);


-- ==============================
-- ZONES TABLE (Zone Management)
-- ==============================
CREATE TABLE IF NOT EXISTS zones (
    id SERIAL PRIMARY KEY,
    zone_name VARCHAR(100) UNIQUE NOT NULL,
    zone_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_zones_type ON zones(zone_type);
CREATE INDEX idx_zones_name ON zones(zone_name);


-- ==============================
-- ATTENDANCE_LOGS TABLE (Event Logging)
-- ==============================
CREATE TABLE IF NOT EXISTS attendance_logs (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id),
    camera_id INTEGER NOT NULL REFERENCES cameras(id),
    zone_type VARCHAR(50),
    event_type VARCHAR(20) NOT NULL,
    confidence_score FLOAT,
    snapshot_path TEXT,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attendance_operator_time ON attendance_logs(operator_id, event_time DESC);
CREATE INDEX idx_attendance_camera_time ON attendance_logs(camera_id, event_time DESC);
CREATE INDEX idx_attendance_zone_time ON attendance_logs(zone_type, event_time DESC);
CREATE INDEX idx_attendance_event_type ON attendance_logs(event_type);


-- ==============================
-- VIOLATIONS TABLE (Compliance Rules)
-- ==============================
CREATE TABLE IF NOT EXISTS violations (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id),
    violation_type VARCHAR(100) NOT NULL,
    violation_message TEXT,
    severity VARCHAR(20) NOT NULL,
    related_event_id INTEGER REFERENCES attendance_logs(id),
    status VARCHAR(20) DEFAULT 'open',
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_violations_operator ON violations(operator_id, created_at DESC);
CREATE INDEX idx_violations_severity ON violations(severity, created_at DESC);
CREATE INDEX idx_violations_type ON violations(violation_type);
CREATE INDEX idx_violations_status ON violations(status);


-- ==============================
-- ALERTS TABLE (Alert Management)
-- ==============================
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    operator_id INTEGER REFERENCES operators(id),
    violation_id INTEGER REFERENCES violations(id),
    status VARCHAR(20) DEFAULT 'open',
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_status ON alerts(status, created_at DESC);
CREATE INDEX idx_alerts_operator ON alerts(operator_id, created_at DESC);


-- ==============================
-- AUDIT_LOGS TABLE (Audit Trail)
-- ==============================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    action VARCHAR(50),
    user_id VARCHAR(100),
    changes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);


-- ==============================
-- CAMERA_METRICS TABLE (Health Metrics)
-- ==============================
CREATE TABLE IF NOT EXISTS camera_metrics (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER NOT NULL REFERENCES cameras(id),
    fps FLOAT,
    uptime_percent FLOAT,
    accuracy_percent FLOAT,
    last_heartbeat TIMESTAMP,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_camera_metrics_camera_time ON camera_metrics(camera_id, recorded_at DESC);


-- ==============================
-- COMPLIANCE_RULES TABLE (Rule Definitions)
-- ==============================
CREATE TABLE IF NOT EXISTS compliance_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50),
    threshold INTEGER,
    severity VARCHAR(20),
    enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ==============================
-- Sample Data Insertion
-- ==============================

-- Insert sample zones
INSERT INTO zones (zone_name, zone_type, description) VALUES
    ('Main Gate', 'entry', 'Factory main entry point'),
    ('Knitting Department', 'department', 'Knitting production zone'),
    ('Linking Department', 'department', 'Linking production zone'),
    ('Finishing Department', 'department', 'Finishing production zone'),
    ('Washing Department', 'department', 'Washing production zone'),
    ('Packing Department', 'department', 'Packing production zone'),
    ('Dormitory', 'common', 'Employee dormitory'),
    ('Canteen', 'common', 'Company canteen'),
    ('Common Area', 'common', 'Common area for breaks')
ON CONFLICT (zone_name) DO NOTHING;

-- Insert sample compliance rules
INSERT INTO compliance_rules (rule_name, rule_type, threshold, severity, description) VALUES
    ('Missing Department Entry', 'missing_entry', NULL, 'high', 'Department entry without factory entry'),
    ('Wrong Department Entry', 'wrong_dept', NULL, 'high', 'Entry to wrong assigned department'),
    ('Dormitory Post Entry', 'dormitory_post_entry', NULL, 'high', 'Unauthorized dormitory access after factory entry'),
    ('Early Department Exit', 'early_exit', 30, 'medium', 'Department exit before 30 mins to shift end'),
    ('Long Absence', 'long_absence', 120, 'medium', 'Absence from department >120 minutes'),
    ('Shift Non-Compliance', 'shift_violation', NULL, 'high', 'Factory entry outside shift hours'),
    ('Late Reporting', 'late_report', 15, 'low', 'Reported >15 minutes late'),
    ('Repeat Violation', 'repeat_violation', 3, 'high', '3+ violations in 7 days')
ON CONFLICT DO NOTHING;

-- ==============================
-- End of Schema
-- ==============================
