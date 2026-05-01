from flask import Flask, render_template, request, redirect, flash
import sqlite3
import requests

from project2 import DatabaseManager, Scheduler

app = Flask(__name__)
app.secret_key = "demo-secret-key"


# ----------------------
# Connection Factory
# ----------------------
def get_db():
    conn = sqlite3.connect("scheduler.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ----------------------
# Dependency Injection
# ----------------------
def get_scheduler():
    db = DatabaseManager(get_db)
    return Scheduler(db)


# ----------------------
# Home
# ----------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------
# Employees
# ----------------------
@app.route("/employees")
def employees():
    db = DatabaseManager(get_db)
    employees = db.get_all_employees()
    print(employees)
    return render_template("employees.html", employees=employees)

@app.route("/add_employee", methods=["POST"])
def add_employee():
    db = DatabaseManager(get_db)
    db.add_employee(
        request.form["name"],
        request.form["role"],
        address=request.form.get("address")
    )
    return redirect("/employees")

# ----------------------
# Jobs
# ----------------------
@app.route("/jobs")
def jobs():
    db = DatabaseManager(get_db)
    scheduler = get_scheduler()

    employees = db.get_all_employees()
    jobs_data = []

    for job in db.get_jobs():
        recs = scheduler.recommend_employees(job.id)

        if recs:
            best_emp, travel_time = recs[0]
            best_name = best_emp.name
            travel = round(travel_time, 2)
        else:
            best_name = "None"
            travel = "-"

        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "start_time": job.start_time,
            "end_time": job.end_time,
            "best_employee": best_name,
            "travel_time": travel
        })

    return render_template("jobs.html", jobs=jobs_data, employees=employees)


@app.route("/add_job", methods=["POST"])
def add_job():
    db = DatabaseManager(get_db)

    try:
        db.create_job(
            request.form["title"],
            address=request.form["address"],
            start_time=request.form["start_time"],
            end_time=request.form["end_time"]
        )
        flash("Job created successfully.", "success")
    except Exception as e:
        flash(f"Could not create job: {e}", "danger")

    return redirect("/jobs")


@app.route("/assign_manual", methods=["POST"])
def assign_manual():
    db = DatabaseManager(get_db)
    scheduler = get_scheduler()

    job_id = int(request.form["job_id"])
    employee_id = int(request.form["employee_id"])

    # get the job being assigned
    job = next((j for j in db.get_jobs() if j.id == job_id), None)
    if not job:
        flash("Job not found.", "danger")
        return redirect("/jobs")

    if not scheduler.is_employee_available(employee_id, job.start_time, job.end_time):
        flash("Employee already has an overlapping job.", "warning")
        return redirect("/jobs")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Assignment (employee_id, job_id)
        VALUES (?, ?)
    """, (employee_id, job_id))
    conn.commit()
    conn.close()

    flash("Employee assigned manually.", "success")
    return redirect("/jobs")

@app.route("/assign/<int:job_id>")
def assign(job_id):
    scheduler = get_scheduler()
    result = scheduler.assign_best_employee(job_id)

    if result and "Assigned" in result:
        flash(result, "success")
    else:
        flash("No available employee found.", "warning")

    return redirect("/jobs")


# ----------------------
# Map
# ----------------------
@app.route("/map/<int:job_id>")
def map_view(job_id):
    db = DatabaseManager(get_db)
    scheduler = get_scheduler()

    jobs = {job.id: job for job in db.get_jobs()}
    job = jobs.get(job_id)

    if not job:
        flash("Job not found.", "danger")
        return redirect("/jobs")

    recs = scheduler.recommend_employees(job_id)[:5]
    if not recs:
        flash("No employees available for this job.", "warning")
        return redirect("/jobs")

    routes = []

    for emp, _ in recs:
        url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{emp.location[1]},{emp.location[0]};"
            f"{job.location[1]},{job.location[0]}"
            f"?overview=full&geometries=geojson"
        )

        try:
            data = requests.get(url, timeout=10).json()
            if "routes" in data and data["routes"]:
                route = data["routes"][0]
                routes.append({
                    "emp": emp.name,
                    "emp_lat": emp.location[0],
                    "emp_lon": emp.location[1],
                    "geometry": route["geometry"],
                    "distance": round(route["distance"] / 1000, 2),
                    "duration": round(route["duration"] / 60, 2)
                })
        except Exception:
            continue

    if not routes:
        flash("Could not build routes for this job.", "danger")
        return redirect("/jobs")

    return render_template("map.html", job=job, routes=routes)


# ----------------------
# Schedule
# ----------------------
@app.route("/schedule")
def schedule():
    scheduler = get_scheduler()
    date = request.args.get("date")
    jobs = scheduler.get_daily_schedule(date) if date else []
    return render_template("schedule.html", jobs=jobs)


# ----------------------
# Dashboard
# ----------------------
@app.route("/dashboard")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Employee")
    employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Job")
    jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Assignment")
    assignments = cursor.fetchone()[0]

    cursor.execute("""
        SELECT e.name, COUNT(a.job_id)
        FROM Employee e
        LEFT JOIN Assignment a ON e.id = a.employee_id
        GROUP BY e.name
    """)
    jobs_per_employee = cursor.fetchall()

    cursor.execute("""
        SELECT substr(start_time, 1, 10), COUNT(*)
        FROM Job
        GROUP BY substr(start_time, 1, 10)
    """)
    jobs_per_day = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        employees=employees,
        jobs=jobs,
        assignments=assignments,
        jobs_per_employee=jobs_per_employee,
        jobs_per_day=jobs_per_day
    )


if __name__ == "__main__":
    app.run(debug=True)