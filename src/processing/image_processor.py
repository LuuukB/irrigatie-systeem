import cv2
from processing.image_filter import ImageFilter
from kivy.graphics.texture import Texture

class ImageProcessor:
    @staticmethod
    async def get_processed_frame(frame, img_filter: ImageFilter = None):
        """turns the given frame into a texture usable for kivy image"""
        if img_filter:
            frame = img_filter.apply_filter(frame)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        texture = Texture.create(
            size=(
                frame_rgb.shape[1],
                frame_rgb.shape[0]),
            colorfmt='rgb')

        texture.flip_vertical()

        texture.blit_buffer(
            frame_rgb.tobytes(),
            colorfmt='rgb',
            bufferfmt='ubyte',
            mipmap_generation=False)

        return texture