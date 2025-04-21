# uploader.py
import os
import io
import json
from datetime import datetime, timezone
from google.cloud import storage, firestore
from dotenv import load_dotenv
import base64

# env configuration
load_dotenv()
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCS_TARGET_FOLDER = os.getenv("GCS_TARGET_FOLDER")
GCS_KEY_PATH = os.getenv("GCS_KEY_PATH")
TEST_PATIENT = os.getenv("PATIENT_ID")

# Uploads raw image to GCS bucket and returns image URL.
def upload_frame_to_gcs(image_bytes, photo_name):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folder_path = f"{GCS_TARGET_FOLDER}/"
    blob_path = f"{folder_path}{photo_name}.jpg"

    client = storage.Client.from_service_account_json(GCS_KEY_PATH)
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(blob_path)

    blob.upload_from_file(io.BytesIO(image_bytes), content_type="image/jpeg")
    blob.make_public()

    print(f"Uploaded image to: {blob.public_url}")
    return blob.public_url, photo_name

# Creates firestore doc. Firestore will handle the Roboflow model API internally.
def upload_frame_to_firestore(image_url, photo_name):
    db = firestore.Client.from_service_account_json(GCS_KEY_PATH)
    timestamp = datetime.now(timezone.utc).isoformat()

    doc_path = f"patients/{TEST_PATIENT}/photos/{timestamp}"
    doc_ref = db.document(doc_path)

    data = {
        "analyzed": False,
        "imageURL": image_url,
        "issue": "unknown",
        "patient": TEST_PATIENT.replace("_", " ").title(),
        "photoName": photo_name,
        "status": "pending",
        "time": timestamp
    }

    doc_ref.set(data)
    print(f"Firestore doc written to: {doc_path}")