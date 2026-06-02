# recognition.py

import cv2
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1
from sklearn.metrics.pairwise import cosine_similarity

from database import SessionLocal, Student


class FaceRecognitionEngine:
    def __init__(self, similarity_threshold=0.70):
        self.similarity_threshold = similarity_threshold

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print(f"[INFO] Using device: {self.device}")

        self.model = InceptionResnetV1(
            pretrained="vggface2"
        ).eval().to(self.device)

        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

    # ---------------------------------------------------------
    # Face Detection
    # ---------------------------------------------------------
    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(60, 60)
        )

        return faces

    # ---------------------------------------------------------
    # Face Preprocessing
    # ---------------------------------------------------------
    def preprocess_face(self, face_img):
        face_rgb = cv2.cvtColor(
            face_img,
            cv2.COLOR_BGR2RGB
        )

        pil_img = Image.fromarray(face_rgb)

        pil_img = pil_img.resize((160, 160))

        face_array = np.array(pil_img).astype(np.float32)

        face_array = (face_array - 127.5) / 128.0

        tensor = (
            torch.tensor(face_array)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .float()
            .to(self.device)
        )

        return tensor

    # ---------------------------------------------------------
    # Generate Embedding
    # ---------------------------------------------------------
    @torch.no_grad()
    def generate_embedding(self, face_img):
        tensor = self.preprocess_face(face_img)

        embedding = self.model(tensor)

        embedding = (
            embedding
            .cpu()
            .numpy()
            .flatten()
        )

        return embedding

    # ---------------------------------------------------------
    # Compare Embeddings
    # ---------------------------------------------------------
    def compare_embeddings(self, emb1, emb2):
        score = cosine_similarity(
            [emb1],
            [emb2]
        )[0][0]

        return float(score)

    # ---------------------------------------------------------
    # Load Students from Database
    # ---------------------------------------------------------
    def load_students(self):
        db = SessionLocal()

        try:
            students = db.query(Student).all()

            data = []

            for student in students:
                embeddings = student.get_embeddings()

                data.append({
                    "student": student,
                    "embeddings": embeddings
                })

            return data

        finally:
            db.close()

    # ---------------------------------------------------------
    # Recognize Face
    # ---------------------------------------------------------
    def recognize(self, face_img):
        query_embedding = self.generate_embedding(face_img)

        students = self.load_students()

        best_score = -1
        best_student = None

        for item in students:

            student = item["student"]

            embeddings = item["embeddings"]

            for emb in embeddings:

                score = self.compare_embeddings(
                    query_embedding,
                    np.array(emb)
                )

                if score > best_score:
                    best_score = score
                    best_student = student

        if (
            best_student is not None
            and best_score >= self.similarity_threshold
        ):
            return {
                "matched": True,
                "student": best_student,
                "confidence": round(best_score, 4)
            }

        return {
            "matched": False,
            "student": None,
            "confidence": round(best_score, 4)
        }

    # ---------------------------------------------------------
    # Draw Bounding Box
    # ---------------------------------------------------------
    def draw_result(
        self,
        frame,
        x,
        y,
        w,
        h,
        label,
        confidence=None
    ):
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        text = label

        if confidence is not None:
            text += f" ({confidence:.2f})"

        cv2.putText(
            frame,
            text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        return frame


# ---------------------------------------------------------
# Utility Function
# ---------------------------------------------------------
def get_engine():
    return FaceRecognitionEngine()


# ---------------------------------------------------------
# Test Module
# ---------------------------------------------------------
if __name__ == "__main__":

    engine = FaceRecognitionEngine()

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        faces = engine.detect_faces(frame)

        for (x, y, w, h) in faces:

            face = frame[y:y+h, x:x+w]

            try:
                result = engine.recognize(face)

                if result["matched"]:
                    label = result["student"].name
                    confidence = result["confidence"]

                else:
                    label = "Unknown"
                    confidence = result["confidence"]

                engine.draw_result(
                    frame,
                    x,
                    y,
                    w,
                    h,
                    label,
                    confidence
                )

            except Exception as e:
                print("Recognition error:", e)

        cv2.imshow(
            "Face Recognition Test",
            frame
        )

        key = cv2.waitKey(1)

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()