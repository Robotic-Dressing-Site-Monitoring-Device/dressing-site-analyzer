# uploader.py
import os
import io
import json
from datetime import datetime
from google.cloud import storage
from dotenv import load_dotenv

# env configuration
load_dotenv()
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCS_TARGET_FOLDER = os.getenv("GCS_TARGET_FOLDER")
GCS_KEY_PATH = os.getenv("GCS_KEY_PATH")

def upload_frame_to_gcs(frame_buffer, inference_result=None, annotated_image_bytes=None):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folder_path = f"{GCS_TARGET_FOLDER}/{timestamp}/"

    # Encoding image into bytes (only used for the raw image, but we're using the image from Roboflow. Just leaving this in in case.)
    buffer = frame_buffer
    image_bytes = io.BytesIO(buffer.tobytes())

    # Initialize GCS connection
    storage_client = storage.Client.from_service_account_json(GCS_KEY_PATH)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    # Upload inference result JSON
    if inference_result:
        json_bytes = io.BytesIO(json.dumps(inference_result, indent=2).encode("utf-8"))
        json_blob = bucket.blob(f"{folder_path}result.json")
        json_blob.upload_from_file(json_bytes, content_type="application/json")
        print(f"Uploaded JSON to gs://{GCS_BUCKET_NAME}/{folder_path}result.json")

    # Upload image
    if annotated_image_bytes:
        annotated_blob = bucket.blob(f"{folder_path}annotated.jpg")
        annotated_blob.upload_from_file(io.BytesIO(annotated_image_bytes), content_type="image/jpeg")
        print(f"Uploaded annotated image to gs://{GCS_BUCKET_NAME}/{folder_path}annotated.jpg")

    return folder_path
