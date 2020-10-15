import sys
# sys.path.append('/home/tienhv/GR/OutOfStockSystem/server')  # nopep8
import torch
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
import time
from db import Singleton
from detect_engine.retinanet import model
from detect_engine.datasets.dataloader import Normalizer, Resizer, UnNormalizer, DATASET_CLASSES
from config import DETECTOR


class Detector(metaclass=Singleton):
    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.config = DETECTOR
        print("Booting detection model with {}".format(self.device))
        self.detect_model = self.init_model()
        self.tfms = self.init_transform()
        self.unnormalize = UnNormalizer()
        img = Image.open(
            'detect_engine/dummy.jpg')
        self.predict(img)
        print("Booting done")

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

    def predict(self, image):
        data = self.read_image(image)
        with torch.no_grad():
            st = time.time()
            scores, _, transformed_anchors = self.detect_model(
                data.to(self.device).float())
            print('Elapsed time: {}'.format(time.time()-st))
            idxs = np.where(scores.cpu() > 0.5)
            img = np.array(255 * self.unnormalize(data[0, :, :, :])).copy()

            img[img < 0] = 0
            img[img > 255] = 255

            img = np.transpose(img, (1, 2, 0)).astype(np.uint8)

            products = []
            bboxes = []

            for j in range(idxs[0].shape[0]):
                bbox = transformed_anchors[idxs[0][j], :]
                bboxes.append(bbox)
                x1 = int(bbox[0])
                y1 = int(bbox[1])
                x2 = int(bbox[2])
                y2 = int(bbox[3])

                # cv2.rectangle(img, (x1, y1), (x2, y2),
                #               color=(0, 255, 0), thickness=3)

                prod = img[y1:y2, x1:x2]
                products.append(prod)
                pil_image = Image.fromarray(prod)
                pil_image.show()

            pil_image = Image.fromarray(img)
            pil_image.show()

            return {'image': img, 'products': products, 'bboxes': bboxes}
