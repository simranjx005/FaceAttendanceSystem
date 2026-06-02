import os
import cv2
import argparse

from database import SessionLocal, Student
from recognition import FaceRecognitionEngine

CAPTURE_COUNT = 5


def enroll_student(roll, name, dept):
    engine = FaceRecognitionEngine()

    db = SessionLocal()

    existing = (
        db.query(Student)
        .filter(Student.roll_number == roll)
        .first()
    )

    if existing:
        print(f"[ERROR] Roll number {roll} already exists.")
        print("Delete the existing record before enrolling again.")
        db.close()
        return

    save_dir = os.path.join("captures", roll)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)

    embeddings = []
    sample_count = 0

    print("\n==============================")
    print("FACE ENROLLMENT SYSTEM")
    print("==============================")
    print(f"Student : {name}")
    print(f"Roll    : {roll}")
    print(f"Dept    : {dept}")
    print("\nInstructions:")
    print("- Position your face properly")
    print("- Press SPACE to start")
    print("- Press ESC anytime to cancel")
    print("- Slightly change face angle between captures")
    print("==============================\n")

    capture_started = False

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Camera error.")
            break

        faces = engine.detect_faces(frame)

        for (x, y, w, h) in faces:
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        if not capture_started:

            cv2.putText(
                frame,
                "PRESS SPACE TO START",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            cv2.imshow("Enrollment", frame)

            key = cv2.waitKey(1)

            if key == 32:  # SPACE
                capture_started = True
                print("\nCapturing samples...\n")

            elif key == 27:  # ESC
                print("Enrollment cancelled.")
                cap.release()
                cv2.destroyAllWindows()
                db.close()
                return

            continue

        for (x, y, w, h) in faces:

            face = frame[y:y+h, x:x+w]

            try:
                embedding = engine.generate_embedding(face)

                image_path = os.path.join(
                    save_dir,
                    f"{sample_count + 1}.jpg"
                )

                cv2.imwrite(image_path, face)

                embeddings.append(
                    embedding.tolist()
                )

                sample_count += 1

                print(
                    f"Captured sample "
                    f"{sample_count}/{CAPTURE_COUNT}"
                )

                cv2.waitKey(500)

            except Exception as e:
                print("Embedding error:", e)

            if sample_count >= CAPTURE_COUNT:
                break

        cv2.putText(
            frame,
            f"Captured: {sample_count}/{CAPTURE_COUNT}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow("Enrollment", frame)

        key = cv2.waitKey(1)

        if key == 27:
            print("Enrollment cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            db.close()
            return

        if sample_count >= CAPTURE_COUNT:
            break

    cap.release()
    cv2.destroyAllWindows()

    student = Student(
        roll_number=roll,
        name=name,
        department=dept
    )

    student.set_embeddings(embeddings)

    db.add(student)
    db.commit()

    print("\n==============================")
    print("ENROLLMENT SUCCESSFUL")
    print("==============================")
    print(f"Name       : {name}")
    print(f"Roll       : {roll}")
    print(f"Department : {dept}")
    print(f"Samples    : {len(embeddings)}")
    print("==============================")

    db.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--roll",
        required=True,
        help="Student Roll Number"
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Student Name"
    )

    parser.add_argument(
        "--dept",
        required=True,
        help="Department"
    )

    args = parser.parse_args()

    enroll_student(
        args.roll,
        args.name,
        args.dept
    )