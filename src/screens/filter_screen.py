import os
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.filter_model import FilterModel

# Laad het KV-bestand automatisch vanuit dezelfde map
Builder.load_file(os.path.join(os.path.dirname(__file__), "res/filter_screen.kv"))

class FilterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm = FilterModel()

    def increase_counter(self):
        self.vm.increase()
        self.ids.counter_label.text = f"Teller: {self.vm.counter}"