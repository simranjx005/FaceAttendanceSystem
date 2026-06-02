import cv2
import argparse
from datetime import datetime

from database import SessionLocal, Student, AttendanceRecord
from recognition import FaceRecognitionEngine


ATTENDANCE_WINDOW = "Attendance System"

# Change this if your class starts at a different time
LATE_AFTER_HOUR = 9
LATE_AFTER_MINUTE = 15


def get_attendance_status():
    now = datetime.now()

    if (
        now.hour > LATE_AFTER_HOUR
        or (
            now.hour == LATE_AFTER_HOUR
            and now.minute > LATE_AFTER_MINUTE
        )
    ):
        return "Late"

    return "Present"


def already_marked(db, student_id, session_name):
    record = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.session_name == session_name
        )
        .first()
    )

    return record is not None


def mark_attendance(
    db,
    student,
    session_name,
    confidence
):
    if already_marked(
        db,
        student.id,
        session_name
    ):
        return False

    status = get_attendance_status()

    record = AttendanceRecord(
        student_id=student.id,
        session_name=session_name,
        status=status,
        confidence=float(confidence)
    )

    db.add(record)
    db.commit()

    print(
        f"[ATTENDANCE] "
        f"{student.name} "
        f"({student.roll_number}) "
        f"-> {status}"
    )

    return True


def start_attendance(session_name):

    engine = FaceRecognitionEngine()

    db = SessionLocal()

    cap = cv2.VideoCapture(0)

    print("\n================================")
    print("ATTENDANCE SESSION STARTED")
    print("================================")
    print(f"Session : {session_name}")
    print("Press ESC to stop")
    print("================================\n")

    marked_students = set()

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Camera error.")
            break

        faces = engine.detect_faces(frame)

        for (x, y, w, h) in faces:

            face = frame[y:y+h, x:x+w]

            try:

                result = engine.recognize(face)

                if result["matched"]:

                    student = result["student"]
                    confidence = result["confidence"]

                    label = (
                        f"{student.name}"
                    )

                    engine.draw_result(
                        frame,
                        x,
                        y,
                        w,
                        h,
                        label,
                        confidence
                    )

                    if student.roll_number not in marked_students:

                        success = mark_attendance(
                            db,
                            student,
                            session_name,
                            confidence
                        )

                        if success:
                            marked_students.add(
                                student.roll_number
                            )

                else:

                    engine.draw_result(
                        frame,
                        x,
                        y,
                        w,
                        h,
                        "Unknown",
                        result["confidence"]
                    )

            except Exception as e:
                print(
                    "Recognition error:",
                    e
                )

        cv2.imshow(
            ATTENDANCE_WINDOW,
            frame
        )

        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    db.close()

    print("\nAttendance session ended.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--session",
        required=True,
        help="Session Name"
    )

    args = parser.parse_args()

    start_attendance(
        args.session
    )