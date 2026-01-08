import asyncio
import cv2
import logging
logger = logging.getLogger(__name__)

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

from processing.image_processor import ImageProcessor
from processing.cv2_processor import Cv2Processor
from custom_pdo.can_message_structure import SetupPdo
from can_bus.i_can_handler import ICanHandler
from processing.image_filter import ImageFilter
from setup.setup import Setup
from processing.point_handler import PointHandler

class HomeModel(EventDispatcher):
    oak0_texture = ObjectProperty(None)
    oak2_texture = ObjectProperty(None)
    oak3_texture = ObjectProperty(None)

    def __init__(self):
        self.setup = Setup()
        self.point_handler = PointHandler()
        self.cv2_processor = Cv2Processor(self.point_handler)
        self.image_filter = self.setup.filter
        self.can_bus = self.setup.can_bus
        self.tasks : List[asyncio.Task] = []
        self.oak2 = None
        self.oak3 = None


    async def start_cameras(self):
        oak0 = await self.setup.get_camera("oak0")
        self.oak2 = await self.setup.get_camera("oak2")
        self.oak3 = await self.setup.get_camera("oak3")
        self.tasks.append( asyncio.create_task(self.process_stream(oak0, "oak0")))
        self.tasks.append(asyncio.create_task(self.process_stream(self.oak2, "oak2")))
        self.tasks.append(asyncio.create_task(self.process_stream(self.oak3, "oak3")))

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
        asyncio.create_task(self.point_handler.check_distances())
        logger.info("start looking for crops")
        while True:
            oak2_frame = await self.oak2.get_frame()
            oak3_frame = await self.oak3.get_frame()
            self.cv2_processor.get_contours(oak2_frame, self.image_filter)
            self.cv2_processor.get_contours(oak3_frame, self.image_filter)
            await asyncio.sleep(0.1)