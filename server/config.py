DATABASE = {
    'path': '/home/tienhv/GR/OutOfStockSystem/server/dummy.db',
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
    'weight': '/home/tienhv/GR/OutOfStockSystem/server/detect_engine/checkpoint_18.pth'
}
