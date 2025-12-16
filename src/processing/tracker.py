import cv2
import numpy as np


class Tracker:
    def __init__(self):
        self.tracked_objects = []
        self.next_id = 0
        self.MAX_DIST = 50

    def track_contours(self, contours):
        new_tracked = []

        for c, cx, cy in contours:
            matched = False

            for iterations, p, px, py in self.tracked_objects:
                if self.difference((cx, cy), (px, py)) < self.MAX_DIST:
                    new_tracked.append((iterations + 1,c, cx, cy))
                    matched = True
                    break

            if not matched:
                new_tracked.append((1, c, cx, cy))

        self.tracked_objects = new_tracked
        return self.tracked_objects

    @staticmethod
    def difference(p1, p2):
        #euclidean distance wikipedia
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])