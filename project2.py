from datetime import datetime
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import sqlite3
import random

def seed_test_data(db, scheduler):
    print("=== Seeding Test Data ===")

    # ----------------------
    # Base Employees
    # ----------------------
    db.add_employee("Alice", "Technician", address="Atlanta, GA")
    db.add_employee("Bob", "Technician", address="Marietta, GA")
    db.add_employee("Charlie", "Electrician", address="Decatur, GA")
    db.add_employee("Diana", "Plumber", address="Sandy Springs, GA")
    db.add_employee("Ethan", "Technician", address="Roswell, GA")

    # ----------------------
    # Base Jobs
    # ----------------------
    db.create_job(
        "AC Repair",
        address="Georgia State University",
        start_time="2026-04-01 09:00:00",
        end_time="2026-04-01 11:00:00"
    )

    db.create_job(
        "Pipe Fix",
        address="Midtown Atlanta",
        start_time="2026-04-03 10:30:00",
        end_time="2026-04-03 12:30:00"
    )

    db.create_job(
        "Wiring Installation",
        address="Buckhead Atlanta",
        start_time="2026-04-07 13:00:00",
        end_time="2026-04-07 15:00:00"
    )

    db.create_job(
        "Maintenance Check",
        address="Downtown Atlanta",
        start_time="2026-04-12 09:00:00",
        end_time="2026-04-12 10:00:00"
    )

    # ----------------------
    # Random Data Generation
    # ----------------------
    first_names = ["John", "Mike", "Sara", "Anna", "Chris", "David", "Laura", "James", "Emma", "Noah"]
    roles = ["Technician", "Electrician", "Plumber"]

    locations = [
        "Atlanta, GA", "Marietta, GA", "Decatur, GA", "Roswell, GA",
        "Sandy Springs, GA", "Alpharetta, GA", "Duluth, GA",
        "Norcross, GA", "Lawrenceville, GA", "Kennesaw, GA"
    ]

    job_titles = [
        "Repair", "Installation", "Inspection", "Maintenance",
        "Wiring Job", "Pipe Work", "HVAC Fix", "Electrical Repair"
    ]

    # ----------------------
    # Add 50 Random Employees
    # ----------------------
    print("\n=== Adding Random Employees ===")
    for i in range(50):
        name = random.choice(first_names) + f"_{i}"
        role = random.choice(roles)
        address = random.choice(locations)

        try:
            db.add_employee(name, role, address=address)
        except Exception:
            pass

    # ----------------------
