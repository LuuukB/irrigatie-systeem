import cv2
import numpy as np
import logging
logger = logging.getLogger(__name__)

from processing.image_filter import ImageFilter
from processing.tracker import Tracker
from processing.point_handler import PointHandler

class Cv2Processor:
    def __init__(self, point_handler=None):
        self.tracker = Tracker()
        self.point_handler = point_handler

    def get_contours(self, frame, camera_number, img_filter: ImageFilter = None, ):
        #logger.debug("get contours")
        img = frame.copy()

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
            if cv2.contourArea(c) > 10000:
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centroids.append((c, cx, cy))

        if len(centroids) > 0:
            try:
                draw_midpoints = self.tracker.track_contours(centroids)
                for iterations, c, cx, cy in draw_midpoints:
                    if iterations < 20:
                        cv2.circle(img, (cx, cy), 4, (0, 0, 255), -1)
                    elif iterations == 20:
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