import cv2
import numpy as np
import logging
logger = logging.getLogger(__name__)

from processing.image_filter import ImageFilter
from processing.tracker import Tracker
from processing.point_handler import PointHandler
from file_communication.json_handler import JsonHandler

class Cv2Processor:
    def __init__(self, point_handler=None):
        self.tracker = Tracker()
        self.point_handler = point_handler
        self.json_handler = JsonHandler()

    def onnodig(self, frame, camera_number, img_filter: ImageFilter = None, ):
        #logger.debug("get contours")
        img = frame.copy()

        big_contours = get_contours(frame, img_filter)
        if img_filter:
            frame = img_filter.apply_filter(frame)
        #logger.debug("aplied filter")
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        ret, binary = cv2.threshold(frame_gray, 1, 150, cv2.THRESH_BINARY)

        kernel = np.ones((15, 15), np.uint8)

        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        contours, hierarchy = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        #logger.debug("found contours")

        #cv2.drawContours(image=frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2,
         #                lineType=cv2.LINE_AA)

        centroids = []
        for c in contours:
            if cv2.contourArea(c) > self.json_handler.get_detection_radius():
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centroids.append((c, cx, cy))

        if len(centroids) > 0:
            try:
                draw_midpoints = self.tracker.track_contours(centroids)
                for iterations, c, cx, cy in draw_midpoints:
                    if iterations < 10:
                        cv2.circle(img, (cx, cy), 4, (0, 0, 255), -1)
                    elif iterations == 10:
                        self.point_handler.handle_point(cx, cy, camera_number)
            except Exception as e:
                print(e)

        #cv2.namedWindow("output", cv2.WINDOW_NORMAL)
        #cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        #cv2.resizeWindow("output", 1200, 900)
        #cv2.resizeWindow("frame", 1200, 900)
        #cv2.imshow("output", img)
        #cv2.imshow("frame", frame)
        #cv2.waitKey(1)

    def get_contours(self, frame, img_filter: ImageFilter = None):
        """takes the given image and returens a list of spotted contours"""
        if img_filter:
            frame = img_filter.apply_filter(frame)
        # logger.debug("aplied filter")
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        ret, binary = cv2.threshold(frame_gray, 1, 150, cv2.THRESH_BINARY)

        kernel = np.ones((15, 15), np.uint8)

        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        contours, hierarchy = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        correct_contours = []
        for c in contours:
            if cv2.contourArea(c) > self.json_handler.get_detection_radius():
                correct_contours.append(c)
        return correct_contours



    def draw_contours(self, contours, frame):
        """draw's given contours over the given frame """
        cv2.drawContours(image=frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2,
                lineType=cv2.LINE_AA)
        return frame