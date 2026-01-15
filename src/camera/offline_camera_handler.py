import asyncio
import threading
import time
import cv2

from threading import Lock
from camera.i_camera_handler import ICameraHandler

class OfflineCameraHandler(ICameraHandler):
    def __init__(self, video_path: str = None):
        self.video_path = video_path
        self.latest_frame = None
        self.running = False
        self.lock = Lock()
        if self.video_path is None:
            self.video_path = "/home/luukb/python/video/test2oak2.rgb.mp4"
            self.cap = cv2.VideoCapture(self.video_path)
        else:
            self.cap = cv2.VideoCapture(self.video_path)

    async def start(self):
        self.running = True
        if not self.cap.isOpened():
            raise ValueError(f"Kan video niet openen: {self.video_path}")
        threading.Thread(target=self.reader, daemon=True).start()

    def reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                # herstart video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    raise RuntimeError("Kan geen frame meer ophalen uit video")
            with self.lock:
                self.latest_frame = frame
            time.sleep(0.3)

    async def get_frame(self):
        while True:
            with self.lock:
                if self.latest_frame is not None:
                    return self.latest_frame
            await asyncio.sleep(0.001)

    async def stop(self):
        self.running = False
        self.cap.release()

