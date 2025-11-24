import os
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from vieuw_models.home_model import HomeModel



# Laad het KV-bestand automatisch vanuit dezelfde map
Builder.load_file(os.path.join(os.path.dirname(__file__), "res/home_screen.kv"))

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm = HomeModel()

    def increase_counter(self):
        self.vm.increase()
        self.ids.counter_label.text = f"Teller: {self.vm.counter}"