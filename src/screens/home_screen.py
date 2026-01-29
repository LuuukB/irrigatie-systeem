import os
import asyncio
import threading

os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from models.home_model import HomeModel
from factory.camera_factory import CameraFactory

Builder.load_file(os.path.join(os.path.dirname(__file__), "view/home_screen.kv"))

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = HomeModel()
        self.camera_task: asyncio.Task = None
        self.task :asyncio.Task = None
        self.thread = None
        self.start_task = False
        self.model.bind(oak0_texture=self.update_oak0)
        self.model.bind(oak2_texture=self.update_oak2)
        self.model.bind(oak3_texture=self.update_oak3)

    def on_enter(self):
        """
        start updating frames when entering this page
        """
        self.camera_task = asyncio.create_task(self.model.start_cameras())

    def on_leave(self):
        """
        stop updating frames when leaving this page
        """
        self.model.stop_cameras()

    def start_stop(self):
        """
        checks if algorithm should start or stop and acts accordingly
        """
        self.start_task = not self.start_task
        print(self.start_task)
        if self.start_task:
            #if start, start thread and let model know to start
            self.model.stop_thread = False
            self.thread = threading.Thread(target=lambda: asyncio.run(self.model.start()), daemon=True)
            self.thread.start()

            self.ids.start_stop_btn.text = "stop"
        else:
            #if stop, stop thread and tell model to stop
            self.model.stop_thread = True
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
        """stops all"""
        if self.camera_task is not None:
            self.camera_task.cancel()
        if self.task is not None:
            self.task.cancel()

        self.model.stop_thread = True
