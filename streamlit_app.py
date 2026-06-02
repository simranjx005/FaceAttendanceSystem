import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from database import SessionLocal, Student, AttendanceRecord

st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Face Recognition Attendance System")

db = SessionLocal()

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Students", "Attendance", "Analytics"]
)

if page == "Dashboard":
    total_students = db.query(Student).count()
    total_records = db.query(AttendanceRecord).count()
    present = db.query(AttendanceRecord).filter(
        AttendanceRecord.status == "Present"
    ).count()
    late = db.query(AttendanceRecord).filter(
        AttendanceRecord.status == "Late"
    ).count()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", total_students)
    c2.metric("Attendance", total_records)
    c3.metric("Present", present)
    c4.metric("Late", late)

    st.divider()

    pie_df = pd.DataFrame({
        "Status": ["Present", "Late"],
        "Count": [present, late]
    })

    st.plotly_chart(
        px.pie(
            pie_df,
            names="Status",
            values="Count",
            title="Attendance Distribution"
        ),
        use_container_width=True
    )

elif page == "Students":
    st.subheader("Students")

    search = st.text_input("Search")

    students = db.query(Student).all()

    rows = []
    for s in students:
        if (
            not search
            or search.lower() in s.name.lower()
            or search.lower() in s.roll_number.lower()
        ):
            rows.append({
                "Roll Number": s.roll_number,
                "Name": s.name,
                "Department": s.department,
                "Created": s.created_at
            })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif page == "Attendance":
    st.subheader("Attendance Records")

    records = db.query(AttendanceRecord).all()

    rows = []
    for r in records:
        rows.append({
            "Name": r.student.name,
            "Roll": r.student.roll_number,
            "Session": r.session_name,
            "Status": r.status,
            "Confidence": round(r.confidence, 4),
            "Date": r.attendance_date
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif page == "Analytics":
    st.subheader("Analytics")

    records = db.query(AttendanceRecord).all()

    rows = []
    for r in records:
        rows.append({
            "Student": r.student.name,
            "Status": r.status
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        chart = (
            df.groupby("Student")
            .size()
            .reset_index(name="Attendance Count")
        )

        st.plotly_chart(
            px.bar(
                chart,
                x="Student",
                y="Attendance Count",
                title="Attendance by Student"
            ),
            use_container_width=True
        )
    else:
        st.info("No attendance data available yet.")

db.close()
