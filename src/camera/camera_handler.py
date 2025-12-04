import asyncio
import cv2
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
        self.image_decoder = TurboJPEG()

    async def start(self):

        config = proto_from_json_file(self.service_config_path,EventServiceConfigList())
        for cfg in config.configs:
            if cfg.name == "camera":
                self.client = EventClient(cfg)
                print("client started")
                self.running = True

        rate = self.client.config.subscriptions[0].every_n
        self.frame_stream = self.client.subscribe(
            SubscribeRequest(
                uri={"path": f"{self.config_name}/{self.stream_name}"},
                every_n=rate
            ),
            decode=False
        )
        asyncio.create_task(self.reader())

    async def reader(self):
        async for event, payload in self.frame_stream:
            message = payload_to_protobuf(event, payload)
            self.latest_frame = self.image_decoder.decode(message.image_data)

    async def get_frame(self):
        if not self.client:
            raise RuntimeError("Client niet gestart")
        while self.latest_frame is None:
            await asyncio.sleep(0.001)
        return self.latest_frame

    async def stop(self):
        self.running = False
        if self.client:
            await self.client.close()
            self.client = None