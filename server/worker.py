from app import app
from celery import Celery
from flask_socketio import SocketIO
from firebase_config import FIREBASE_CONFIG
from fire_engine.fire import FireAlarm
from datetime import datetime
from PIL import Image
from common import random_name_generator
from db import Database

import pyrebase
import io
import base64
import re


celery = Celery(
    app.name, broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'])
database = Database()

fire_alarm = FireAlarm() if __name__ == 'worker' else None
firebase_app = pyrebase.initialize_app(FIREBASE_CONFIG)
firebase_storage = firebase_app.storage()


@celery.task(ignore_result=True)
def fire_alert(data, room):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Detecting fire...')
    with app.app_context():
        image_data = base64.b64decode(data)
        image = Image.open(io.BytesIO(image_data))
        result = fire_alarm.check_fire(image)
        socketio.emit('fire', {'fire': result}, room=room)
        if result:
            t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            socketio.emit(
                'log', {'log': '[{}] Fire warning'.format(t)})
            database.insert(
                'INSERT INTO log_text(camera_id, time, message) VALUES(?,?,?)', (int(room), t, '[{}] Fire warning'.format(t)))


@celery.task(ignore_result=True)
def save_image(data, room):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Saving image...')
    with app.app_context():
        t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        socketio.emit(
            'log', {'log': '[{}] Object is out of ROI. Saving image...'.format(t)}, room=room)
        database.insert(
            'INSERT INTO log_text(camera_id, time, message) VALUES(?,?,?)', (int(room), t, '[{}] Object is out of ROI. Saving image...'.format(t)))

    send_image = io.BytesIO(
        base64.b64decode(re.sub("data:image/jpeg;base64", '', data)))
    image_name = random_name_generator() + '.jpg'
    firebase_storage.child(
        "images/{}".format(image_name)).put(send_image)
    url = firebase_storage.child("images/{}".format(image_name)).get_url(None)
    t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    database.insert(
        'INSERT INTO log_image(url, time, camera_id) VALUES(?,?,?)', (url, t, int(room)))
