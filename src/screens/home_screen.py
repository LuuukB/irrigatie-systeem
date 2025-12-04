import os
import asyncio

os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.home_model import HomeModel

from factory.camera_factory import CameraFactory
from setup.setup import Setup
from widgets.camera_widget.camera_widget import CameraWidget


Builder.load_file(os.path.join(os.path.dirname(__file__), "res/home_screen.kv"))

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup = Setup()
        self.vm = HomeModel(self.setup.can_bus)
        self.tasks: List[asyncio.Task] = [asyncio.create_task(self.start_cameras())]
        self.start_task = False
        self.vm.bind(oak0_texture=self.update_oak0)
        self.vm.bind(oak2_texture=self.update_oak2)
        self.vm.bind(oak3_texture=self.update_oak3)


    async def start_cameras(self):
        pass
        #oak0 = await self.setup.get_camera("oak0")
        oak2 = await self.setup.get_camera("oak2")
        #oak3 = await self.setup.get_camera("oak3")
        #self.tasks.append(asyncio.create_task(self.vm.process_stream(oak0, "oak0")))
        self.tasks.append(asyncio.create_task(self.vm.process_stream(oak2, "oak2")))
        #self.tasks.append(asyncio.create_task(self.vm.process_stream(oak3, "oak3")))

    def start_stop(self):
        self.start_task = not self.start_task
        print(self.start_task)
        if self.start_task:
            print("go")
            self.vm.send_message()
            self.ids.start_stop_btn.text = "stop"
        else:
            print("stop")
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
        for task in self.tasks:
            task.cancel()
