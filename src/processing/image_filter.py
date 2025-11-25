import cv2
import numpy as np

class ImageFilter:
    def __init__(self):
        # init met default waarden
        self.lower_hue = 0
        self.upper_hue = 180
        self.lower_sat = 0
        self.upper_sat = 255
        self.lower_val = 0
        self.upper_val = 255

    def update_filter(self, lower_hue, upper_hue, lower_sat, upper_sat, lower_val, upper_val):

        self.lower_hue = lower_hue
        self.upper_hue = upper_hue
        self.lower_sat = lower_sat
        self.upper_sat = upper_sat
        self.lower_val = lower_val
        self.upper_val = upper_val

    def apply_filter(self, frame):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([self.lower_hue, self.lower_sat, self.lower_val])
        upper = np.array([self.upper_hue, self.upper_sat, self.upper_val])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        return result