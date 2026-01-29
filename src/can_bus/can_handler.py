import asyncio
import logging
logger = logging.getLogger(__name__)

from pathlib import Path
from threading import Lock
from can_bus.i_can_handler import ICanHandler
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.canbus.canbus_pb2 import RawCanbusMessage
from farm_ng.core.events_file_reader import payload_to_protobuf
from farm_ng.canbus.packet import AmigaTpdo1
from farm_ng.core.uri_pb2 import Uri
from farm_ng.canbus.canbus_pb2 import Twist2d
from farm_ng.core.events_file_reader import proto_from_json_file

class CanHandler(ICanHandler):
    def __init__(self):
        service_config_path = Path() / 'service_config.json'
        config = proto_from_json_file(service_config_path, EventServiceConfigList())
        self.max_speed = 0.1
        self.max_angular_rate = 0.1
        self.speed = 0
        self.lock = Lock()
        self.send_queue = asyncio.Queue()
        print("create canbus")

        for cfg in config.configs:
            if cfg.name == "canbus":
                self.client = EventClient(cfg)
                print("canbus started")
                self.callbacks = {}
                self._listening = False

    async def start(self):
        """
        starts 2 tasks
        - one for listening to info from the amiga to get the current speed
        - one to send messages over the Canbus
        """
        if not self._listening:
            asyncio.create_task(self._speed_listener())
            asyncio.create_task(self._send_messages())
            self._listening = True

    async def _speed_listener(self):
        """
        listens to the amiga to get the current speed
        """
        logger.debug("start looking for speed")
        async for event, payload in self.client.subscribe(
                SubscribeRequest(uri = Uri(path= "/state"), every_n = 5),
                decode=False,
        ):
            message = payload_to_protobuf(event, payload)

            tpdo1 = AmigaTpdo1.from_proto(message.amiga_tpdo1)
            measured_speed = tpdo1.meas_speed
            with self.lock:
                self.speed = measured_speed # m/s

    async def get_speed(self):
        """
        returns the current speed
        """
        while True:
            with self.lock:
                if self.speed is not None:
                    return self.speed
            await asyncio.sleep(0.001)

    async def send_to_microcontroller(self, message: RawCanbusMessage):
        """
        sends message to microcontroller
        - message: RawCanbusMessage containing at least location and encoded message
        """
        logger.info(f"send Queue {message}")
        await self.send_queue.put(message)


    async def _send_messages(self):
        """
        waits for a message to be put in the que to send this message
        """
        while True:
            msg = await self.send_queue.get()  # wacht tot er iets is
            logger.debug("got message")
            try:
                await self.client.request_reply("/can_message", msg)
                logger.info(f"CAN message send: {msg}")
            except Exception as e:
                logger.info(f"error with sending CAN message: {e}")
            finally:
                self.send_queue.task_done()