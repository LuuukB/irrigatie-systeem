import os
import asyncio
import cv2

from camera.i_camera_handler import ICameraHandler

# Must come before kivy imports
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.input.providers.mouse import MouseMotionEvent  # noqa: E402
from kivy.lang.builder import Builder  # noqa: E402
from kivy.uix.widget import Widget  # noqa: E402

class CameraWidget(Widget ):
    def __init__(self, **kwargs):
        super(CameraWidget,self ).__init__(**kwargs)
        self.texture : Texture = None
        self.camera : ICameraHandler = None
        self.running : bool = True

        Builder.load_file(os.path.join(os.path.dirname(__file__), "camera_widget.kv"))

    async def start_stream(self, camera : ICameraHandler):
        """
        starts a loop that gets frames from the given camera,
        turns them into a texture and fils the Image with the texture
        """
        self.camera = camera

        while self.running:

            frame = await self.camera.get_frame()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.texture is None:
                self.texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]), icolorfmt="rgb"
                )
                self.texture.flip_vertical()

            self.texture.blit_buffer(
                bytes(frame.data),
               colorfmt="rgb",
               bufferfmt="ubyte",
               mipmap_generation=False,
            )

            self.root.ids.image.texture = self.texture
            await asyncio.sleep(0.01)

    async def stop_stream(self):
        """
        stops the camera and clears the texture
        """
        self.running = False
        self.texture = None
