import asyncio
import can
from farm_ng.canbus.packet import Packet
from can_bus.i_can_handler import ICanHandler

class AsyncCanHandler(ICanHandler):
    def __init__(self, channel="can0", bustype="socketcan", bitrate=250_000):

        self.bus = can.Bus(channel=channel, bustype=bustype, bitrate=bitrate)
        self._running = False
        self.callbacks = {}

        # receiving via notifier
        #self.reader = can.AsyncBufferedReader()
        #self.notifier = can.Notifier(
        #    self.bus,
        #    [self.reader],
        #    timeout=0.01
        #)


    def register_callback(self, cob_id, callback):
        """"
        registers a callback for a specifick COB-ID
        """
        if cob_id not in self.callbacks:
            self.callbacks[cob_id] = []
        self.callbacks[cob_id].append(callback)


    def send_packet(self, packet: Packet, cob_id: int):
        """
        sends a packet to a COB-ID
        """
        print("can on queue")
        msg = can.Message(
            arbitration_id=cob_id,
            data=packet.to_can_data(),
            is_extended_id=False
        )
        try:
            self.bus.send(msg)
            print(f"CAN Sent: COB_ID=0x{msg.arbitration_id:X}, data={msg.data}")
        except Exception as e:
            print(f"CAN Send error: {e}")

    async def _dispatch(self, msg):
        """"
        dispatches a message to the corresponding callbacks
        """
        cob_id = msg.arbitration_id

        if cob_id in self.callbacks:
            for cb in self.callbacks[cob_id]:
                cb(msg)


    async def _receive_task(self):
        """"
        constantly listens for incoming messages
        """
        while self._running:
            msg = await self.reader.get_message()
            if msg:
                await self._dispatch(msg)
            await asyncio.sleep(0.001)

    async def run(self):
        """
        Start de send/receive loop
        """
        self._running = True
        asyncio.create_task(self._send_task())


    def stop(self):
        self._running = False
        #self.notifier.stop()
        self.bus.shutdown()