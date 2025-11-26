import os
import asyncio
import cv2

from camera.i_camera_handler import ICameraHandler

# Must come before kivy imports
os.environ["KIVY_NO_ARGS"] = "1"
  # noqa: E402
from kivy.lang.builder import Builder  # noqa: E402
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture # noqa: E402
from kivy.properties import ObjectProperty

Builder.load_file(os.path.join(os.path.dirname(__file__), "camera_widget.kv"))

class CameraWidget(Widget ):
    texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CameraWidget,self ).__init__(**kwargs)
        self.camera = None
        self.camera : ICameraHandler = None
        self.running : bool = True



    async def stream_camera(self, camera : ICameraHandler):
        """
        starts a loop that gets frames from the given camera,
        turns them into a texture and fils the Image with the texture
        """
        self.camera = camera

        while self.running:

            frame = await self.camera.get_frame()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Texture.create(
               size=(frame.shape[1], frame.shape[0]), icolorfmt="rgb"
            )
            img.flip_vertical()

            img.blit_buffer(
                bytes(frame.data),
               colorfmt="rgb",
               bufferfmt="ubyte",
               mipmap_generation=False,
            )
            print(img)
            self.texture = img

            await asyncio.sleep(0.01)

    async def stop_stream(self):
        """
        stops the camera and clears the texture
        """
        self.running = False
        self.texture = None

    def on_texture(self, instance, value):
        if value:
            self.ids.image.texture = value