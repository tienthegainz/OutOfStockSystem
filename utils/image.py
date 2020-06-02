"""
image utils module
"""
import copy
import cv2
import numpy as np


def _rand_scale(scale):
    """
    randome scale
    """
    scale = np.random.uniform(1, scale)
    return scale if (np.random.randint(2) == 0) else 1. / scale


def _constrain(min_v, max_v, value):
    """
    constrain value to give range
    """
    if value < min_v:
        return min_v
    if value > max_v:
        return max_v
    return value


def random_flip(image, flip):
    """
    random flip
    """
    if flip == 1:
        return cv2.flip(image, 1)
    return image


def correct_bounding_boxes(boxes, new_w, new_h, net_w, net_h, d_x, d_y, flip, image_w, image_h):
    """
    correct bounding boxes
    """
    boxes = copy.deepcopy(boxes)

    # randomize boxes' order
    np.random.shuffle(boxes)

    # correct sizes and positions
    s_x, s_y = float(new_w) / image_w, float(new_h) / image_h
    zero_boxes = []

    for i in range(len(boxes)):
        boxes[i]['xmin'] = int(_constrain(0, net_w, boxes[i]['xmin'] * s_x + d_x))
        boxes[i]['xmax'] = int(_constrain(0, net_w, boxes[i]['xmax'] * s_x + d_x))
        boxes[i]['ymin'] = int(_constrain(0, net_h, boxes[i]['ymin'] * s_y + d_y))
        boxes[i]['ymax'] = int(_constrain(0, net_h, boxes[i]['ymax'] * s_y + d_y))

        if boxes[i]['xmax'] <= boxes[i]['xmin'] or boxes[i]['ymax'] <= boxes[i]['ymin']:
            zero_boxes += [i]
            continue

        if flip == 1:
            swap = boxes[i]['xmin']
            boxes[i]['xmin'] = net_w - boxes[i]['xmax']
            boxes[i]['xmax'] = net_w - swap

    boxes = [boxes[i] for i in range(len(boxes)) if i not in zero_boxes]

    return boxes


def random_distort_image(image, hue=18, saturation=1.5, exposure=1.5):
    """
    random distort
    """
    # determine scale factors
    dhue = np.random.uniform(-hue, hue)
    dsat = _rand_scale(saturation)
    dexp = _rand_scale(exposure)

    # convert RGB space to HSV space
    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype('float')

    # change satuation and exposure
    image[:, :, 1] *= dsat
    image[:, :, 2] *= dexp

    # change hue
    image[:, :, 0] += dhue
    image[:, :, 0] -= (image[:, :, 0] > 180) * 180
    image[:, :, 0] += (image[:, :, 0] < 0) * 180

    # convert back to RGB from HSV
    return cv2.cvtColor(image.astype('uint8'), cv2.COLOR_HSV2RGB)


def apply_random_scale_and_crop(image, new_w, new_h, net_w, net_h, d_x, d_y):
    """
    random scale and crop image
    """
    im_sized = cv2.resize(image, (new_w, new_h))

    if d_x > 0:
        im_sized = np.pad(im_sized, ((0, 0), (d_x, 0), (0, 0)),
                          mode='constant', constant_values=127)
    else:
        im_sized = im_sized[:, -d_x:, :]
    if (new_w + d_x) < net_w:
        im_sized = np.pad(im_sized, ((0, 0), (0, net_w - (new_w + d_x)), (0, 0)), mode='constant',
                          constant_values=127)

    if d_y > 0:
        im_sized = np.pad(im_sized, ((d_y, 0), (0, 0), (0, 0)),
                          mode='constant', constant_values=127)
    else:
        im_sized = im_sized[-d_y:, :, :]

    if (new_h + d_y) < net_h:
        im_sized = np.pad(im_sized, ((0, net_h - (new_h + d_y)), (0, 0), (0, 0)), mode='constant',
                          constant_values=127)

    return im_sized[:net_h, :net_w, :]
