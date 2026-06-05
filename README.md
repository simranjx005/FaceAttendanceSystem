# 🎓 Face Recognition Attendance System

A Face Recognition Based Attendance Management System built using Python, FaceNet, OpenCV, Flask, Streamlit, SQLAlchemy, and SQLite.

The system automatically recognizes enrolled students and records attendance with timestamp and status (Present/Late).

## 🌐 Live Demo

The application is deployed and accessible online:

**Live Website:** 
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://faceattendancesystem-bckbavsdyhecddgwu4thw4.streamlit.app/)

Visit the link above to explore the dashboard, analytics, student records, and attendance reports.

## 🚀 Features

- Face Enrollment using Webcam
- Face Recognition using FaceNet Embeddings
- Automatic Attendance Marking
- SQLite Database Storage
- Flask REST API
- Streamlit Dashboard
- Attendance Analytics
- CSV Report Export
- Student Management
- Attendance History Tracking

---

## 🛠 Technologies Used

### Backend
- Python
- Flask
- SQLAlchemy
- SQLite

### Computer Vision
- OpenCV
- FaceNet
- PyTorch
- NumPy
- Scikit-Learn

### Dashboard
- Streamlit
- Plotly

---

## 📂 Project Structure

```text
FaceAttendanceSystem/
│
├── database.py
├── recognition.py
├── enroll.py
├── attendance.py
├── app.py
├── report.py
├── streamlit_app.py
├── requirements.txt
├── attendance.db
│
├── captures/
├── exports/
├── logs/
└── README.md
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/simranjx005/FaceAttendanceSystem.git
cd FaceAttendanceSystem
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

#### Windows

```bash
venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄 Create Database

```bash
python database.py
```

Expected Output:

```text
Database created successfully.
Tables:
- students
- attendance_records
```

---

## 👨‍🎓 Enroll Student

Example:

```bash
python enroll.py --roll 2401020495 --name "Shimran Jaiswal" --dept "CSE (AI & DS)"
```

Instructions:

1. Position your face in front of webcam
2. Press SPACE to start capture
3. System captures face samples
4. Embeddings are stored in database

---

## 📝 Take Attendance

```bash
python attendance.py --session "Lecture-01"
```

The system:

- Detects faces
- Generates embeddings
- Matches enrolled students
- Marks attendance automatically

---

## 🌐 Run Flask API

```bash
python app.py
```

Available at:

```text
http://127.0.0.1:5000
```

### API Endpoints

| Endpoint | Description |
|-----------|------------|
| `/` | Home |
| `/students` | List students |
| `/attendance` | Attendance records |
| `/dashboard` | Dashboard statistics |

---

## 📊 Run Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

Features:

- Dashboard Metrics
- Student Records
- Attendance Logs
- Analytics Charts
- CSV Reports

---

## 📈 Generate Reports

### Daily Report

```bash
python report.py --mode daily
```

### Weekly Report

```bash
python report.py --mode weekly
```

### Student Report

```bash
python report.py --mode student --roll 2401020495
```

### Summary Report

```bash
python report.py --mode summary
```

Generated reports are saved in:

```text
exports/
```

---

## 📸 Attendance Workflow

```text
Student Enrollment
        ↓
Face Embedding Generation
        ↓
Database Storage
        ↓
Live Recognition
        ↓
Attendance Marking
        ↓
Analytics & Reports
```

---

## 🔮 Future Enhancements

- Multi-user Support
- Cloud Database Integration
- Browser-Based Face Enrollment
- Real-Time Notifications
- Attendance Percentage Tracking
- Face Anti-Spoofing
- Mobile Application

---

## 👨‍💻 Author

**Shimran Jaiswal**

Department: CSE (AI & DS)

---

## 📜 License

This project is developed for educational and academic purposes.
