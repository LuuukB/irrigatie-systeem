import cv2
import numpy as np
import logging
logger = logging.getLogger(__name__)

from processing.image_filter import ImageFilter
from file_communication.json_handler import JsonHandler

class Cv2Processor:
    def __init__(self):
        self.json_handler = JsonHandler()

    def get_contours(self, frame, img_filter: ImageFilter = None):
        """
        takes the given image and returns a list of spotted contours
        - frame: frame to process
        - img_filter: filter to apply to frame
        """
        if img_filter:
            frame = img_filter.apply_filter(frame)
        # logger.debug("aplied filter")
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        ret, binary = cv2.threshold(frame_gray, 1, 150, cv2.THRESH_BINARY)

        kernel = np.ones((15, 15), np.uint8)

        morphopen = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        morphclose = cv2.morphologyEx(morphopen, cv2.MORPH_OPEN, kernel)


        contours, hierarchy = cv2.findContours(
            morphclose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        correct_contours = []
        for c in contours:
            if cv2.contourArea(c) > self.json_handler.get_detection_radius():
                correct_contours.append(c)
        return correct_contours

    def draw_contours(self, contours, frame):
        """
        draw's given contours over the given frame
        - contours: list of contours that needs to be drawn
        - frame: frame to draw contours on
        """
        cv2.drawContours(image=frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2,
                lineType=cv2.LINE_AA)
        return frame