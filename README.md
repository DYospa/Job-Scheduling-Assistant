# 🚀 Job Scheduling Assistant

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black)
![Database](https://img.shields.io/badge/Database-SQLite-green)
![Maps](https://img.shields.io/badge/Maps-Leaflet-blue)
![Routing](https://img.shields.io/badge/API-OSRM-orange)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## 📌 Overview
This project is a web-based application designed to help employers schedule employees who work at different locations rather than a central office.  
It allows users to create employees and jobs, automatically assign employees based on travel time, prevent scheduling conflicts, and visualize routes between locations.

---

## 🧠 System Design
- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, Bootstrap, Jinja
- **Routing & Maps:** OSRM API + Leaflet
- **Geolocation:** GeoPy

---

## 🗄️ Database

Main entities:
- **Employee**
- **Job**
- **Assignment**
- **Location**
- **Availability**

### Key Properties
- Normalized to **3NF / BCNF**
- Prevents overlapping job assignments
- Supports location-based scheduling
- Uses coordinates for routing and travel time

---

## ⚙️ Features

### 🔹 Core Features
- Add employees with address-based coordinates  
- Create jobs with time windows and required roles  
- View employees, jobs, and schedules  
- Manual assignment of employees  

### 🔥 Advanced Features
- Automatic employee assignment (shortest travel time)  
- Conflict detection (prevents overlapping jobs)  
- Travel time calculation using coordinates  
- Real driving route visualization (OSRM + Leaflet)  
- Dashboard analytics (jobs per employee, jobs per day)  

---

## 📊 Example Workflow

1. Add employees with addresses  
2. Create jobs with locations and time frames  
3. Automatically assign the best employee  
4. View route between employee and job  
5. Analyze workload using dashboard  

---

## ⚠️ Limitations
- Uses SQLite (not ideal for large-scale systems)  
- Routing does not account for real-time traffic  
- Limited to single-employee job assignments  
- No authentication system  

---

## 🚀 Future Improvements
- Add user authentication  
- Upgrade to PostgreSQL or MySQL  
- Implement traffic-aware routing  
- Support multiple employees per job  
- Add employee-side interface  

---

## ▶️ How to Run

```bash
git clone https://github.com/yourusername/job-scheduling-assistant.git
cd job-scheduling-assistant
pip install flask geopy requests
python app.py
