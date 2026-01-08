import asyncio
import cv2
import time

from threading import Lock
from pathlib import Path
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.core.events_file_reader import payload_to_protobuf
from farm_ng.core.events_file_reader import proto_from_json_file
from camera.i_camera_handler import ICameraHandler
from turbojpeg import TurboJPEG


class CameraHandler(ICameraHandler):
    def __init__(self, name : str, stream_name: str = "rgb"):

        self.service_config_path = Path() / "service_config.json"
        if not self.service_config_path.exists():
            raise FileNotFoundError("Service config not found!")
        self.config_name = name
        self.stream_name = stream_name
        self.client = None
        self.running = False
        self.frame_stream = None
        self.latest_frame = None
        self.lock = Lock()
        self.image_decoder = TurboJPEG()

    async def start(self):

        config = proto_from_json_file(self.service_config_path,EventServiceConfigList())
        for cfg in config.configs:
            if cfg.name == "camera":
                self.client = EventClient(cfg)
                print("client started")
                self.running = True
        for sub in self.client.config.subscriptions:
            print("Path:", sub.uri.path, "Query:", sub.uri.query)

        for sub in self.client.config.subscriptions:
            if f"service_name={self.config_name}" in sub.uri.query:
                self.frame_stream = self.client.subscribe(sub, decode=False)
                asyncio.create_task(self.reader())

    async def reader(self):
        async for event, payload in self.frame_stream:
            message = payload_to_protobuf(event, payload)
            frame = self.image_decoder.decode(message.image_data)
            with self.lock:
                self.latest_frame = frame

    async def get_frame(self):
        if not self.client:
            raise RuntimeError("Client niet gestart")
        while True:
            with self.lock:
                if self.latest_frame is not None:
                    return self.latest_frame
            time.sleep(0.001)

    async def stop(self):
        self.running = False
        if self.client:
            await self.client.close()
            self.client = None