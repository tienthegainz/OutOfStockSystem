from app import db
from config import STORAGE
import os

if __name__ == '__main__':
    from model import *
    db.drop_all()
    db.create_all()
    camera = Camera(name='Raspberry Pi 3')
    db.session.add(camera)
    db.session.commit()
    print(camera.id)
    ann_path = os.path.join(STORAGE['path'], STORAGE['ann'], 'index.bin')
    os.remove(ann_path)
    print('Removed ', ann_path)
