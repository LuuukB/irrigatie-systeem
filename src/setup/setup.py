import asyncio
from factory.camera_factory import CameraFactory
from camera.i_camera_handler import ICameraHandler

from typing import Dict

class Setup:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            print("creating instance: setup")
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            print("already has setup")
            return

        self._initialized = True

        self.robot_online = self.check_status()
        self.camera_factory = CameraFactory()
        self._cameras: Dict[str, ICameraHandler] = {}

    async def initialize_canbus(self):
        # hier moet canbus setup komen
        await asyncio.sleep(0.1)

    async def get_camera(self, name: str):
        if name not in self._cameras:
            if self.robot_online:
                cam = self.camera_factory.add_camera_online(name)
                await cam.start()
            else:
                cam = self.camera_factory.add_camera_offline()
                print(f"made cam {name}")
                await cam.start()
            self._cameras[name] = cam

        return self._cameras[name]

    def check_status(self):
        return False  # tijdelijk

    async def stop(self):
        await self.camera_factory.stop_all()
