import asyncio
from collections import defaultdict
from farm_ng.canbus.packet import Packet
from can_bus.i_can_handler import ICanHandler

class MockCanHandler(ICanHandler):

    def __init__(self):
        self.callbacks = {}
        self._running = False
        # Interne queue om "verzonden" berichten te dispatchen
        self._queue = asyncio.Queue()

    def register_callback(self, cob_id, callback):
        """
        register a callback to a COB-ID
        """
        self.callbacks[cob_id].append(callback)


    def send_packet(self, packet: Packet, cob_id: int):
        """
        places the package in a queue that wil be sent to itself, this way i can check te messages
        """
        print(f"Queuing Packet for COB_ID 0x{cob_id:X}: {packet.to_can_data()}")

        self._queue.put_nowait((cob_id, packet))


    async def _dispatch(self, cob_id, packet: Packet):
        """
        Dispatches a packet to the corresponding callback
        """
        if cob_id in self.callbacks:
            for cb in self.callbacks[cob_id]:
                cb(packet)

    async def _receive_task(self):
        """
        Async loop that waits for message to be send,
         then returns it as if it was send to this application
        """
        while self._running:
            cob_id, packet = await self._queue.get()
            await self._dispatch(cob_id, packet)
            await asyncio.sleep(0)

    async def run(self):
        """
        Start the receive loop
        """
        self._running = True
        asyncio.create_task(self._receive_task())

    def stop(self):
        """
        Stops the recieve loop
        """
        self._running = False
