import cv2
import numpy as np
import json

class ImageFilter:
    with open("filter_values.json") as json_file:
        data = json.load(json_file)

    def __init__(self):
        self.lower_hue = self.data["lower_hue"]
        self.upper_hue = self.data["upper_hue"]
        self.lower_sat = self.data["lower_sat"]
        self.upper_sat = self.data["upper_sat"]
        self.lower_val = self.data["lower_val"]
        self.upper_val = self.data["upper_val"]

    def update_filter(self, lower_hue, upper_hue, lower_sat, upper_sat, lower_val, upper_val):

        self.lower_hue = lower_hue
        self.upper_hue = upper_hue
        self.lower_sat = lower_sat
        self.upper_sat = upper_sat
        self.lower_val = lower_val
        self.upper_val = upper_val

    def update_json(self):
        data = {
            "lower_hue": self.lower_hue,
            "upper_hue": self.upper_hue,
            "lower_sat": self.lower_sat,
            "upper_sat": self.upper_sat,
            "lower_val": self.lower_val,
            "upper_val": self.upper_val,
        }
        json_str = json.dumps(data)
        with open("filter_values.json", "w") as json_file:
            json_file.write(json_str)

    def apply_filter(self, frame):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([self.lower_hue, self.lower_sat, self.lower_val])
        upper = np.array([self.upper_hue, self.upper_sat, self.upper_val])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        return result