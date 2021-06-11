import os
import sys
# sys.path.append('/home/tienhv/GR/OutOfStockSystem/server')  # nopep8
import torch
from torchvision import transforms
from PIL import Image, ImageDraw
import cv2
import numpy as np
import time
from common import Singleton
from detect_engine.retinanet import model
from detect_engine.datasets.dataloader import Normalizer, Resizer, UnNormalizer, DATASET_CLASSES
from config import DETECTOR, SAMPLE_IMAGE


class Detector(metaclass=Singleton):
    """
        Detect object
    """

    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.config = DETECTOR
        print("Booting detection model with {}".format(self.device))
        self.detect_model = self.init_model()
        self.tfms = self.init_transform()
        self.unnormalize = UnNormalizer()
        # give RAM space
        img = Image.open(SAMPLE_IMAGE)
        self.predict(img)
        print("Booting detection: Done")

    def read_checkpoint(self):
        checkpoint = torch.load(self.config['weight'])
        if 'num_classes' not in checkpoint:
            checkpoint['num_classes'] = self.config['num_classes']
        return checkpoint

    def init_model(self):
        checkpoint = self.read_checkpoint()
        detect_model = model.retina_bb_resnet50(
            num_classes=checkpoint['num_classes'])
        detect_model.load_state_dict(checkpoint['state_dict'])
        detect_model.to(self.device)
        detect_model.eval()
        detect_model.training = False
        return detect_model

    def init_transform(self):
        return transforms.Compose([Normalizer(), Resizer()])

    def read_image(self, image):
        data = {
            'img': np.array(image)/255.00,
            'annot': np.array([[0.00, 0.00, 0.00, 0.00, 0.00, ]])
        }
        data = self.tfms(data)
        return data['img'].permute(2, 0, 1).unsqueeze(0)

    def valid_bboxes(self, bboxes):
        r = len(bboxes)
        if r == 1:
            return bboxes
        for i in range(r):
            if bboxes[i] == None:
                continue
            bbox_i = bboxes[i]
            x1_i = int(bbox_i[0])
            y1_i = int(bbox_i[1])
            x2_i = int(bbox_i[2])
            y2_i = int(bbox_i[3])
            S_i = (x2_i-x1_i)*(y2_i-y1_i)
            for j in range(r):
                if i == j or bboxes[j] == None:
                    continue
                bbox_j = bboxes[j]
                x1_j = int(bbox_j[0])
                y1_j = int(bbox_j[1])
                x2_j = int(bbox_j[2])
                y2_j = int(bbox_j[3])
                S_j = (x2_j-x1_j)*(y2_j-y1_j)
                S_ij = max(0, min(x2_i, x2_j) - max(x1_i, x1_j)) * \
                    max(0, min(y2_i, y2_j) - max(y1_i, y1_j))
                # print("i={}, j={}, S_i={}, S_ij={}, p={}".format(
                #     i, j, S_i, S_ij, S_ij/S_i))
                if (S_ij/S_i) > self.config['overlap_thres']:
                    bboxes[j if S_j < S_i else i] = None

        return bboxes

    def predict(self, image):
        image = np.array(image)

        image_orig = image.copy()

        rows, cols, cns = image.shape

        smallest_side = min(rows, cols)

        # rescale the image so the smallest side is min_side
        min_side = 608
        max_side = 1024
        scale = min_side / smallest_side

        # check if the largest side is now greater than max_side, which can happen
        # when images have a large aspect ratio
        largest_side = max(rows, cols)

        if largest_side * scale > max_side:
            scale = max_side / largest_side

        # resize the image with the computed scale
        image = cv2.resize(image, (int(round(cols * scale)),
                                   int(round((rows * scale)))))
        rows, cols, cns = image.shape

        pad_w = 32 - rows % 32
        pad_h = 32 - cols % 32

        new_image = np.zeros(
            (rows + pad_w, cols + pad_h, cns)).astype(np.float32)
        new_image[:rows, :cols, :] = image.astype(np.float32)
        image = new_image.astype(np.float32)
        image /= 255
        image -= [0.485, 0.456, 0.406]
        image /= [0.229, 0.224, 0.225]
        image = np.expand_dims(image, 0)
        image = np.transpose(image, (0, 3, 1, 2))
        image = torch.from_numpy(image)
        with torch.no_grad():
            st = time.time()
            scores, classification, transformed_anchors = self.detect_model(
                image.to(self.device).float())

            del image
            scores = scores.cpu()
            classification = classification.cpu()
            transformed_anchors = transformed_anchors.cpu()

            print('Detect time: {}'.format(time.time()-st))
            idxs = np.where(scores > 0.5)

            products = []
            bboxes = {}

            for j in range(idxs[0].shape[0]):
                bbox = transformed_anchors[idxs[0][j], :]
                cls = str(int(classification[idxs[0][j]]))
                if cls not in bboxes:
                    bboxes[cls] = []
                bboxes[cls].append(bbox.tolist())

            for k, v in bboxes.items():
                bboxes[k] = self.valid_bboxes(v)

            point_bbox = []

            for k, v in bboxes.items():
                for bbox in v:
                    if bbox == None:
                        continue
                    x1 = int(bbox[0] / scale)
                    y1 = int(bbox[1] / scale)
                    x2 = int(bbox[2] / scale)
                    y2 = int(bbox[3] / scale)
                    point_bbox.append(tuple([x1, y1, x2-x1, y2-y1]))
                    # cv2.rectangle(image_orig, (x1, y1), (x2, y2),
                    #               color=(0, 0, 255), thickness=2)

                    prod = image_orig[y1:y2, x1:x2]
                    products.append(prod)

            # pil_image = Image.fromarray(image_orig.astype(np.uint8))

            return {'image': image_orig, 'products': products, 'bboxes': point_bbox}

    def test(self):
        return True
