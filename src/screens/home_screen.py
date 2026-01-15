import os
import asyncio
import threading

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
        self.camera_task: asyncio.Task = None
        self.task :asyncio.Task = None
        self.thread = None
        self.start_task = False
        self.vm.bind(oak0_texture=self.update_oak0)
        self.vm.bind(oak2_texture=self.update_oak2)
        self.vm.bind(oak3_texture=self.update_oak3)

    async def start_cameras(self):
        await self.vm.start_cameras()

    def stop_cameras(self):
        self.vm.stop_cameras()

    def on_enter(self):
        print("enter")
        self.camera_task = asyncio.create_task(self.start_cameras())

    def on_leave(self):
        print("leave")
        self.vm.stop_cameras()

    def start_stop(self):
        self.start_task = not self.start_task
        print(self.start_task)
        if self.start_task:
            print("start")
            self.vm.stop_thread = False
            self.thread = threading.Thread(target=lambda: asyncio.run(self.vm.start()), daemon=True)
            self.thread.start()

            self.ids.start_stop_btn.text = "stop"
        else:
            print("stop")
            self.vm.stop_thread = True
            self.ids.start_stop_btn.text = "start"

    def update_oak0(self,instance, value):
        if value:
            self.ids.oak0.texture = value

    def update_oak2(self,instance, value):
        if value:
            self.ids.oak2.texture = value

    def update_oak3(self,instance, value):
        if value:
            self.ids.oak3.texture = value

    def stop(self):
        if self.camera_task is not None:
            self.camera_task.cancel()
        if self.task is not None:
            self.task.cancel()
