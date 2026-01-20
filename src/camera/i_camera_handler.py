from abc import ABC, abstractmethod

class ICameraHandler(ABC):
    @abstractmethod
    def start(self):
        """starts the camera"""
        pass
    @abstractmethod
    def get_frame(self):
        """returns latest frame"""
        pass
    @abstractmethod
    def stop(self):
        """stops the camera"""
        pass