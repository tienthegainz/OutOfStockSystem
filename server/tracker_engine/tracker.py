import sys
sys.path.append('/home/tienhv/GR/OutOfStockSystem/server')  # nopep8
from db import Singleton
from config import TRACKER
import cv2


class Tracker(metaclass=Singleton):
    """
        Manage shelf area and object state
    """

    def __init__(self):
        self.count = 0
        self.track_obj = {}
        self.frame = None
        self.bbox = None

    def update(self, frame, bbox):
        self.bbox = bbox
        self.frame = frame

    def update_frame(self, frame):
        self.frame = frame

    def draw(self):
        if self.bbox:
            p1 = (int(self.bbox[0]), int(self.bbox[1]))
            p2 = (int(self.bbox[0] + self.bbox[2]),
                  int(self.bbox[1] + self.bbox[3]))
            cv2.rectangle(self.frame, p1, p2, (255, 0, 0), 2, 1)
        return self.frame
