"""
Configuration settings for Factory AI Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DATABASE_URL: str = " "
    DATABASE_ECHO: bool = False  # Set to True for SQL debugging
    
    # API Configuration
    API_TITLE: str = "Factory AI Compliance Dashboard"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Real-time operator movement compliance tracking"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Compliance Rule Thresholds
    LONG_ABSENCE_THRESHOLD_MINUTES: int = 120  # 2 hours
    REPEAT_VIOLATION_THRESHOLD: int = 3        # 3 violations
    REPEAT_VIOLATION_DAYS: int = 7             # in 7 days
    EARLY_EXIT_THRESHOLD_MINUTES: int = 30     # 30 mins before shift end
    LATE_REPORTING_THRESHOLD_MINUTES: int = 15 # 15 mins after shift start
    
    # Face Recognition Thresholds
    MIN_CONFIDENCE_SCORE: float = 0.65
    DUPLICATE_EVENT_COOLDOWN_SECONDS: int = 30
    
    # Alert Configuration
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_SMS_ENABLED: bool = False
    ALERT_DASHBOARD_ENABLED: bool = True
    
    # Application Settings
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Compliance violation severity mapping
VIOLATION_SEVERITY = {
    "missing_department_entry": "high",
    "wrong_department_entry": "high",
    "dormitory_post_entry": "high",
    "early_department_exit": "medium",
    "long_absence_department": "medium",
    "repeat_violation": "high",
    "shift_non_compliance": "high",
    "late_reporting": "low",
}

# Zone categories for classification
ZONE_CATEGORIES = {
    "main_gate": "entry",
    "knitting": "department",
    "linking": "department",
    "finishing": "department",
    "washing": "department",
    "packing": "department",
    "dormitory": "common",
    "canteen": "common",
    "common_area": "common",
}
