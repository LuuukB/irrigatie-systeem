# camera_factory.py
import asyncio
from pathlib import Path
from typing import Dict
from camera.i_camera_handler  import ICameraHandler

class CameraFactory:
    """Factory en manager voor meerdere camera's tegelijk."""

    def __init__(self):
        self.cameras: List[ICameraHandler] = {}

    def add_camera_online(self, name: str, stream_name: str = "rgb"):
        """Voeg een realtime camera aan de factory."""
        from camera.camera_handler import CameraHandler
        return CameraHandler(name, stream_name)

    def add_camera_offline(self, source: str = None):
        """Voeg een offline camera aan de factory."""
        from camera.offline_camera_handler import OfflineCameraHandler
        return OfflineCameraHandler(source)

    async def start_all(self):
        """Start alle camera's async."""
        print("start camera async.")
        await asyncio.gather(*(cam.start() for cam in self.cameras.values()))

    async def stop_all(self):
        """Stop alle camera's async."""
        await asyncio.gather(*(cam.stop() for cam in self.cameras.values()))
