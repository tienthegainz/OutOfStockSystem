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
        self.config = TRACKER
        self.state = {'is_out': False}

    def update(self, frame, bbox):
        self.bbox = bbox
        self.frame = frame

    def update_frame(self, frame):
        self.frame = frame

    def draw_bbox(self, frame):
        if self.bbox:
            p1 = (int(self.bbox[0]), int(self.bbox[1]))
            p2 = (int(self.bbox[0] + self.bbox[2]),
                  int(self.bbox[1] + self.bbox[3]))
            cv2.rectangle(frame, p1, p2, (0, 255, 255), 2, 1)
        return frame

    def draw_roi(self, frame):
        p1 = (int(self.config['roi'][0]), int(self.config['roi'][1]))
        p2 = (int(self.config['roi'][0] + self.config['roi'][2]),
              int(self.config['roi'][1] + self.config['roi'][3]))
        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        return frame

    def draw(self):
        frame = self.frame
        frame = self.draw_roi(frame)
        frame = self.draw_bbox(frame)
        return frame

    def check_outside(self):
        """
            Check if object is out of ROI
        """
        obj_center = (int(self.bbox[0] + self.bbox[2]/2),
                      int(self.bbox[1] + self.bbox[3]/2))
        if obj_center[0] < int(self.config['roi'][0]) or \
                obj_center[0] > int(self.config['roi'][0] + self.config['roi'][2]) or \
                obj_center[1] < int(self.config['roi'][1]) or \
                obj_center[1] > int(self.config['roi'][1] + self.config['roi'][3]):
            if self.state['is_out']:
                return False
            else:
                self.state['is_out'] = True
                return True
        else:
            return False


if __name__ == "__main__":
    import time
    tracker = cv2.TrackerKCF_create()
    img1 = cv2.imread(
        '/home/tienhv/GR/OutOfStockSystem/server/images/wat84m.jpg')
    img2 = cv2.imread(
        '/home/tienhv/GR/OutOfStockSystem/server/images/wat84m.jpg')

    scale_percent = 60  # percent of original size
    width = int(img1.shape[1] * scale_percent / 100)
    height = int(img1.shape[0] * scale_percent / 100)
    dim = (width, height)

    img1 = cv2.resize(img1, dim, interpolation=cv2.INTER_AREA)
    img2 = cv2.resize(img2, dim, interpolation=cv2.INTER_AREA)

    tracker.init(img1, (0, 0, 200, 100))
    t = time.time()
    (success, box) = tracker.update(img1)
    print("{} - {}".format(success, box))
    print('Time: {}'.format(time.time() - t))
