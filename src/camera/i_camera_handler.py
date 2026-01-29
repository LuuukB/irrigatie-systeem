from abc import ABC, abstractmethod

class ICameraHandler(ABC):
    @abstractmethod
    def start(self):
        """starts the camera"""

    @abstractmethod
    def get_frame(self):
        """returns latest frame"""

    @abstractmethod
    def stop(self):
        """stops the camera"""