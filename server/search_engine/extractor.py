import sys
import os
from search_engine.model import resnet50
from torchvision import transforms
import torch
import PIL
import functools
import numpy as np
from common import Singleton


class Extractor(metaclass=Singleton):
    """
        Exect image feature to build graph
    """

    def __init__(self, size=248):
        print('Init Extraction engine')
        self.model = resnet50(pretrained=True, progress=True)
        self.size = size
        self.tfms = transforms.Compose([
            transforms.Resize((self.size, self.size)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self.extract(PIL.Image.open(
            "/home/tienhv/GR/OutOfStockSystem/server/storage/image/1/1.jpeg"))

    def extract(self, image):
        # Return numpy array
        return self.model.extract(self.preprocess(image)).detach().cpu().numpy()

    def extract_many(self, images):
        """
            images: list of PIL Image
            Return: numpy array
        """
        features = [self.extract(image) for image in images]
        features = np.squeeze(np.array(features), axis=1)

        return features

    def preprocess(self, image):
        return torch.unsqueeze(self.tfms(image), 0)

    def get_output_size(self):
        return self.model.output_size
