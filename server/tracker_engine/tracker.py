import sys
sys.path.append('/home/tienhv/GR/OutOfStockSystem/server')  # nopep8
from common import Singleton
from config import TRACKER
import cv2


class TrackerMulti(metaclass=Singleton):
    """
        Manage shelf area and object state single
    """

    def __init__(self):
        self.frame = None
        self.config = TRACKER
        # {id: string, bbox: list[], is_out: bool}
        self.objs = []
        self.updating = False
        self.old_ids = []
        # count for no detect frame
        self.count = 0
        print('Tracking engine booted')
    
    def pause(self):
        self.updating = True
    
    def unpause(self):
        self.updating = False
    
    def isPausing(self):
        return self.updating

    def update(self, frame, states=[], reset=False):
        # If false => Save image
        self.frame = frame
        if reset:
            self.old_ids = [id for id in self.objs]
            self.objs = []
            self.count = 0
        if states:
            if self.objs:
                for state in states:
                    if state['id'] in self.old_ids:
                        return True
                    check_index = -1
                    for idx, element in enumerate(self.objs):
                        # print(idx, ' - ', element)
                        if state['id'] == element['id']:
                            check_index = idx
                    if check_index >= 0:
                        # print('Update object\'s position with ID: {}'.format(
                        #     state['id']))
                        self.objs[check_index] = {
                            **state, 'is_out': self.objs[check_index]['is_out']}
                    else:
                        # print('Add new object\'s position with ID: {}'.format(
                        #     state['id']))
                        bbox = state['bbox']
                        center = (int(bbox[0] + bbox[2]/2),
                                  int(bbox[1] + bbox[3]/2))
                        state['is_out'] = self.check_outside(center)
                        self.objs.append(state)
            else:
                self.objs = [{**state, 'is_out': False} for state in states]
        else:
            self.count += 1
            if self.count >= self.config['no_bbox_thres'] and self.objs:
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

    def check_out_roi(self):
        """
            Check if object is out of ROI
        """
        # TODO
        out = False
        for idx, obj in enumerate(self.objs):
            bbox = obj['bbox']
            center = (int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2))
            if self.check_outside(center):
                if not obj['is_out']:
                    self.objs[idx]['is_out'] = True
                    out = True
            else:
                self.objs[idx]['is_out'] = False

        return out

    def check_outside(self, center):
        return (center[0] < int(self.config['roi'][0]) or
                center[0] > int(self.config['roi'][0] + self.config['roi'][2]) or
                center[1] < int(self.config['roi'][1]) or
                center[1] > int(self.config['roi'][1] + self.config['roi'][3]))

    def clear_objects(self, ids):
        self.objs = [obj for obj in self.objs if obj['id'] not in ids]

    def clear_all_objects(self):
        self.objs = []