# Add 50 Random Jobs Spread Across April (mostly not April 1)
# ----------------------
    print("\n=== Adding Random Jobs ===")

    for i in range(50):
        title = random.choice(job_titles) + f" #{i}"
        address = random.choice(locations)

        # spread jobs across April 2-30 so April 1 does not get overloaded
        random_day = random.randint(2, 30)

        start_hour = random.randint(8, 16)
        duration = random.choice([1, 2])

        start_time = datetime(2026, 4, random_day, start_hour, 0, 0)
        end_time = datetime(2026, 4, random_day, start_hour + duration, 0, 0)

        try:
            db.create_job(
                title,
                address=address,
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S")
            )
        except Exception:
            pass

    # ----------------------
    # Assign All Jobs
    # ----------------------
    print("\n=== Assigning All Jobs ===")
    jobs = db.get_jobs()

    for job in jobs:
        try:
            result = scheduler.assign_best_employee(job.id)
            print(f"Job {job.id}: {result}")
        except Exception:
            pass

    # ----------------------
    # Travel Time Calculations
    # ----------------------
    print("\n=== Travel Time Calculations ===")
    employees = db.get_all_employees()

    for job in jobs[:5]:
        print(f"\nJob: {job.title}")
        for emp in employees[:5]:
            try:
                travel_time = calculate_travel_time(
                    emp.location[0], emp.location[1],
                    job.location[0], job.location[1]
                )
                print(f"{emp.name} → {round(travel_time, 2)} min")
            except Exception:
                continue

    # ----------------------
    # Best Recommendations
    # ----------------------
    print("\n=== Best Employee Recommendations ===")
    for job in jobs[:5]:
        print(f"\nJob: {job.title}")
        recommendations = scheduler.recommend_employees(job.id)
        for emp, travel_time in recommendations[:3]:
            print(f"{emp.name} → {round(travel_time, 2)} min")

    # ----------------------
    # Simulation Example
    # ----------------------
    print("\n=== Simulation Example ===")
    print(scheduler.simulate_assignment(1))

    # ----------------------
    # Aggregate Query
    # ----------------------
    print("\n=== Jobs Per Employee ===")
    for row in db.jobs_per_employee():
        print(f"{row[0]} → {row[1]} jobs")

    # ----------------------
    # Join Query
    # ----------------------
    print("\n=== Employee Schedule (ID = 1) ===")
    schedule = db.get_employee_schedule(1)
    for job in schedule:
        print(job.title, job.start_time, job.end_time)

    # ----------------------
    # Update Example
    # ----------------------
    print("\n=== Updating Job Title ===")
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE Job SET title = ? WHERE id = ?", ("Updated Job", 1))
    conn.commit()
    conn.close()

    # ----------------------
    # Delete Example
    # ----------------------
    print("\n=== Deleting Job ID 4 ===")
    db.delete_job(4)

    # ----------------------
    # Daily Schedule
    # ----------------------
    print("\n=== Daily Schedule (2026-04-01) ===")
    daily = scheduler.get_daily_schedule("2026-04-01")
    for job in daily[:10]:
        print(job.title, job.start_time)

    print("\n=== Seeding Complete ===")
# ----------------------
# Helper Functions
# ----------------------

def calculate_travel_time(lat1, lon1, lat2, lon2, speed_mph=30):
    distance = geodesic((lat1, lon1), (lat2, lon2)).miles
    return (distance / speed_mph) * 60


def get_coordinates_from_address(address, retries=3):
    geolocator = Nominatim(user_agent="job_scheduler_app")

    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        return None
    except GeocoderTimedOut:
        if retries > 0:
            return get_coordinates_from_address(address, retries - 1)
        return None


_geocode_cache = {}

def get_coordinates_cached(address):
    if address in _geocode_cache:
        return _geocode_cache[address]

    coords = get_coordinates_from_address(address)
    if coords:
        _geocode_cache[address] = coords
    return coords


# ----------------------
# Data Classes
# ----------------------

class Employee:
    def __init__(self, id, name, role, latitude, longitude):
        self.id = id
        self.name = name
        self.role = role
        self.location = (latitude, longitude)


class Job:
    def __init__(self, id, title, latitude, longitude, start_time, end_time):
        self.id = id
        self.title = title
        self.location = (latitude, longitude)
        self.start_time = start_time
        self.end_time = end_time


# ----------------------
# Database Initialization
# ----------------------

