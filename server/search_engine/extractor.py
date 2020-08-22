import sys
import os
from search_engine.model import resnet50
from torchvision import transforms
import torch
import PIL
import functools
import numpy as np
from db import *


class Extractor(metaclass=Singleton):
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

    def preprocess(self, image):
        return torch.unsqueeze(self.tfms(image), 0)

    def get_output_size(self):
        return self.model.output_size


if __name__ == "__main__":
    e = Extractor()
