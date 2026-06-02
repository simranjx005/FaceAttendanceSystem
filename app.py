from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from database import (
    SessionLocal,
    Student,
    AttendanceRecord
)

app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def get_db():
    return SessionLocal()


def student_to_dict(student):
    return {
        "id": student.id,
        "roll_number": student.roll_number,
        "name": student.name,
        "department": student.department,
        "created_at": str(student.created_at)
    }


def attendance_to_dict(record):
    return {
        "id": record.id,
        "student_id": record.student_id,
        "student_name": record.student.name,
        "roll_number": record.student.roll_number,
        "session_name": record.session_name,
        "status": record.status,
        "confidence": round(record.confidence, 4),
        "attendance_date": str(record.attendance_date)
    }


# --------------------------------------------------
# API 1 - Home
# --------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "project": "Face Recognition Attendance System",
        "status": "running",
        "time": str(datetime.now())
    })


# --------------------------------------------------
# API 2 - Get All Students
# --------------------------------------------------

@app.route("/students", methods=["GET"])
def get_students():

    db = get_db()

    try:
        students = db.query(Student).all()

        return jsonify(
            [student_to_dict(s) for s in students]
        )

    finally:
        db.close()


# --------------------------------------------------
# API 3 - Get Student by Roll Number
# --------------------------------------------------

@app.route("/students/<roll>", methods=["GET"])
def get_student(roll):

    db = get_db()

    try:

        student = (
            db.query(Student)
            .filter(Student.roll_number == roll)
            .first()
        )

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify(
            student_to_dict(student)
        )

    finally:
        db.close()


# --------------------------------------------------
# API 4 - Delete Student
# --------------------------------------------------

@app.route("/students/<roll>", methods=["DELETE"])
def delete_student(roll):

    db = get_db()

    try:

        student = (
            db.query(Student)
            .filter(Student.roll_number == roll)
            .first()
        )

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        db.delete(student)
        db.commit()

        return jsonify({
            "message": f"{roll} deleted successfully"
        })

    finally:
        db.close()


# --------------------------------------------------
# API 5 - Get All Attendance
# --------------------------------------------------

@app.route("/attendance", methods=["GET"])
def get_attendance():

    db = get_db()

    try:

        records = (
            db.query(AttendanceRecord)
            .order_by(
                AttendanceRecord.attendance_date.desc()
            )
            .all()
        )

        return jsonify(
            [attendance_to_dict(r) for r in records]
        )

    finally:
        db.close()


# --------------------------------------------------
# API 6 - Attendance By Session
# --------------------------------------------------

@app.route("/attendance/session/<session_name>")
def attendance_by_session(session_name):

    db = get_db()

    try:

        records = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_name ==
                session_name
            )
            .all()
        )

        return jsonify(
            [attendance_to_dict(r) for r in records]
        )

    finally:
        db.close()


# --------------------------------------------------
# API 7 - Attendance By Student
# --------------------------------------------------

@app.route("/attendance/student/<roll>")
def attendance_by_student(roll):

    db = get_db()

    try:

        student = (
            db.query(Student)
            .filter(Student.roll_number == roll)
            .first()
        )

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        records = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.student_id ==
                student.id
            )
            .all()
        )

        return jsonify(
            [attendance_to_dict(r) for r in records]
        )

    finally:
        db.close()


# --------------------------------------------------
# API 8 - Dashboard Statistics
# --------------------------------------------------

@app.route("/dashboard", methods=["GET"])
def dashboard():

    db = get_db()

    try:

        total_students = (
            db.query(Student)
            .count()
        )

        total_attendance = (
            db.query(AttendanceRecord)
            .count()
        )

        present_count = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.status ==
                "Present"
            )
            .count()
        )

        late_count = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.status ==
                "Late"
            )
            .count()
        )

        return jsonify({
            "total_students": total_students,
            "total_attendance_records":
                total_attendance,
            "present_count":
                present_count,
            "late_count":
                late_count
        })

    finally:
        db.close()


# --------------------------------------------------
# Run Server
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )