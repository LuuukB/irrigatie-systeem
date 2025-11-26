import os
import asyncio
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.home_model import HomeModel

from factory.camera_factory import CameraFactory
from widgets.camera_widget.camera_widget import CameraWidget


Builder.load_file(os.path.join(os.path.dirname(__file__), "res/home_screen.kv"))

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm = HomeModel()
        self.task : asyncio.Task = None
        self.start_task = False
    
    
    def start_stop(self):
        self.start_task = not self.start_task
        print(self.start_task)
        if self.start_task:
            print("go")
            self.ids.start_stop_btn.text = "stop"
        else:
            print("stop")
            self.ids.start_stop_btn.text = "start"
