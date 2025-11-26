import asyncio
import cv2

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, NumericProperty
from kivy.event import EventDispatcher
from processing.image_processor import ImageProcessor
from processing.image_filter import ImageFilter

class FilterModel(EventDispatcher):
    frame_texture = ObjectProperty(None)
    filter_texture = ObjectProperty(None)

    def __init__(self):
        self.img_filter = ImageFilter()
        self.lower_hue = 0
        self.upper_hue = 180
        self.lower_sat = 0
        self.upper_sat = 180
        self.lower_val = 0
        self.upper_val = 180

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
        """Set filter"""
        setattr(self, property, value)



    async def process_stream(self, camera):
        await camera.start()
        while True:
            frame = await camera.get_frame()
            self.frame_texture = await ImageProcessor.get_processed_frame(frame)
            self.update_filter()
            self.filter_texture = await ImageProcessor.get_processed_frame(frame, self.img_filter)
            await asyncio.sleep(0.01)