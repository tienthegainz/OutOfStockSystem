
DATABASE = {
    'path': '/home/tienhv/GR/OutOfStockSystem/server/dev.db',
    'type': 'sqlite3'
}

STORAGE = {
    'path': '/home/tienhv/GR/OutOfStockSystem/server/storage',
    'type': 'local',
    'image': 'image',
    'ann': 'ann'
}

SEARCHER = {
    'dim': 2048,
    'space': 'l2',
    'threshold': 4
}

DETECTOR = {
    'num_classes': 3,
    'overlap_thres': 0.7,
    'weight': '/home/tienhv/GR/OutOfStockSystem/server/detect_engine/checkpoint_18.pth'
}

TRACKER = {
    # x, y, h, w
    'roi': [144, 250, 432, 330],
    'no_bbox_thres': 5,
}
