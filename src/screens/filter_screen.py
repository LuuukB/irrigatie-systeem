import os
import asyncio
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from models.filter_model import FilterModel
from kivy.properties import NumericProperty
from file_communication.json_handler import JsonHandler

Builder.load_file(os.path.join(os.path.dirname(__file__), "view/filter_screen.kv"))

class FilterScreen(Screen):
    upper_hue = NumericProperty(0)
    lower_hue = NumericProperty(0)
    upper_sat = NumericProperty(0)
    lower_sat = NumericProperty(0)
    upper_val = NumericProperty(0)
    lower_val = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = FilterModel()
        self.json_handler = JsonHandler()
        self.model.bind(frame_texture = self.update_oak0)
        self.model.bind(filter_texture = self.update_oak1)
        self.camera_task: asyncio.Task = None
        (
            self.upper_hue,
            self.lower_hue,
            self.upper_sat,
            self.lower_sat,
            self.upper_val,
            self.lower_val
        ) = self.json_handler.get_filter_values()

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

    def update_oak0(self,instance, value):
        if value:
            self.ids.oak0.texture = value

    def update_oak1(self,instance, value):
        if value:
            self.ids.oak1.texture = value

    def on_slider_change(self, slider):
        """
        updates slider value, and tells model to update filter
        - slider: slider instance that calls this function
        """
        property = slider.slider_id
        value = round(slider.value)
        setattr(self, property, value)
        self.model.set_filter_property(property, value)

    def set_detection_radius(self, text):
        self.model.change_area(int(text))

    def set_amount_of_water(self, text):
        self.model.set_water(int(text))

    def stop(self):
        if self.camera_task is not None:
            self.camera_task.cancel()