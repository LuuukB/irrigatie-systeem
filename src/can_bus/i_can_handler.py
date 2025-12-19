from abc import ABC, abstractmethod
from farm_ng.canbus.packet import Packet

class ICanHandler(ABC):

    @abstractmethod
    def register_callback(self, cob_id, callback):
        """Callback for cob_id"""

    @abstractmethod
    def get_speed(self):
        """"get speed"""

    @abstractmethod
    def send_packet(self, packet: Packet, cob_id: int):
        """send packet to cob_id"""

    @abstractmethod
    async def _dispatch(self, msg):
        """dispatches incoming message to corresponding cob_id"""

    @abstractmethod
    async def _receive_task(self):
        """puts recieved packets into queue"""

    @abstractmethod
    async def run(self):
        """Start receive loop"""

    @abstractmethod
    def stop(self):
        """Stop receive loop"""
