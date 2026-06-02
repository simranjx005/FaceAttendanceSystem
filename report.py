import argparse
import os
from datetime import datetime, timedelta

import pandas as pd

from database import (
    SessionLocal,
    Student,
    AttendanceRecord
)

EXPORT_DIR = "exports"


def ensure_export_dir():
    os.makedirs(EXPORT_DIR, exist_ok=True)


def export_dataframe(df, filename):
    ensure_export_dir()

    path = os.path.join(EXPORT_DIR, filename)

    df.to_csv(path, index=False)

    print(f"\nCSV Exported:")
    print(path)


def daily_report():
    db = SessionLocal()

    try:

        today = datetime.now().date()

        records = db.query(
            AttendanceRecord
        ).all()

        data = []

        for r in records:

            if r.attendance_date.date() == today:

                data.append({
                    "Student ID": r.student_id,
                    "Name": r.student.name,
                    "Roll Number": r.student.roll_number,
                    "Department": r.student.department,
                    "Session": r.session_name,
                    "Status": r.status,
                    "Confidence": round(
                        r.confidence, 4
                    ),
                    "Date": r.attendance_date
                })

        df = pd.DataFrame(data)

        print("\nDAILY REPORT")
        print(df)

        export_dataframe(
            df,
            f"daily_report_{today}.csv"
        )

    finally:
        db.close()


def weekly_report():
    db = SessionLocal()

    try:

        today = datetime.now()
        week_start = today - timedelta(days=7)

        records = db.query(
            AttendanceRecord
        ).all()

        data = []

        for r in records:

            if r.attendance_date >= week_start:

                data.append({
                    "Student ID": r.student_id,
                    "Name": r.student.name,
                    "Roll Number": r.student.roll_number,
                    "Department": r.student.department,
                    "Session": r.session_name,
                    "Status": r.status,
                    "Confidence": round(
                        r.confidence, 4
                    ),
                    "Date": r.attendance_date
                })

        df = pd.DataFrame(data)

        print("\nWEEKLY REPORT")
        print(df)

        export_dataframe(
            df,
            "weekly_report.csv"
        )

    finally:
        db.close()


def student_report(roll):
    db = SessionLocal()

    try:

        student = (
            db.query(Student)
            .filter(
                Student.roll_number == roll
            )
            .first()
        )

        if not student:
            print(
                f"Student {roll} not found."
            )
            return

        records = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.student_id ==
                student.id
            )
            .all()
        )

        data = []

        for r in records:

            data.append({
                "Name": student.name,
                "Roll Number":
                    student.roll_number,
                "Department":
                    student.department,
                "Session":
                    r.session_name,
                "Status":
                    r.status,
                "Confidence":
                    round(
                        r.confidence,
                        4
                    ),
                "Date":
                    r.attendance_date
            })

        df = pd.DataFrame(data)

        print(
            f"\nREPORT FOR "
            f"{student.name}"
        )
        print(df)

        export_dataframe(
            df,
            f"{roll}_attendance.csv"
        )

    finally:
        db.close()


def summary_report():
    db = SessionLocal()

    try:

        students = db.query(
            Student
        ).all()

        summary = []

        for s in students:

            records = (
                db.query(
                    AttendanceRecord
                )
                .filter(
                    AttendanceRecord.student_id
                    == s.id
                )
                .all()
            )

            total = len(records)

            present = len([
                r for r in records
                if r.status == "Present"
            ])

            late = len([
                r for r in records
                if r.status == "Late"
            ])

            summary.append({
                "Roll Number":
                    s.roll_number,
                "Name":
                    s.name,
                "Department":
                    s.department,
                "Total Attendance":
                    total,
                "Present":
                    present,
                "Late":
                    late
            })

        df = pd.DataFrame(summary)

        print("\nSUMMARY REPORT")
        print(df)

        export_dataframe(
            df,
            "summary_report.csv"
        )

    finally:
        db.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "daily",
            "weekly",
            "student",
            "summary"
        ]
    )

    parser.add_argument(
        "--roll",
        help="Student Roll Number"
    )

    args = parser.parse_args()

    if args.mode == "daily":
        daily_report()

    elif args.mode == "weekly":
        weekly_report()

    elif args.mode == "summary":
        summary_report()

    elif args.mode == "student":

        if not args.roll:
            print(
                "Please provide --roll"
            )

        else:
            student_report(
                args.roll
            )