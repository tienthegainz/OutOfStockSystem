from dotenv import dotenv_values, load_dotenv
import os

load_dotenv()


DATABASE = {
    'path': os.getenv('DATABASE_PATH'),
    'type': 'sqlite3'
}

STORAGE = {
    'path': os.getenv('STORAGE_PATH'),
    'type': 'local',
    'ann': 'ann'
}

SEARCHER = {
    'dim': 2048,
    'space': 'l2',
    'threshold': 4
}

DETECTOR = {
    'num_classes': 4,
    'overlap_thres': 0.7,
    'weight': os.getenv('DETECTOR_WEIGHT')
}

TRACKER = {
    # x, y, h, w
    'roi': [144, 250, 432, 330],
    'no_bbox_thres': 5,
}

FIRE_MODEL = {
    'num_classes': 3,
    'weight': os.getenv('FIRE_MODEL_WEIGHT')
}

EXTRACTOR = {
    'weight': os.getenv('EXTRACTOR_WEIGHT')
}

SAMPLE_IMAGE = os.getenv('SAMPLE_IMAGE')
