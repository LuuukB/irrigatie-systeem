from abc import ABC, abstractmethod
from farm_ng.canbus.canbus_pb2 import Twist2d

class ICanHandler(ABC):
    @abstractmethod
    async def start(self):
        """start listening to speed and start send task"""

    @abstractmethod
    def get_speed(self):
        """Return current speed of amiga in m/s"""

    @abstractmethod
    async def send_to_microcontroller(self, message):
        """sends a RawCanbusMessage to canbus"""
