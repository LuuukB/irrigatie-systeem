import asyncio
from collections import defaultdict
from farm_ng.canbus.packet import Packet
from can_bus.i_can_handler import ICanHandler
from farm_ng.canbus.canbus_pb2 import Twist2d

class MockCanHandler(ICanHandler):

    def __init__(self):
        self.callbacks = {}
        self._running = False
        # Interne queue om "verzonden" berichten te dispatchen
        self._queue = asyncio.Queue()

    async def start(self):
        pass

    def register_callback(self, cob_id, callback):
        """
        register a callback to a COB-ID
        """
        self.callbacks[cob_id].append(callback)

    async def send_twist(self, message : Twist2d):
        print(f"send twist : {message}")

    async def set_speed(self, linear_velocity_x, angular_velocity):
        print(f"set speed : {linear_velocity_x, angular_velocity}")
        pass

    async def get_speed(self):
        await asyncio.sleep(0.01)
        return 0.2

    async def send_to_microcontroller(self,  message):
        print(f"send microcontroller message: {message}")
        pass