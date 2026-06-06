"""
API routes package
"""
from app.api import attendance, violations, dashboard, employees, cameras, movement

__all__ = [
    "attendance",
    "violations",
    "dashboard",
    "employees",
    "cameras",
    "movement"
]
