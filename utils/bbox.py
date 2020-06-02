"""
bbox utils module
"""

import numpy as np
import cv2


class BoundBox:
    """
    class BoundBox
    """
    def __init__(self, xmin, ymin, xmax, ymax, c=None, classes=None):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.c = c
        self.classes = classes

    def get_label(self):
        """
        get label of bounding box
        """
        return np.argmax(self.classes)

    def get_score(self):
        """
        get score of bounding box
        """
        return self.classes[self.get_label()]


def _interval_overlap(interval_a, interval_b):
    x_1, x_2 = interval_a
    x_3, x_4 = interval_b

    if x_3 < x_1:
        if x_4 < x_1:
            return 0
        return min(x_2, x_4) - x_1
    if x_2 < x_3:
        return 0
    return min(x_2, x_4) - x_3


def bbox_iou(box1, box2):
    """
    calculate iou between 2 box
    """
    intersect_w = _interval_overlap([box1.xmin, box1.xmax], [box2.xmin, box2.xmax])
    intersect_h = _interval_overlap([box1.ymin, box1.ymax], [box2.ymin, box2.ymax])

    intersect = intersect_w * intersect_h

    w_1, h_1 = box1.xmax - box1.xmin, box1.ymax - box1.ymin
    w_2, h_2 = box2.xmax - box2.xmin, box2.ymax - box2.ymin

    union = w_1 * h_1 + w_2 * h_2 - intersect

    return float(intersect) / union


def draw_boxes(image, boxes):
    """
    draw boxes on image
    """
    for box in boxes:
        cv2.rectangle(img=image, pt1=(box["xmin"], box["ymin"]), pt2=(box["xmax"], box["ymax"]),
                      color=(0, 255, 255),
                      thickness=5)
        label = box["class"] + str(round(box["score"] * 100, 2))
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.1e-3 * image.shape[0], 5)
        width, height = text_size[0][0], text_size[0][1]
        region = np.array([[box["xmin"] - 3, box["ymin"] + height],
                           [box["xmin"] - 3, box["ymin"]],
                           [box["xmin"] + width + 13, box["ymin"]],
                           [box["xmin"] + width + 13, box["ymin"] + height]], dtype='int32')
        cv2.fillPoly(img=image, pts=[region], color=(0, 255, 255))
        cv2.putText(img=image,
                    text=label,
                    org=(box["xmin"] + 13, box["ymin"] + height),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1e-3 * image.shape[0],
                    color=(0, 0, 0),
                    thickness=2)
    return image
