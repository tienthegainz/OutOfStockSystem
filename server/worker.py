from app import app, db
from model import *
from celery import Celery
from flask_socketio import SocketIO
from fire_engine.fire import FireAlarm
from datetime import datetime
from PIL import Image
from common import random_name_generator

import pyrebase
import io
import base64
import re
import os
import config

FIREBASE_CONFIG = {
    "apiKey": os.getenv('FIREBASE_API_KEY'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    "appId": os.getenv('FIREBASE_APP_ID'),
    "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID')
}


celery = Celery(
    app.name, broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'])

fire_alarm = FireAlarm() if not (
    os.environ.get('NO_FIRENET') == 'true') else None
firebase_app = pyrebase.initialize_app(FIREBASE_CONFIG)
firebase_storage = firebase_app.storage()


@celery.task(ignore_result=True)
def fire_alert(data, room):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    image_data = base64.b64decode(data)
    image = Image.open(io.BytesIO(image_data)).convert('RGB')
    result = fire_alarm.check_fire(image)
    print('Detecting fire.... Result: {}'.format(result))
    with app.app_context():
        if result:
            # Log to UI
            socketio.emit('fire', {'fire': result}, room=room)
            t = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            message = '[{}] WARNING There may be fire. Please check'.format(t)
            socketio.emit(
                'log', {'log': message})
            # Notification
            camera = Camera.query.filter(Camera.id == room).first()
            socketio.emit('noti', {
                'title': camera.name,
                'message': message
            }, broadcast=True)
            # Save log to DB
            log = LogText(message=message, time=t, camera_id=room)
            log.save_to_db()

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
def handle_out_of_roi(data, room):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Saving image and send log ...')
    t = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with app.app_context():
        # Log to UI
        message = '[{}] Object is out of ROI. Saving image...'.format(t)
        socketio.emit('log', {'log': message}, room=room)
        log = LogText(message=message, time=t, camera_id=room)
        db.session.add(log)
        # Notification
        camera = Camera.query.filter(Camera.id == room).first()
        socketio.emit('noti', {
            'title': camera.name,
            'message': message
        }, broadcast=True)
        # Save image to DB
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
        # Log to UI
        logs = ['{}: {}'.format(c['name'], c['quantity'])
                for c in data['missing']]
        message = '[{}] WARNING: May be missing: {}. Please check. Saving image...'.format(
            t, ', '.join(logs))
        socketio.emit('log', {'log': message}, room=room)
        # Notification
        camera = Camera.query.filter(Camera.id == room).first()
        socketio.emit('noti', {
            'title': camera.name,
            'message': message
        }, broadcast=True)
        # Logging to db
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
def save_image_product(data, product_id, product_index):
    print('Saving image products ...')
    for i in range(len(data)):
        image = data[i]
        image_name = random_name_generator() + '.jpg'
        send_image = io.BytesIO(
            base64.b64decode(image))
        firebase_storage.child(
            "products/{}/{}".format(product_id, image_name)).put(send_image)
        url = firebase_storage.child(
            "products/{}/{}".format(product_id, image_name)).get_url(None)
        image = ProductImage(url=url, product_id=product_id,
                             ann_id=product_index[i])
        db.session.add(image)
    db.session.commit()
