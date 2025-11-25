import os
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.drive_model import DriveModel


Builder.load_file(os.path.join(os.path.dirname(__file__), "res/drive_screen.kv"))

class DriveScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm = DriveModel()
        print("hello")

    def on_enter(self):
        print("drive start")
    def on_leave(self):
        print("drive stop")

    def increase_counter(self):
        self.vm.increase()
        self.ids.counter_label.text = f"Teller: {self.vm.counter}"