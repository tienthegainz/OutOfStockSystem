from __future__ import print_function, division
import sys
import os
import torch
import numpy as np
import random

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
from torch.utils.data.sampler import Sampler

# import skimage.io
# import skimage.transform
# import skimage.color
# import skimage
import cv2
import traceback
# VOC
from PIL import Image
if sys.version_info[0] == 2:
    import xml.etree.cElementTree as ET
else:
    import xml.etree.ElementTree as ET

DATASET_CLASSES = ("goi", "chai", "lon")

CLASSES_TO_IDS = dict(zip(DATASET_CLASSES, range(len(DATASET_CLASSES))))


def get_list_ids(path):
    """
        path: image_path or xml_path
        output: list of [image, xml] item name
    """
    ids = list()
    for item in os.listdir(path):
        parts = item.split('.')[:-1]
        if not parts:
            print("Skip ", item)
        else:
            name = '.'.join(parts)
            ids.append(name)
    return ids


class VOCDataset(Dataset):
    """
        VOC dataset
    """

    def __init__(self, root, mode='train', transform=None):
        self.root = root
        self.transform = transform
        if mode == 'train':
            self._annopath = os.path.join(self.root, 'train_xml', '%s.xml')
            self._imgpath = os.path.join(self.root, 'train_image', '%s')
            self.image_ids = get_list_ids(
                os.path.join(self.root, 'train_image'))
        elif mode == 'val':
            # self._annopath = os.path.join(self.root, 'val_xml', '%s.xml')
            # self._imgpath = os.path.join(self.root, 'val_image', '%s')
            # self.image_ids = get_list_ids(os.path.join(self.root, 'val_image'))
            self._annopath = os.path.join(self.root, 'train_xml', '%s.xml')
            self._imgpath = os.path.join(self.root, 'train_image', '%s')
            self.image_ids = get_list_ids(
                os.path.join(self.root, 'train_image'))
        else:
            print('%s not supported. Exitting\n' % mode)
            exit(-1)

    def __getitem__(self, idx):
        img = self.load_image(idx)
        annot = self.load_annotations(idx)
        sample = {'img': img, 'annot': annot}

        if self.transform:
            sample = self.transform(sample)

        return sample

    def __len__(self):
        return len(self.image_ids)

    def load_image(self, idx):
        try:
            img_id = self.image_ids[idx]
            xml_name = self._annopath % img_id
            anno_file = ET.parse(xml_name).getroot()

            file_postfix = anno_file.find('./filename').text.split('.')[-1]
            image_name = img_id+'.' + file_postfix
            image = Image.open(self._imgpath % image_name).convert('RGB')
            return np.array(image)/255.00
        except Exception as e:
            print("Err image: {} - idx: {}".format(self.image_ids[idx], idx))
            traceback.print_exc()

    def load_annotations(self, idx):
        img_id = self.image_ids[idx]
        xml_name = self._annopath % img_id
        anno_file = ET.parse(xml_name).getroot()

        annot = []
        for obj in anno_file.iter('object'):

            name = obj.find('name').text.lower().strip()
            if name not in DATASET_CLASSES:
                continue

            bbox = obj.find('bndbox')

            pts = ['xmin', 'ymin', 'xmax', 'ymax']
            bndbox = []
            for i, pt in enumerate(pts):
                cur_pt = float(bbox.find(pt).text)
                bndbox.append(cur_pt)
            label_idx = CLASSES_TO_IDS[name]
            bndbox.append(label_idx)
            annot.append(bndbox)  # [xmin, ymin, xmax, ymax, label_ind]

        return np.array(annot)  # [[xmin, ymin, xmax, ymax, label_ind], ... ]

    def image_aspect_ratio(self, image_index):
        img_id = self.image_ids[idx]
        xml_name = self._annopath % img_id
        anno_file = ET.parse(name).getroot()
        file_postfix = anno_file.find('./filename').text.split('.')[-1]
        image_name = img_id+'.' + file_postfix
        image = Image.open(self._imgpath % image_name).convert('RGB')
        return float(image.width) / float(image.height)

    def num_classes(self):
        return len(DATASET_CLASSES)

    def label_to_name(self, label):
        return DATASET_CLASSES[label]


