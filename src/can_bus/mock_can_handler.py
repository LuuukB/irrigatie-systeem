import asyncio
from can_bus.i_can_handler import ICanHandler

class MockCanHandler(ICanHandler):

    def __init__(self):
        # internal queue to to dispatch "send" messages
        self._queue = asyncio.Queue()

    async def start(self):
        pass

    async def get_speed(self):
        await asyncio.sleep(0.01)
        return 0.2

    async def send_to_microcontroller(self,  message):
        print(f"send microcontroller message: {message}")