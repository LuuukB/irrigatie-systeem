import asyncio
import cv2

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

from processing.image_processor import ImageProcessor

class HomeModel(EventDispatcher):
    oak0_texture = ObjectProperty(None)
    oak2_texture = ObjectProperty(None)
    oak3_texture = ObjectProperty(None)

    def __init__(self):
        self.counter = 100

    async def process_stream(self, camera, property_name : str):
        while True:
            frame = await camera.get_frame()
            texture = await ImageProcessor.get_processed_frame(frame)
            setattr(self, f"{property_name}_texture", texture)
            await asyncio.sleep(0.01)