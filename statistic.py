"""
statistic module
"""
import os
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from prettytable import PrettyTable
from utils.utils import compute_overlap

ALL_CLASSES = ["balo", "balo_diutre", "bantreem", "binh_sua", "cautruot", "coc_sua", "ghe_an",
               "ghe_bap_benh", "ghe_ngoi_oto", "ghedualung_treem", "ke", "noi", "person", "phao",
               "quay_cui", "tham",
               "thanh_chan_cau_thang", "thanh_chan_giuong", "xe_babanh", "xe_choichan", "xe_day",
               "xe_tapdi", "xichdu",
               "yem"]


def read_ann(ann_path):
    """
    read xml file
    """
    try:
        tree = ET.parse(ann_path)
    except Exception as ex:
        print(ex)
        print('Ignore this bad annotation: ', ann_path)

    bboxes = []
    for elem in tree.iter():
        if 'object' in elem.tag or 'part' in elem.tag:
            obj = {}
            for attr in list(elem):
                if 'name' in attr.tag:
                    if attr.text == "adult" or attr.text == "baby":
                        obj["name"] = "person"
                    else:
                        obj['name'] = attr.text

                if 'bndbox' in attr.tag:
                    for dim in list(attr):
                        if 'xmin' in dim.tag:
                            obj['xmin'] = int(round(float(dim.text)))
                        if 'ymin' in dim.tag:
                            obj['ymin'] = int(round(float(dim.text)))
                        if 'xmax' in dim.tag:
                            obj['xmax'] = int(round(float(dim.text)))
                        if 'ymax' in dim.tag:
                            obj['ymax'] = int(round(float(dim.text)))
                            if obj["name"] in ALL_CLASSES:
                                bboxes.append(obj)
    return bboxes


def generate_not_detected(pred_folder, image_folder, ann_folder):
    """
    generate case object of trained object not detected by the model
    """
    source_folder = image_folder[:image_folder.rindex('/')]
    not_detected_folder = os.path.join(source_folder, 'not_detected')
    misclassified_folder = os.path.join(source_folder, 'misclassified')
    log_path = source_folder + '/log.txt'
    with open(log_path, 'w') as file:
        if not os.path.exists(not_detected_folder):
            os.makedirs(not_detected_folder)
        if not os.path.exists(misclassified_folder):
            os.makedirs(misclassified_folder)

        # intialize variable
        not_detected_rs = {}
        all_instance = {}
        for cls in ALL_CLASSES:
            not_detected_rs[cls] = 0
            all_instance[cls] = 0
        misclassified_rs = {}
        for cls in ALL_CLASSES:
            for cls1 in ALL_CLASSES:
                misclassified_rs[cls, cls1] = 0

        for image in os.listdir(image_folder):
            if image.lower().endswith(('.jpg', '.png', '.jpeg')):
                image_path = os.path.join(image_folder, image)
                ann_name = os.path.splitext(image)[0] + '.xml'
                pred_xml_path = os.path.join(pred_folder, ann_name)
                if os.path.exists(pred_xml_path):
                    list_boxes = read_ann(pred_xml_path)
                else:
                    list_boxes = []
                pred_boxes_array = np.array(
                    [[b["xmin"], b["ymin"], b["xmax"], b["ymax"]] for b in list_boxes])
                pred_boxes_label = np.array([b["name"] for b in list_boxes])
                ann_path = os.path.join(ann_folder, ann_name)
                if not os.path.exists(ann_path):
                    continue
                gt_boxes = read_ann(ann_path)
                gt_boxes_array = np.array(
                    [[b["xmin"], b["ymin"], b["xmax"], b["ymax"]] for b in gt_boxes])
                gt_boxes_label = np.array([b["name"] for b in gt_boxes])
                if len(list_boxes) == 0:
                    for label in gt_boxes_label:
                        not_detected_rs[label] += 1
                    continue
                if len(gt_boxes) == 0:
                    continue
                iou = compute_overlap(gt_boxes_array, pred_boxes_array)
                used_index = []
                for i, gt_box in enumerate(gt_boxes_array):
                    sort_index = np.argsort(-iou[i])
                    gt_label = gt_boxes_label[i]
                    all_instance[gt_label] += 1
                    for index in sort_index:
                        if iou[i][index] < 0.5:
                            file.write(image + ' not found ' + gt_label + '\n')
                            not_detected_rs[gt_label] += 1
                            shutil.copy(image_path, not_detected_folder)
                            break
                        if index not in used_index:
                            pred_label = pred_boxes_label[index]
                            used_index.append(index)
                            if pred_label != gt_label:
                                file.write(
                                    image + ' misclasified from ' + gt_label + ' to ' +
                                    pred_label + '\n')
                                misclassified_rs[gt_label, pred_label] += 1
                                shutil.copy(image_path, misclassified_folder)
                            break

    # print result
    table = PrettyTable()
    table.field_names = ["class", 'all instances', 'Not detected', 'Not detected rate']
    for key in all_instance:
        table.add_row(
            [key, all_instance[key], not_detected_rs[key],
             round(100 * not_detected_rs[key] / all_instance[key], 2)])
    print(table)

    print('Misclassified statistic')

    table2 = PrettyTable()
    table2.field_names = ["True class", "Pred class", "Wrong detected time"]
    for k in sorted(misclassified_rs, key=misclassified_rs.get, reverse=True):
        if misclassified_rs[k] > 0:
            table2.add_row([k[0], k[1], misclassified_rs[k]])
    print(table2)


if __name__ == '__main__':
    PRED_FOLDER = 'all_data/ghe_an_800/ghe_an_800_xml'
    IMAGE_FOLDER = 'all_data/ghe_an_800/ghe_an_800_output'
    GT_FOLDER = 'all_data/ghe_an_800/ghe_an_800_gt'
    generate_not_detected(PRED_FOLDER, IMAGE_FOLDER, GT_FOLDER)
