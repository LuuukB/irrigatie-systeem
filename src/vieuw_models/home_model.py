import asyncio
import cv2

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

from processing.image_processor import ImageProcessor
from processing.cv2_processor import Cv2Processor
from custom_pdo.can_message_structure import SetupPdo
from can_bus.i_can_handler import ICanHandler
from processing.image_filter import ImageFilter
from setup.setup import Setup

class HomeModel(EventDispatcher):
    oak0_texture = ObjectProperty(None)
    oak2_texture = ObjectProperty(None)
    oak3_texture = ObjectProperty(None)

    def __init__(self):
        self.setup = Setup()
        self.cv2_processor = Cv2Processor()
        self.image_filter = self.setup.filter
        self.can_bus = self.setup.can_bus
        self.tasks : List[asyncio.Task] = []
        self.oak0 = None

    async def start_cameras(self):
        self.oak0 = await self.setup.get_camera("oak0")
        oak2 = await self.setup.get_camera("oak2")
        oak3 = await self.setup.get_camera("oak3")
        self.tasks.append( asyncio.create_task(self.process_stream(self.oak0, "oak0")))
        self.tasks.append(asyncio.create_task(self.process_stream(oak2, "oak2")))
        self.tasks.append(asyncio.create_task(self.process_stream(oak3, "oak3")))

    async def process_stream(self, camera, property_name : str):
        while True:
            frame = await camera.get_frame()
            texture = await ImageProcessor.get_processed_frame(frame)
            setattr(self, f"{property_name}_texture", texture)
            await asyncio.sleep(0.01)

    def send_message(self):
        msg = SetupPdo(command=1, amount=200)
        self.can_bus.send_packet(packet = msg, cob_id = 0x301)

    def stop_cameras(self):
        for task in self.tasks:
            task.cancel()

    async def start(self):
        while True:
            frame = await self.oak0.get_frame()
            self.cv2_processor.get_contours(frame, self.image_filter)
            await asyncio.sleep(0.01)