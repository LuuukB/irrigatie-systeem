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
        #asyncio.create_task(self.stream_cameras())

    #def on_leave(self):
    #    self.task.cancel()

    def increase_counter(self):
        self.vm.increase()
        self.ids.counter_label.text = f"Teller: {self.vm.counter}"

    async def stream_cameras(self):

        camera_factory = CameraFactory()
        camera_widget: CameraWidget = self.ids["oak0"]
        camera_factory.add_camera_offline("video")
        await camera_factory.start_all()
        print("start")
        self.task = asyncio.create_task(
            camera_widget.stream_camera(camera_factory.get_camera("video"))
        )