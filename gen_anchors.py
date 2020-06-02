"""
calculate anchors for given data
"""
import random
import argparse
import json
import numpy as np
from utils.utils import parse_voc_annotation


def iou(ann, centroids):
    """
    calculate IOU
    """
    width, height = ann
    similarities = []

    for centroid in centroids:
        c_w, c_h = centroid

        if c_w >= width and c_h >= height:
            similarity = width * height / (c_w * c_h)
        elif c_w >= width and c_h <= height:
            similarity = width * c_h / (width * height + (c_w - width) * c_h)
        elif c_w <= width and c_h >= height:
            similarity = c_w * height / (width * height + c_w * (c_h - height))
        else:  # means both w,h are bigger than c_w and c_h respectively
            similarity = (c_w * c_h) / (width * height)
        similarities.append(similarity)  # will become (k,) shape

    return np.array(similarities)


def avg_iou(anns, centroids):
    """
    calculate average IOU
    """
    num = anns.shape[0]
    sum_value = 0.

    for i in range(anns.shape[0]):
        sum_value += max(iou(anns[i], centroids))
    return sum_value / num


def print_anchors(centroids):
    """
    print anchors
    """
    out_string = ''

    anchors = centroids.copy()

    widths = anchors[:, 0]
    sorted_indices = np.argsort(widths)

    for i in sorted_indices:
        out_string += str(int(anchors[i, 0] * 416)) + ',' + str(int(anchors[i, 1] * 416)) + ', '

    print(out_string[:-2])


def run_kmeans(ann_dims, anchor_num):
    """
    kmeans operation
    """
    ann_num = ann_dims.shape[0]
    prev_assignments = np.ones(ann_num) * (-1)
    iteration = 0
    old_distances = np.zeros((ann_num, anchor_num))

    indices = [random.randrange(ann_dims.shape[0]) for i in range(anchor_num)]
    centroids = ann_dims[indices]
    anchor_dim = ann_dims.shape[1]

    while True:
        distances = []
        iteration += 1
        for i in range(ann_num):
            distance = 1 - iou(ann_dims[i], centroids)
            distances.append(distance)
        distances = np.array(distances)  # distances.shape = (ann_num, anchor_num)

        print("iteration {}: dists = {}".format(iteration,
                                                np.sum(np.abs(old_distances - distances))))

        # assign samples to centroids
        assignments = np.argmin(distances, axis=1)

        if (assignments == prev_assignments).all():
            return centroids

        # calculate new centroids
        centroid_sums = np.zeros((anchor_num, anchor_dim), np.float)
        for i in range(ann_num):
            centroid_sums[assignments[i]] += ann_dims[i]
        for j in range(anchor_num):
            centroids[j] = centroid_sums[j] / (np.sum(assignments == j) + 1e-6)

        prev_assignments = assignments.copy()
        old_distances = distances.copy()


def _main_(args):
    config_path = args.conf
    num_anchors = args.anchors

    with open(config_path) as config_buffer:
        config = json.loads(config_buffer.read())

    train_imgs = parse_voc_annotation(
        config['train']['train_annot_folder'],
        config['train']['train_image_folder'],
        config['model']['labels']
    )[0]

    # run k_mean to find the anchors
    annotation_dims = []
    for image in train_imgs:
        print(image['filename'])
        for obj in image['object']:
            relative_w = (float(obj['xmax']) - float(obj['xmin'])) / image['width']
            relatice_h = (float(obj["ymax"]) - float(obj['ymin'])) / image['height']
            annotation_dims.append(tuple(map(float, (relative_w, relatice_h))))

    annotation_dims = np.array(annotation_dims)
    centroids = run_kmeans(annotation_dims, num_anchors)

    # write anchors to file
    print('\naverage IOU for', num_anchors, 'anchors:', '%0.2f' %
          avg_iou(annotation_dims, centroids))
    print_anchors(centroids)


if __name__ == '__main__':
    ARGPARSER = argparse.ArgumentParser()

    ARGPARSER.add_argument(
        '-c',
        '--conf',
        default='config.json',
        help='path to configuration file')
    ARGPARSER.add_argument(
        '-a',
        '--anchors',
        default=9,
        help='number of anchors to use')

    ARGS = ARGPARSER.parse_args()
    _main_(ARGS)