def collater(data):

    imgs = [s['img'] for s in data]
    annots = [s['annot'] for s in data]
    scales = [s['scale'] for s in data]

    widths = [int(s.shape[0]) for s in imgs]
    heights = [int(s.shape[1]) for s in imgs]
    batch_size = len(imgs)

    max_width = np.array(widths).max()
    max_height = np.array(heights).max()

    padded_imgs = torch.zeros(batch_size, max_width, max_height, 3)

    for i in range(batch_size):
        img = imgs[i]
        padded_imgs[i, :int(img.shape[0]), :int(img.shape[1]), :] = img

    max_num_annots = max(annot.shape[0] for annot in annots)

    if max_num_annots > 0:

        annot_padded = torch.ones((len(annots), max_num_annots, 5)) * -1

        if max_num_annots > 0:
            for idx, annot in enumerate(annots):
                # print(annot.shape)
                if annot.shape[0] > 0:
                    annot_padded[idx, :annot.shape[0], :] = annot
    else:
        annot_padded = torch.ones((len(annots), 1, 5)) * -1

    padded_imgs = padded_imgs.permute(0, 3, 1, 2)

    return {'img': padded_imgs, 'annot': annot_padded, 'scale': scales}


class Resizer(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample, common_size=512):
        image, annots = sample['img'], sample['annot']
        height, width, _ = image.shape
        if height > width:
            scale = common_size / height
            resized_height = common_size
            resized_width = int(width * scale)
        else:
            scale = common_size / width
            resized_height = int(height * scale)
            resized_width = common_size

        image = cv2.resize(image, (resized_width, resized_height))

        new_image = np.zeros((common_size, common_size, 3))
        new_image[0:resized_height, 0:resized_width] = image
        annots[:, :4] *= scale

        return {'img': torch.from_numpy(new_image), 'annot': torch.from_numpy(annots), 'scale': scale}


class Augmenter(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample, flip_x=0.5):

        if np.random.rand() < flip_x:
            image, annots = sample['img'], sample['annot']
            image = image[:, ::-1, :]

            rows, cols, channels = image.shape

            x1 = annots[:, 0].copy()
            x2 = annots[:, 2].copy()

            x_tmp = x1.copy()

            annots[:, 0] = cols - x2
            annots[:, 2] = cols - x_tmp

            sample = {'img': image, 'annot': annots}

        return sample


class Normalizer(object):

    def __init__(self):
        self.mean = np.array([[[0.485, 0.456, 0.406]]])
        self.std = np.array([[[0.229, 0.224, 0.225]]])

    def __call__(self, sample):

        image, annots = sample['img'], sample['annot']

        return {'img': ((image.astype(np.float32)-self.mean)/self.std), 'annot': annots}


class UnNormalizer(object):
    def __init__(self, mean=None, std=None):
        if mean == None:
            self.mean = [0.485, 0.456, 0.406]
        else:
            self.mean = mean
        if std == None:
            self.std = [0.229, 0.224, 0.225]
        else:
            self.std = std

    def __call__(self, tensor):
        """
        Args:
            tensor (Tensor): Tensor image of size (C, H, W) to be normalized.
        Returns:
            Tensor: Normalized image.
        """
        for t, m, s in zip(tensor, self.mean, self.std):
            t.mul_(s).add_(m)
        return tensor


class AspectRatioBasedSampler(Sampler):

    def __init__(self, data_source, batch_size, drop_last):
        self.data_source = data_source
        self.batch_size = batch_size
        self.drop_last = drop_last
        self.groups = self.group_images()

    def __iter__(self):
        random.shuffle(self.groups)
        for group in self.groups:
            yield group

    def __len__(self):
        if self.drop_last:
            return len(self.data_source) // self.batch_size
        else:
            return (len(self.data_source) + self.batch_size - 1) // self.batch_size

    def group_images(self):
        # determine the order of the images
        order = list(range(len(self.data_source)))
        order.sort(key=lambda x: self.data_source.image_aspect_ratio(x))

        # divide into groups, one group = one batch
        return [[order[x % len(order)] for x in range(i, i + self.batch_size)] for i in range(0, len(order), self.batch_size)]


if __name__ == "__main__":
    dataset_train = VOCDataset('test_data',
                               transform=transforms.Compose([Normalizer(), Augmenter(), Resizer()]))
    # dataset_train = VOCDataset('test_data')
    for i in range(2):
        data = dataset_train.__getitem__(i)
        print(data['img'].shape)
        print(data['annot'])
