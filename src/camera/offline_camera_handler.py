import asyncio
import threading
import time
import cv2

from camera.i_camera_handler import ICameraHandler

class OfflineCameraHandler(ICameraHandler):
    def __init__(self, video_path: str = None):
        self.video_path = video_path
        self.latest_frame = None
        self.running = False
        if self.video_path is None:
            self.video_path = "/home/luukb/python/video/2025_10_03_11_38_03_013649_smart-sprout.0000.rgb.mp4"
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
            self.latest_frame = frame
            time.sleep(0.03)

    async def get_frame(self):
        while self.latest_frame is None:
            await asyncio.sleep(0.001)
        return self.latest_frame

    async def stop(self):
        self.running = False
        self.cap.release()

