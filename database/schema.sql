-- ==============================
-- OPERATORS TABLE
-- ==============================

CREATE TABLE operators (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    shift_name VARCHAR(50),
    face_image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- CAMERAS TABLE
-- ==============================

CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    camera_name VARCHAR(100),
    rtsp_url TEXT,
    location_name VARCHAR(100),
    zone_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- EVENTS TABLE
-- ==============================

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER REFERENCES operators(id),
    camera_id INTEGER REFERENCES cameras(id),
    event_type VARCHAR(20),
    confidence_score FLOAT,
    snapshot_path TEXT,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- VIOLATIONS TABLE
-- ==============================

CREATE TABLE violations (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER REFERENCES operators(id),
    violation_type VARCHAR(100),
    violation_message TEXT,
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);