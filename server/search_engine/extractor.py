import sys
import os
from server.search_engine.model import resnet50
from torchvision import transforms
import torch
import PIL
import functools
import numpy as np


class Extractor():
    def __init__(self, size=248):
        self.model = resnet50(pretrained=True, progress=True)
        self.size = size
        self.tfms = transforms.Compose([
            transforms.Resize((self.size, self.size)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def extract(self, image):
        # Return numpy array
        return self.model.extract(self.preprocess(image)).detach().cpu().numpy()

    def extract_many(self, images):
        """
            images: list of PIL Image
            Return: numpy array
        """
        images = [self.preprocess(image) for image in images]

        images_tensor = torch.cat(images, dim=0)

        return self.model.extract(images_tensor).detach().cpu().numpy()

    def extract_database(self, data_path, n=4):
        """
            n: chunk size
            Output: {cls: [], ...}
        """
        # Return dict
        result = {}
        for cls in os.listdir(data_path):
            cls_path = os.path.join(data_path, cls)
            image_list = [PIL.Image.open(os.path.join(cls_path, ip))
                          for ip in os.listdir(cls_path)]
            image_chunk = [image_list[i:i+n]
                           for i in range(0, len(image_list), n)]
            # print(image_chunk)
            cls_feature = []
            for image in image_chunk:
                cls_feature.append(self.extract_many(image))
            cls_feature = np.concatenate(cls_feature)
            result[cls] = cls_feature
        return result

    def preprocess(self, image):
        return torch.unsqueeze(self.tfms(image), 0)

    def get_output_size(self):
        return self.model.output_size


if __name__ == "__main__":
    e = Extractor()
    e.extract_database('server/image_data', n=2)
    # images = PIL.Image.open("/home/tienhv/Pictures/fire.jpg")

    # feature = e.extract(images)
    # print(feature.shape)
