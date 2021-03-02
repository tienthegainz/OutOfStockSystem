from app import app, db
from model import *
from celery import Celery
from flask_socketio import SocketIO
from firebase_config import FIREBASE_CONFIG
from fire_engine.fire import FireAlarm
from datetime import datetime
from PIL import Image
from common import random_name_generator

import pyrebase
import io
import base64
import re


celery = Celery(
    app.name, broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'])

# fire_alarm = FireAlarm()
fire_alarm = None
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
            t = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            message = '[{}] WARNING There may be fire. Please check'.format(t)
            socketio.emit(
                'log', {'log': message})
            log = LogText(message=message, time=t, camera_id=room)
            log.save_to_db()


@celery.task(ignore_result=True)
def handle_out_of_roi(data, room):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Saving image and send log ...')
    t = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with app.app_context():
        # Log
        message = '[{}] Object is out of ROI. Saving image...'.format(t)
        socketio.emit('log', {'log': message}, room=room)
        log = LogText(message=message, time=t, camera_id=room)
        db.session.add(log)
        # Image
        send_image = io.BytesIO(
            base64.b64decode(re.sub("data:image/jpeg;base64", '', data)))
        image_name = random_name_generator() + '.jpg'
        firebase_storage.child(
            "images/{}".format(image_name)).put(send_image)
        url = firebase_storage.child(
            "images/{}".format(image_name)).get_url(None)

        image = LogImage(url=url, time=t, camera_id=room)
        db.session.add(image)
        db.session.commit()


@celery.task(ignore_result=True)
def handle_missing_object(data, room):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Saving image and send log ...')
    t = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with app.app_context():
        # Log
        logs = ['{}: {}'.format(c['name'], c['quantity'])
                for c in data['missing']]
        message = '[{}] WARNING: May be missing: {}. Please check. Saving image...'.format(
            t, ', '.join(logs))
        socketio.emit('log', {'log': message}, room=room)
        log = LogText(message=message, time=t, camera_id=room)
        db.session.add(log)
        # Image
        send_image = io.BytesIO(
            base64.b64decode(re.sub("data:image/jpeg;base64", '', data['image'])))
        image_name = random_name_generator() + '.jpg'
        firebase_storage.child(
            "images/{}".format(image_name)).put(send_image)
        url = firebase_storage.child(
            "images/{}".format(image_name)).get_url(None)

        image = LogImage(url=url, time=t, camera_id=room)
        db.session.add(image)
        db.session.commit()


@celery.task(ignore_result=True)
def save_image_product(data, product_id):
    print('Saving image products ...')
    for image in data:
        image_name = random_name_generator() + '.jpg'
        send_image = io.BytesIO(
            base64.b64decode(image))
        firebase_storage.child(
            "products/{}/{}".format(product_id, image_name)).put(send_image)
        url = firebase_storage.child(
            "products/{}/{}".format(product_id, image_name)).get_url(None)
        image = ProductImage(url=url, product_id=product_id)
        db.session.add(image)
    db.session.commit()
