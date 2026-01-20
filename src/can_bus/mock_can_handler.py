import asyncio
from collections import defaultdict
from farm_ng.canbus.packet import Packet
from can_bus.i_can_handler import ICanHandler
from farm_ng.canbus.canbus_pb2 import Twist2d

class MockCanHandler(ICanHandler):

    def __init__(self):
        self.callbacks = {}
        self._running = False
        # internal queue to to dispatch "send" messages
        self._queue = asyncio.Queue()

    async def start(self):
        pass

    async def get_speed(self):
        await asyncio.sleep(0.01)
        return 0.2

    async def send_to_microcontroller(self,  message):
        print(f"send microcontroller message: {message}")