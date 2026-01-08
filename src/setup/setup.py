import asyncio
from factory.camera_factory import CameraFactory
from processing.image_filter import ImageFilter
from camera.i_camera_handler import ICameraHandler
from factory.can_bus_factory import CanBusFactory
from can_bus.i_can_handler import ICanHandler

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
        self.robot_online = True
        self.camera_factory = CameraFactory()
        self.can_bus_factory = CanBusFactory()
        self._cameras: Dict[str, ICameraHandler] = {}
        self.filter = ImageFilter()
        self.can_bus : ICanHandler = None

    def initialize_canbus(self):
        # hier moet canbus setup komen
        try:
            self.can_bus = self.can_bus_factory.create_online()
            print("create online canbus")
            self.robot_online = True
        except Exception as e:
            print(e)
            self.can_bus = self.can_bus_factory.create_offline()
            print("create offline canbus")
            self.robot_online = False

    async def get_camera(self, name: str):
        if name not in self._cameras:
            if self.robot_online:
                cam = self.camera_factory.add_camera_online(name)
                print(f"made cam {name}")
                await cam.start()
            else:
                cam = self.camera_factory.add_camera_offline()
                print(f"made cam {name}")
                await cam.start()
            self._cameras[name] = cam

        return self._cameras[name]

    async def stop(self):
        await self.camera_factory.stop_all()
