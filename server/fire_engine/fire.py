import os
import sys
sys.path.append('/home/tienhv/GR/OutOfStockSystem/server')  # nopep8
from shutil import Error
from PIL import Image
from common import Singleton
import time

from fire_engine.model import resnet101
import torch
import torch.nn.functional as F
from torchvision import transforms
from config import FIRE_MODEL, SAMPLE_IMAGE


class FireAlarm(metaclass=Singleton):
    """
    docstring
    """

    def __init__(self):
        self.fire_model = resnet101(num_classes=FIRE_MODEL['num_classes'])
        self.device = torch.device('cpu')
        print("Booting fire classification model with {}".format(self.device))
        self.fire_model.load_state_dict(torch.load(
            FIRE_MODEL['weight'], map_location=self.device))
        self.fire_model.eval()
        self.size = 256
        self.tfms = transforms.Compose([
            transforms.Resize((self.size, self.size)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        # give RAM space
        image = self.check_fire(Image.open(SAMPLE_IMAGE))
        print("Booting fire detection: Done")

    def check_fire(self, image):
        t = time.time()
        try:
            image = self.preprocess_image(image)
            output = self.fire_model(image)
            print('Fire model output: ', output)
            _, predicted = torch.max(output.data, 1)
            predicted = predicted.item()
            if predicted != 1:
                return True
            else:
                output_normal = [val.item() for val in torch.squeeze(output)]
                variance = output_normal[1] - output_normal[0]
                percentage = abs(variance/output_normal[1])
                if percentage < 0.25:
                    return True
            return False
        except Exception as e:
            print(e)
            return None

    def preprocess_image(self, pil_image):
        image = self.tfms(pil_image)
        image = image.unsqueeze_(0).cpu()
        image = F.interpolate(image, size=self.size)
        return image
