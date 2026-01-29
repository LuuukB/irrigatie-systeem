import asyncio
import cv2
import logging
logger = logging.getLogger(__name__)

from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

from processing.image_processor import ImageProcessor
from processing.tracker import Tracker
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
        self.processor = Cv2Processor()
        self.oak2_tracker = Tracker()
        self.oak3_tracker = Tracker()
        self.image_filter = self.setup.filter
        self.can_bus = self.setup.can_bus
        asyncio.create_task(self.can_bus.start())
        self.tasks : List[asyncio.Task] = []
        self.stop_thread = False
        self.oak2 = None
        self.oak3 = None


    async def start_cameras(self):
        """
        starts updating textures with frames form the camera's
        """
        oak0 = await self.setup.get_camera("oak0")
        self.oak2 = await self.setup.get_camera("oak2")
        self.oak3 = await self.setup.get_camera("oak3")
        self.tasks.append( asyncio.create_task(self.process_stream(oak0, "oak0")))
        self.tasks.append(asyncio.create_task(self.process_stream(self.oak2, "oak2")))
        self.tasks.append(asyncio.create_task(self.process_stream(self.oak3, "oak3")))

    async def process_stream(self, camera, property_name : str):
        """
        gets frame from camera, turns it into a texture end updates the corresponding texture
        - camera: camera to get frame from
        - property_name: name of the property to change the texture from
        """
        while True:
            frame = await camera.get_frame()
            texture = await ImageProcessor.get_processed_frame(frame)
            setattr(self, f"{property_name}_texture", texture)
            await asyncio.sleep(0.01)

    def stop_cameras(self):
        """
        stops updating textures for all cameras
        """
        for task in self.tasks:
            task.cancel()

    async def start(self):
        """
        starts a task to check distances of detected crops
        and starts algorithm for both oak2 and oak3
        """
        asyncio.create_task(self.point_handler.check_distances())

        logger.info("start looking for crops")
        while True and not self.stop_thread:

            await self.analyze_camera_frame(self.oak2, 0, self.oak2_tracker)
            await self.analyze_camera_frame(self.oak3, 1, self.oak3_tracker)

            await asyncio.sleep(0.1)

    async def analyze_camera_frame(self, camera, camera_number, tracker):
        """
        checks camera for contours finds out if they are crops,
        then puts the crops to be added to setup's
        - camera: camera to get frame from
        - camera_number: camera from left to right
        - tracker: tracker that keeps track of all discovered contours for just this camera
        """
        tracker = tracker
        frame = await camera.get_frame()

        contours = self.processor.get_contours(frame, self.image_filter)

        centroids = []
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append((c, cx, cy))

        #adds contours to be tracked and checks for enough validations to know contour is a crop
        #than adds it to be handled by point handler
        if len(centroids) > 0:
            try:
                draw_midpoints = tracker.track_contours(centroids)
                for iterations, c, cx, cy in draw_midpoints:
                    logger.debug(f"found crop with {iterations} itterations")
                    if iterations > 5:
                        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                    elif iterations == 5:
                        self.point_handler.handle_point(cx, cy, camera_number)
            except Exception as e:
                print(e)
