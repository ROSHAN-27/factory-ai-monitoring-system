import psycopg2

# ---------------- DATABASE CONNECTION ----------------

conn = psycopg2.connect(
    host="localhost",
    database="factory_ai",
    user="postgres",
    password="GR1dn9k3"
)

cursor = conn.cursor()

# ---------------- SAVE ATTENDANCE ----------------

def save_attendance(name, event_type, camera_name):

    query = """
    INSERT INTO attendance_logs
    (employee_name, event_type, camera_name)
    VALUES (%s, %s, %s)
    """

    values = (name, event_type, camera_name)

    cursor.execute(query, values)

    conn.commit()

    print(f"Saved to DB: {name} {event_type}")