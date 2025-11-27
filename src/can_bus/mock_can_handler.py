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

    # ----------------------------
    # Callbacks registratie
    # ----------------------------
    def register_callback(self, cob_id, callback):
        """
        Registreer een callback functie voor een bepaalde COB-ID
        """
        self.callbacks[cob_id].append(callback)

    # ----------------------------
    # Verzenden
    # ----------------------------
    def send_packet(self, packet: Packet, cob_id: int):
        """
        Plaatst een Packet in de interne queue om later te dispatchen
        """
        print(f"Queuing Packet for COB_ID 0x{cob_id:X}: {packet.to_can_data()}")

        self._queue.put_nowait((cob_id, packet))

    # ----------------------------
    # Dispatch / receive
    # ----------------------------
    async def _dispatch(self, cob_id, packet: Packet):
        """
        Dispatch een packet naar callbacks
        """
        if cob_id in self.callbacks:
            for cb in self.callbacks[cob_id]:
                cb(packet)

    async def _receive_task(self):
        """
        Async loop die berichten uit de queue haalt en dispatcht
        """
        while self._running:
            cob_id, packet = await self._queue.get()
            await self._dispatch(cob_id, packet)
            await asyncio.sleep(0)

    # ----------------------------
    # Run / stop
    # ----------------------------
    async def run(self):
        """
        Start de send/receive loop
        """
        self._running = True
        asyncio.create_task(self._receive_task())

    def stop(self):
        """
        Stop de dispatch loop
        """
        self._running = False
