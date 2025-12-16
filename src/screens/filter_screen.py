import os
import asyncio
import json
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.filter_model import FilterModel
from kivy.properties import NumericProperty

from widgets.camera_widget.camera_widget import CameraWidget


Builder.load_file(os.path.join(os.path.dirname(__file__), "res/filter_screen.kv"))
with open ("filter_values.json") as json_file:
    data = json.load(json_file)

class FilterScreen(Screen):
    upper_hue = NumericProperty(data.get("upper_hue"))
    lower_hue = NumericProperty(data.get("lower_hue"))
    upper_sat = NumericProperty(data.get("upper_sat"))
    lower_sat = NumericProperty(data.get("lower_sat"))
    upper_val = NumericProperty(data.get("upper_val"))
    lower_val = NumericProperty(data.get("lower_val"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm = FilterModel()
        self.vm.bind(frame_texture = self.update_oak0)
        self.vm.bind(filter_texture = self.update_oak1)
        self.camera_task: asyncio.Task = None

    def on_enter(self):
        print("enter")
        self.camera_task = asyncio.create_task(self.vm.start_cameras())

    def on_leave(self):
        print("leave")
        self.vm.stop_cameras()

    async def start_cameras(self):
        self.vm.start_cameras()

    def stop_cameras(self):
        self.vm.stop_cameras()

    def update_oak0(self,instance, value):
        if value:
            self.ids.oak0.texture = value

    def update_oak1(self,instance, value):
        if value:
            self.ids.oak1.texture = value

    def on_slider_change(self, slider):
        property = slider.slider_id
        value = round(slider.value)
        setattr(self, property, value)
        self.vm.set_filter_property(property, value)

    def stop(self):
        if self.camera_task is not None:
            self.camera_task.cancel()

