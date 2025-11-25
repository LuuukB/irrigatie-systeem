import os
import asyncio
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.filter_model import FilterModel
from kivy.properties import NumericProperty
from factory.camera_factory import CameraFactory
from widgets.camera_widget.camera_widget import CameraWidget


Builder.load_file(os.path.join(os.path.dirname(__file__), "res/filter_screen.kv"))

class FilterScreen(Screen):
    upper_hue = NumericProperty(0)
    lower_hue = NumericProperty(0)
    upper_sat = NumericProperty(0)
    lower_sat = NumericProperty(0)
    upper_val = NumericProperty(0)
    lower_val = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm = FilterModel()
        self.vm.bind(frame_texture = self.update_oak0)
        self.vm.bind(filter_texture = self.update_oak1)
        self.camera_factory = CameraFactory()
        self.camera_factory.add_camera_offline("oak0")
        asyncio.create_task(self.vm.process_stream(self.camera_factory.get_camera("oak0")))

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
