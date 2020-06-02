"""
detection module
"""
import argparse
import os
import json
import time
import cv2
from keras.models import load_model
from utils.utils import get_yolo_boxes, refine
from utils.bbox import draw_boxes
from voc_writer import Writer

class Detector:
    """
    Used for object detection
    """
    def __init__(self, config_path='config.json',
                 score_thresh=0.5, obj_thresh=0.5, nms_thresh=0.45):
        with open(config_path) as config_buffer:
            self.config = json.load(config_buffer)
        self.infer_model = load_model(self.config['train']['saved_weights_name'])
        self.labels = self.config['model']['labels']
        self.score_thresh = score_thresh
        self.obj_thresh = obj_thresh
        self.nms_thresh = nms_thresh

    def detect(self, image_path, result_path=None):
        """
        detect object in an image
        Args:
            image_path: path of image
            result_path: folder to save result image
        Returns:
            list_boxes: list of all detected boxes
        """
        net_h, net_w = 416, 416  # a multiple of 32, the smaller the faster
        image = cv2.imread(image_path)
        # predict the bounding boxes
        boxes = get_yolo_boxes(self.infer_model, [image], net_h, net_w,
                               self.config['model']['anchors'], self.obj_thresh, self.nms_thresh)[0]
        list_boxes = []
        for box in boxes:
            score = box.get_score()
            if score > self.score_thresh:
                obj = dict()
                obj["xmin"] = box.xmin
                obj["xmax"] = box.xmax
                obj["ymin"] = box.ymin
                obj["ymax"] = box.ymax
                class_id = box.get_label()
                label = self.config['model']['labels'][class_id]
                obj["class"] = label
                obj["score"] = score
                list_boxes.append(obj)
        if result_path:
            out_image = draw_boxes(image, list_boxes)
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            save_path = os.path.join(result_path, image_path.split('/')[-1])
            cv2.imwrite(save_path, out_image)
        return list_boxes

    def write_xml(self, image_path, out_folder):
        """
        detect and dump result to pascal voc format
        Args:
            image_path: path of image
            out_folder: path of folder to dump xml file
        Returns:
        """
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        # write value to xml
        height, width = cv2.imread(image_path).shape[:2]
        writer = Writer(image_path, width, height)
        list_boxes = self.detect(image_path)
        for obj in list_boxes:
            xmin, xmax, ymin, ymax, cls = obj["xmin"], obj["xmax"], obj["ymin"],\
                                          obj["ymax"], obj["class"]
            xmin = refine(xmin, 0, width)
            xmax = refine(xmax, 0, width)
            ymin = refine(ymin, 0, height)
            ymax = refine(ymax, 0, height)
            writer.add_object(cls, xmin, ymin, xmax, ymax)
            xml_name = os.path.splitext(image_path.split('/')[-1])[0]+'.xml'
            save_path = os.path.join(out_folder, xml_name)
            writer.save(save_path)


if __name__ == '__main__':
    ARGPARSER = argparse.ArgumentParser(description='Predict YOLO_v3 model on any test set')
    ARGPARSER.add_argument('-i', '--input_path', required=True, help='path to test folder')
    ARGPARSER.add_argument('-o', '--output_path', default=None, help='path to save result')
    ARGPARSER.add_argument('-d', '--dump', default=False, help='dump result to voc format or not')
    ARGS = ARGPARSER.parse_args()
    DETECTOR = Detector()
    INPUT_PATH = ARGS.input_path
    OUT_FOLDER = ARGS.output_path
    DUMP = ARGS.dump
    if os.path.isdir(INPUT_PATH):
        for name in os.listdir(INPUT_PATH):
            print('image', name)
            t = time.time()
            if name.endswith(('.jpg', '.png', '.jpeg')):
                img_path = os.path.join(INPUT_PATH, name)
                if not DUMP:
                    LIST_BOXES = DETECTOR.detect(img_path, OUT_FOLDER)
                else:
                    DETECTOR.write_xml(img_path, ARGS.output_path)
            print('processing time', time.time() - t)
    else:
        LIST_BOXES = DETECTOR.detect(INPUT_PATH, OUT_FOLDER)
