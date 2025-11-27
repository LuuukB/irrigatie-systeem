import asyncio
import cv2

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

from processing.image_processor import ImageProcessor
from custom_pdo.can_message_structure import SetupPdo
from can_bus.i_can_handler import ICanHandler

class HomeModel(EventDispatcher):
    oak0_texture = ObjectProperty(None)
    oak2_texture = ObjectProperty(None)
    oak3_texture = ObjectProperty(None)

    def __init__(self, can_bus : ICanHandler):
        self.can_bus = can_bus

    async def process_stream(self, camera, property_name : str):
        while True:
            frame = await camera.get_frame()
            texture = await ImageProcessor.get_processed_frame(frame)
            setattr(self, f"{property_name}_texture", texture)
            await asyncio.sleep(0.01)

    def send_message(self):
        msg = SetupPdo(command=1, amount=200)
        self.can_bus.send_packet(packet = msg, cob_id = 0x301)