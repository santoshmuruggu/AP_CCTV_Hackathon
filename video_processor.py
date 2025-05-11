# video_processor.py

import cv2
import os
import numpy as np
import easyocr
from datetime import datetime
from ultralytics import YOLO
import face_recognition

from db import SessionLocal, GunnyBagEvent, VehicleLog, FaceLog, Vehicle, User

# === Load YOLO Models ===
bag_model = YOLO("gunny_bag.pt")
plate_model = YOLO("number_plate.pt")

# === OCR Reader ===
reader = easyocr.Reader(['en'], gpu=False)

# === Load Known Faces ===
known_encodings = []
known_names = []
KNOWN_FACES_DIR = "known_faces"

if not os.path.exists(KNOWN_FACES_DIR):
    raise FileNotFoundError("The 'known_faces' folder is missing.")

for file in os.listdir(KNOWN_FACES_DIR):
    if file.lower().endswith(('.jpg', '.png')):
        img_path = os.path.join(KNOWN_FACES_DIR, file)
        img = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(file)[0])

# === Main Processing Function ===
def process_video(video_path):
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {video_path}")

    db = SessionLocal()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = datetime.now()

            # --- Gunny Bag Detection ---
            bag_results = bag_model.predict(source=frame, verbose=False)[0]
            bag_count = sum(1 for box in bag_results.boxes if bag_model.names[int(box.cls[0])].lower() == "gunny bag")

            if bag_count > 0:
                db.add(GunnyBagEvent(
                    timestamp=timestamp,
                    camera_id="CAM-1",
                    location_zone="AutoZone",
                    bag_count=bag_count,
                    estimated_volume=bag_count * 50.0
                ))

            # --- License Plate Detection ---
            plate_results = plate_model.predict(source=frame, verbose=False)[0]
            for box in plate_results.boxes:
                cls = int(box.cls[0])
                name = plate_model.names[cls].lower()
                if "plate" in name:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    crop = frame[y1:y2, x1:x2]
                    ocr_result = reader.readtext(crop)

                    if ocr_result:
                        plate_text = ocr_result[0][1].replace(" ", "")
                        vehicle = db.query(Vehicle).filter_by(license_plate=plate_text).first()
                        status = "Authorized" if vehicle and vehicle.is_authorized else "Unauthorized"

                        db.add(VehicleLog(
                            timestamp=timestamp,
                            camera_id="CAM-1",
                            license_plate=plate_text,
                            confidence=float(box.conf[0]) * 100,
                            status=status
                        ))

            # --- Face Detection ---
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)
            face_encodings = face_recognition.face_encodings(rgb, face_locations)

            for encoding in face_encodings:
                matches = face_recognition.compare_faces(known_encodings, encoding)
                name = "UNKNOWN"
                status = "Intrusion"
                user_id = None

                if True in matches:
                    idx = matches.index(True)
                    name = known_names[idx]
                    user = db.query(User).filter_by(name=name).first()
                    if user:
                        user_id = user.id
                        status = "Verified"

                db.add(FaceLog(
                    timestamp=timestamp,
                    camera_id="CAM-1",
                    user_id=user_id,
                    confidence=95.0,
                    status=status
                ))

            db.commit()

    finally:
        cap.release()
        db.close()
        print("✅ Video processing complete. All data saved to the database.")


# === Run Script ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python video_processor.py <path_to_video>")
        sys.exit(1)

    video_path = sys.argv[1]
    process_video(video_path)
