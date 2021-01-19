import sys
sys.path.append('/home/tienhv/GR/OutOfStockSystem/server')  # nopep8
from db import Singleton
from config import TRACKER
import cv2


class Tracker(metaclass=Singleton):
    """
        Manage shelf area and object state single
    """

    def __init__(self):
        self.frame = None
        self.bbox = None
        self.config = TRACKER
        self.is_out = False

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
        frame = self.frame.copy()
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
            if self.is_out:
                return False
            else:
                self.is_out = True
                return True
        else:
            return False


class TrackerMulti(metaclass=Singleton):
    """
        Manage shelf area and object state single
    """

    def __init__(self):
        self.frame = None
        self.config = TRACKER
        # {id: string, bbox: list[], is_out: bool}
        self.objs = []
        # count for no detect frame
        self.count = 0

    def update(self, frame, states=[]):
        # If false => Save image
        self.frame = frame
        if states:
            if self.objs:
                for state in states:
                    check_index = -1
                    for idx, element in enumerate(self.objs):
                        # print(idx, ' - ', element)
                        if state['id'] == element['id']:
                            check_index = idx
                    if check_index >= 0:
                        print('Update object\'s position with ID: {}'.format(
                            state['id']))
                        self.objs[check_index] = {
                            **state, 'is_out': self.objs[check_index]['is_out']}
                    else:
                        print('Add new object\'s position with ID: {}'.format(
                            state['id']))
                        state['is_out'] = False
                        self.objs.append(state)
            else:
                self.objs = [{**state, 'is_out': False} for state in states]
        else:
            self.count += 1
            if self.count >= self.config['no_bbox_thres']:
                # clear all object
                self.objs = []
                self.count = 0
                return False
        return True

    def draw_bbox(self, frame):
        for obj in self.objs:
            bbox = obj['bbox']
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]),
                  int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (0, 255, 255), 2, 1)
        return frame

    def draw_roi(self, frame):
        p1 = (int(self.config['roi'][0]), int(self.config['roi'][1]))
        p2 = (int(self.config['roi'][0] + self.config['roi'][2]),
              int(self.config['roi'][1] + self.config['roi'][3]))
        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        return frame

    def draw(self):
        frame = self.frame.copy()
        frame = self.draw_roi(frame)
        frame = self.draw_bbox(frame)
        return frame

    def check_outside(self):
        """
            Check if object is out of ROI
        """
        # TODO
        out = False
        for idx, obj in enumerate(self.objs):
            bbox = obj['bbox']
            obj_center = (int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2))
            if obj_center[0] < int(self.config['roi'][0]) or \
                    obj_center[0] > int(self.config['roi'][0] + self.config['roi'][2]) or \
                    obj_center[1] < int(self.config['roi'][1]) or \
                    obj_center[1] > int(self.config['roi'][1] + self.config['roi'][3]):
                if not obj['is_out']:
                    self.objs[idx]['is_out'] = True
                    out = True
            else:
                self.objs[idx]['is_out'] = False

        return out


if __name__ == "__main__":
    t = TrackerMulti()
    frame = cv2.imread(
        '/home/tienhv/2021-01-06-215110.jpg')
    t.update(frame, [
        {'id': 'are123', 'bbox': [160, 280, 50, 78]},
        {'id': 'qhi538', 'bbox': [450, 310, 80, 100]}
    ])
    print('Out: ', t.check_outside())
    cv2.imshow('image', t.draw())
    cv2.waitKey(0)
    print(t.objs)

    t.update(frame, [
        {'id': 'are123', 'bbox': [160, 150, 50, 78]},
        {'id': 'eee4w1', 'bbox': [200, 280, 180, 200]}
    ])
    print('Out: ', t.check_outside())
    cv2.imshow('image', t.draw())
    cv2.waitKey(0)
    print(t.objs)

    t.update(frame)
    print('Out: ', t.check_outside())
    cv2.imshow('image', t.draw())
    cv2.waitKey(0)
    print(t.objs)
