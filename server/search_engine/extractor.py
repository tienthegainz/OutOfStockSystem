import os
from search_engine.model import resnet50
from torchvision import transforms
import torch
import PIL
import numpy as np
from common import Singleton
from config import EXTRACTOR, SAMPLE_IMAGE


class Extractor(metaclass=Singleton):
    """
        Exect image feature to build graph
    """

    def __init__(self, size=248):
        print('Init Extraction engine')
        self.model = resnet50()
        self.device = torch.device('cpu')
        print("Booting extraction model with {}".format(self.device))
        self.model.load_state_dict(torch.load(
            EXTRACTOR['weight'], map_location=self.device))
        self.size = size
        self.tfms = transforms.Compose([
            transforms.Resize((self.size, self.size)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self.extract(PIL.Image.open(SAMPLE_IMAGE))

    def extract(self, image):
        # Return numpy array
        return self.model.extract(self.preprocess(image)).detach().cpu().numpy()

    def extract_many(self, images):
        """
            images: list of PIL Image
            Return: numpy array
        """
        features = [self.extract(image) for image in images]
        features = np.array(features)
        features = np.squeeze(features, axis=1)

        return features

    def preprocess(self, image):
        return torch.unsqueeze(self.tfms(image), 0)

    def get_output_size(self):
        return self.model.output_size
