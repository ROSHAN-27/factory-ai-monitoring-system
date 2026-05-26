from fastapi import APIRouter
import psycopg2

router = APIRouter()

# PostgreSQL Connection

conn = psycopg2.connect(
    host="localhost",
    database="factory_ai",
    user="postgres",
    password="GR1dn9k3"
)

# ---------------- GET ATTENDANCE ----------------

@router.get("/attendance")

def get_attendance():

    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_name,
               event_type,
               camera_name,
               created_at
        FROM attendance_logs
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    data = []

    for row in rows:

        data.append({
            "employee_name": row[0],
            "event_type": row[1],
            "camera_name": row[2],
            "created_at": str(row[3])
        })

    return data