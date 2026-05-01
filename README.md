# 🚀 Job Scheduling Assistant

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap-purple?logo=bootstrap)
![Status](https://img.shields.io/badge/Status-Complete-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Description

The **Job Scheduling Assistant** is a web application designed for employers who manage employees working at different locations instead of a central office. It allows users to create employees and jobs, assign employees based on availability and travel time, prevent scheduling conflicts, visualize routes, and analyze workload using a dashboard.

---

## ⚙️ Features

### 🔹 Basic Features
- Add and manage employees  
- Create and manage jobs  
- View employees and jobs  
- Manual job assignment  
- Daily schedule view  

### 🔥 Advanced Features
- Automatic employee assignment (based on travel time)  
- Conflict detection (prevents overlapping jobs)  
- Travel time calculation using coordinates  
- Real driving route visualization (OSRM + Leaflet)  
- Dashboard analytics (jobs per employee, jobs per day)  

---

## 🖼️ Screenshots

> 📌 Add screenshots to a `/screenshots` folder in your repo

### Home Page
![Home](screenshots/home.png)

### Jobs Page
![Jobs](screenshots/jobs.png)

### Route Map
![Map](screenshots/map.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask  
- **Database:** SQLite  
- **Frontend:** HTML, Bootstrap, Jinja  
- **Maps:** Leaflet  
- **Routing API:** OSRM  
- **Geolocation:** GeoPy  

---

## 🗄️ Database Design

Main tables:
- `Employee`
- `Job`
- `Assignment`
- `Location`
- `Availability`

The database is normalized (3NF / BCNF) and includes constraints such as:
- No overlapping job assignments  
- Role matching for jobs  
- Valid address → coordinate mapping  

---

