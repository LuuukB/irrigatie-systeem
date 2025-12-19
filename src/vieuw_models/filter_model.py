import asyncio
import cv2
import json

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

from setup.setup import Setup
from processing.image_processor import ImageProcessor
from processing.image_filter import ImageFilter
from processing.point_handler import PointHandler

class FilterModel(EventDispatcher):
    frame_texture = ObjectProperty(None)
    filter_texture = ObjectProperty(None)
    with open("filter_values.json") as json_file:
        data = json.load(json_file)

    def __init__(self):
        self.setup = Setup()
        self.img_filter = self.setup.filter
        self.camera_task : asyncio.Task = None
        self.lower_hue = self.data.get('lower_hue')
        self.upper_hue = self.data.get('upper_hue')
        self.lower_sat = self.data.get('lower_sat')
        self.upper_sat = self.data.get('upper_sat')
        self.lower_val = self.data.get('lower_val')
        self.upper_val = self.data.get('upper_val')

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
        setattr(self, property, value)

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