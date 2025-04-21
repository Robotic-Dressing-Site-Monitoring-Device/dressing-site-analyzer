import os
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
import requests

# env configuration
load_dotenv()
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID")
ROBOFLOW_API_URL = os.getenv("ROBOFLOW_API_URL", "https://serverless.roboflow.com")

# Gets Roboflow prediction JSON
def run_inference_json(image_path):
    url = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}"
    with open(image_path, "rb") as img_file:
        response = requests.post(url, files={"file": img_file})
        return response.json()

# Gets Roboflow annotated image 
def run_inference_with_annotated_image(image_path):
    # Modifiers: format=image -> bounding boxes, labels=on -> class labels on bounding boxes, nothing -> raw.
    url = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}&format=image"
    with open(image_path, "rb") as img_file:
        image_response = requests.post(url, files={"file": img_file})
    json_result = run_inference_json(image_path)
    return json_result, image_response.content if image_response.headers.get("Content-Type", "").startswith("image") else None

# Takes the snapshot and starts the API process
def inference_helper(frame):
    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
        raise ValueError("Failed to encode frame")

    temp_path = "temp_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(buffer)

    result, annotated_image = run_inference_with_annotated_image(temp_path)
    return result, annotated_image, buffer
