import asyncio
import cv2

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
        """
        update ImageFilter with current values
        """
        self.img_filter.update_filter(
            self.lower_hue,
            self.upper_hue,
            self.lower_sat,
            self.upper_sat,
            self.lower_val,
            self.upper_val
        )

    def set_filter_property(self, property, value):
        """
        changes a property of the filter
        - property: property name witch to change value
        - value: new value for the property
        """
        setattr(self, property, value)

    def change_area(self, text):
        """
        change the area a contour needs to be, to be recognised as crop
        - text: square pixels of how big contours need to be, to be recognised
        """
        self.json_handler.update_property("detection_radius", text)

    def set_water(self, text):
        """
        change the water amount that wil be given to a crop
        - crop: nieuw amount of water that wil be given to each individual crop in ml
        """
        self.json_handler.update_property("water_amount", text)

    async def start_cameras(self):
        """
        start getting camera frames
        """
        camera = await self.setup.get_camera("oak2")
        print("start cameras")
        self.camera_task = asyncio.create_task(self.process_stream(camera))

    def stop_cameras(self):
        """
        stop getting caemra frames
        """
        self.camera_task.cancel()

    async def process_stream(self, camera):
        """
        updates to camera textures
        - one texture for camera feed
        - one texture for camera feed with overlaying current filter
        - camera: camera to both show and put filter over
        """
        while True:
            frame = await camera.get_frame()
            self.frame_texture = await ImageProcessor.get_processed_frame(frame)
            self.update_filter()
            self.filter_texture = await ImageProcessor.get_processed_frame(frame, self.img_filter)
            await asyncio.sleep(0.01)