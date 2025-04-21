import os
import io
import json
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
from datetime import datetime
import time
from dotenv import load_dotenv
from google.cloud import storage
from ai import inference_helper
from uploader import upload_frame_to_gcs

def launch_gui():
    window = tk.Tk()
    window.title("Dressing Site Feed")

    # Camera: Channel 0 for built-in camera, 1 for USB/Bluetooth
    cap = cv2.VideoCapture(1)
    video_label = tk.Label(window)
    video_label.pack()

    # Auto-Capture setup
    auto_running = False
    interval_seconds = tk.IntVar(value=10)
    countdown_label = tk.Label(window, text="")
    countdown_label.pack(pady=5)

    def update_countdown(text):
        countdown_label.config(text=text)

    def update_video_feed():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
        video_label.after(10, update_video_feed)

    def take_snapshot():
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image")
            return

        def send_api():
            try:
                result, annotated_image_bytes, buffer = inference_helper(frame)
                print("Roboflow Result:", result)

                if result.get("predictions"):
                    upload_frame_to_gcs(buffer, result, annotated_image_bytes)
                    messagebox.showinfo("Result", "Inference complete. Annotated image and prediction JSON uploaded to GCS.")
                else:
                    messagebox.showinfo("Result", "No predictions were made.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=send_api).start()

    def auto_capture_loop():
        nonlocal auto_running
        while auto_running:
            for i in range(interval_seconds.get(), 0, -1):
                if not auto_running:
                    update_countdown("Auto-Capture stopped")
                    return
                update_countdown(f"Next snapshot in: {i}s")
                time.sleep(1)
            take_snapshot()

    def start_auto_capture():
        nonlocal auto_running
        if not auto_running:
            auto_running = True
            threading.Thread(target=auto_capture_loop, daemon=True).start()

    def stop_auto_capture():
        nonlocal auto_running
        auto_running = False
        update_countdown("Auto-Capture stopped")

    tk.Button(window, text="Capture & Analyze", command=take_snapshot).pack(pady=10)

    auto_frame = tk.Frame(window)
    auto_frame.pack(pady=10)

    tk.Label(auto_frame, text="Auto-capture interval (sec):").pack(side="left")
    tk.Entry(auto_frame, textvariable=interval_seconds, width=5).pack(side="left", padx=5)
    tk.Button(auto_frame, text="Start Auto-Capture", command=start_auto_capture).pack(side="left", padx=5)
    tk.Button(auto_frame, text="Stop Auto-Capture", command=stop_auto_capture).pack(side="left")

    update_video_feed()
    window.mainloop()

    cap.release()
    cv2.destroyAllWindows()