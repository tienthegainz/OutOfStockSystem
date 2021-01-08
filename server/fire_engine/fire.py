import sys
sys.path.append('/home/tienhv/GR/OutOfStockSystem/server')  # nopep8
from shutil import Error
from PIL import Image
from db import Singleton
import time

from fire_engine.model import resnet101
import torch
import torch.nn.functional as F
from torchvision import transforms


class FireAlarm(metaclass=Singleton):
    """
    docstring
    """

    def __init__(self):
        self.fire_model = resnet101(num_classes=3)
        self.device = torch.device('cpu')
        print("Booting fire detection model with {}".format(self.device))
        self.fire_model.load_state_dict(torch.load(
            '/home/tienhv/GR/OutOfStockSystem/server/fire_engine/FireNet_ver2_epoch_2_loss_0.09.pth', map_location=self.device))
        self.fire_model.eval()
        self.size = 256
        self.tfms = transforms.Compose([
            transforms.Resize((self.size, self.size)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        # give RAM space
        image = self.preprocess_image(Image.open(
            '/home/tienhv/GR/OutOfStockSystem/server/storage/image/1/1.jpeg'))
        self.fire_model(image)
        print("Booting fire detection: Done")

    def check_fire(self, image):
        t = time.time()
        try:
            image = self.preprocess_image(image)
            output = self.fire_model(image)
            print('Output: ', output)
            _, predicted = torch.max(output.data, 1)
            predicted = predicted.item()
            print('Fire check time: {} -Result: {}'.format(time.time()-t, predicted))
            return False if predicted == 1 else True
        except Exception as e:
            print(e)
            return None

    def preprocess_image(self, pil_image):
        image = self.tfms(pil_image)
        image = image.unsqueeze_(0).cpu()
        image = F.interpolate(image, size=self.size)
        return image


# if __name__ == "__main__":
#     f = FireAlarm()
#     image = Image.open('/home/tienhv/GR/OutOfStockSystem/image/20.jpg')
#     print(f.check_fire(image))
