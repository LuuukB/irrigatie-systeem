import asyncio
import cv2
import json

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

from setup.setup import Setup
from file_communication.json_handler import JsonHandler
from processing.cv2_processor import Cv2Processor
from processing.image_processor import ImageProcessor
from processing.image_filter import ImageFilter


class FilterModel(EventDispatcher):
    frame_texture = ObjectProperty(None)
    filter_texture = ObjectProperty(None)

    def __init__(self):
        self.setup = Setup()
        self.processor = Cv2Processor()
        self.img_filter = self.setup.filter
        self.json_handler = JsonHandler()
        self.camera_task : asyncio.Task = None
        (
            self.upper_hue,
            self.lower_hue,
            self.upper_sat,
            self.lower_sat,
            self.upper_val,
            self.lower_val
        ) = self.json_handler.get_filter_values()

    def update_filter(self):

        self.img_filter.update_filter(
            self.lower_hue,
            self.upper_hue,
            self.lower_sat,
            self.upper_sat,
            self.lower_val,
            self.upper_val
        )

    def set_filter_property(self, property, value):
        """changes a property of the filter"""
        setattr(self, property, value)

    def change_area(self, text):
        self.json_handler.update_property("detection_radius", text)

    def set_water(self, text):
        self.json_handler.update_property("water_amount", text)

    async def start_cameras(self):
        camera = await self.setup.get_camera("oak2")
        print("start cameras")
        self.camera_task = asyncio.create_task(self.process_stream(camera))

    def stop_cameras(self):
        self.camera_task.cancel()

    async def process_stream(self, camera):
        print("start process")
        while True:
            frame = await camera.get_frame()
            self.frame_texture = await ImageProcessor.get_processed_frame(frame)
            self.update_filter()
            self.filter_texture = await ImageProcessor.get_processed_frame(frame, self.img_filter)
            await asyncio.sleep(0.01)