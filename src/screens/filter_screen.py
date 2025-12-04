import os
import asyncio
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.filter_model import FilterModel
from kivy.properties import NumericProperty
from setup.setup import Setup
from widgets.camera_widget.camera_widget import CameraWidget


Builder.load_file(os.path.join(os.path.dirname(__file__), "res/filter_screen.kv"))

class FilterScreen(Screen):
    upper_hue = NumericProperty(180)
    lower_hue = NumericProperty(0)
    upper_sat = NumericProperty(180)
    lower_sat = NumericProperty(0)
    upper_val = NumericProperty(180)
    lower_val = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm = FilterModel()
        self.vm.bind(frame_texture = self.update_oak0)
        self.vm.bind(filter_texture = self.update_oak1)
        self.setup = Setup()
        #self.tasks: List[asyncio.Task] = [asyncio.create_task(self.start_cameras())]

    async def start_cameras(self):
        camera = await self.setup.get_camera("oak2")
        self.tasks.append(asyncio.create_task(self.vm.process_stream(camera)))

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
       for task in self.tasks:
           task.cancel()