def initialize_database(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            latitude REAL,
            longitude REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Job (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            latitude REAL,
            longitude REAL,
            start_time TEXT,
            end_time TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Assignment (
            employee_id INTEGER,
            job_id INTEGER,
            PRIMARY KEY (employee_id, job_id),
            FOREIGN KEY (employee_id) REFERENCES Employee(id),
            FOREIGN KEY (job_id) REFERENCES Job(id)
        )
    """)

    conn.commit()


# ----------------------
# Database Manager (FIXED)
# ----------------------

class DatabaseManager:
    def __init__(self, get_conn):
        self.get_conn = get_conn

    def add_employee(self, name, role, latitude=None, longitude=None, address=None):
        if address and (latitude is None or longitude is None):
            coords = get_coordinates_cached(address)
            if not coords:
                raise ValueError("Invalid address")
            latitude, longitude = coords

        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Employee (name, role, latitude, longitude)
            VALUES (?, ?, ?, ?)
        """, (name, role, latitude, longitude))

        conn.commit()
        conn.close()

    def create_job(self, title, latitude=None, longitude=None, start_time=None, end_time=None, address=None):
        if address and (latitude is None or longitude is None):
            coords = get_coordinates_cached(address)
            if not coords:
                raise ValueError("Invalid address")
            latitude, longitude = coords

        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Job (title, latitude, longitude, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """, (title, latitude, longitude, start_time, end_time))

        conn.commit()
        conn.close()

    def get_jobs(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Job")
        rows = cursor.fetchall()

        conn.close()
        return [Job(*row) for row in rows]

    def get_all_employees(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Employee")
        rows = cursor.fetchall()

        conn.close()
        return [Employee(*row) for row in rows]

    def delete_job(self, job_id):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Job WHERE id = ?", (job_id,))
        conn.commit()
        conn.close()

    def get_employee_schedule(self, employee_id):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.id, j.title, j.latitude, j.longitude, j.start_time, j.end_time
            FROM Assignment a
            JOIN Job j ON a.job_id = j.id
            WHERE a.employee_id = ?
        """, (employee_id,))

        rows = cursor.fetchall()
        conn.close()
        return [Job(*row) for row in rows]

    def jobs_per_employee(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.name, COUNT(a.job_id)
            FROM Employee e
            LEFT JOIN Assignment a ON e.id = a.employee_id
            GROUP BY e.name
        """)

        rows = cursor.fetchall()
        conn.close()
        return rows

# ----------------------
# Scheduler (FIXED)
# ----------------------

class Scheduler:
    def __init__(self, db):
        self.db = db

    def is_employee_available(self, employee_id, start, end):
        conn = self.db.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM Assignment a
            JOIN Job j ON a.job_id = j.id
            WHERE a.employee_id = ?
            AND j.start_time < ?
            AND j.end_time > ?
        """, (employee_id, end, start))

        overlap_count = cursor.fetchone()[0]
        conn.close()

        return overlap_count == 0

    def get_travel_time_for_job(self, employee, job):
        return calculate_travel_time(
            employee.location[0], employee.location[1],
            job.location[0], job.location[1]
        )

    def recommend_employees(self, job_id):
        conn = self.db.get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Job WHERE id = ?", (job_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return []

        job = Job(*row)
        conn.close()

        employees = self.db.get_all_employees()

        results = []
        for emp in employees:
            if self.is_employee_available(emp.id, job.start_time, job.end_time):
                time = self.get_travel_time_for_job(emp, job)
                results.append((emp, time))

        return sorted(results, key=lambda x: x[1])

    def assign_best_employee(self, job_id):
        recs = self.recommend_employees(job_id)

        if not recs:
            return "No available employee"

        best = recs[0][0]

        conn = self.db.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Assignment (employee_id, job_id)
            VALUES (?, ?)
        """, (best.id, job_id))

        conn.commit()
        conn.close()

        return f"Assigned {best.name}"

    def get_daily_schedule(self, date):
        conn = self.db.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM Job
            WHERE start_time LIKE ?
        """, (date + "%",))

        rows = cursor.fetchall()
        conn.close()

        return [Job(*row) for row in rows]

    def simulate_assignment(self, job_id):
        recs = self.recommend_employees(job_id)

        return [
            {"employee": emp.name, "travel_time_min": round(t, 2)}
            for emp, t in recs[:5]
        ]

    def reschedule_job(self, job_id):
        conn = self.db.get_conn()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Assignment WHERE job_id = ?", (job_id,))
        conn.commit()
        conn.close()

        return self.assign_best_employee(job_id)

# ----------------------
# Main Function
# ----------------------

def get_connection():
    conn = sqlite3.connect("scheduler.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def main():
    conn = get_connection()
    initialize_database(conn)
    conn.close()

    db = DatabaseManager(get_connection)
    scheduler = Scheduler(db)

    seed_test_data(db, scheduler)


if __name__ == "__main__":
    main()