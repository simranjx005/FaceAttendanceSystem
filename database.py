# database.py

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import json

DATABASE_URL = "sqlite:///attendance.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)

    # Store FaceNet embeddings as JSON text
    embeddings = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    attendance_records = relationship(
        "AttendanceRecord",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def set_embeddings(self, embedding_list):
        self.embeddings = json.dumps(embedding_list)

    def get_embeddings(self):
        return json.loads(self.embeddings)

    def __repr__(self):
        return (
            f"<Student("
            f"roll='{self.roll_number}', "
            f"name='{self.name}', "
            f"dept='{self.department}')>"
        )


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    session_name = Column(String(100), nullable=False)

    attendance_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    status = Column(
        String(20),
        nullable=False
    )  # Present / Late

    confidence = Column(
        Float,
        default=0.0
    )

    student = relationship(
        "Student",
        back_populates="attendance_records"
    )

    def __repr__(self):
        return (
            f"<AttendanceRecord("
            f"student_id={self.student_id}, "
            f"session='{self.session_name}', "
            f"status='{self.status}')>"
        )


def create_database():
    Base.metadata.create_all(bind=engine)
    print("Database created successfully.")
    print("Tables:")
    print("  - students")
    print("  - attendance_records")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    create_database()