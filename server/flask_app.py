from db import Database, LogImageModel, ProductImageModel, ProductModel
from detect_engine.detector import Detector
from fire_engine.fire import FireAlarm
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from tracker_engine.tracker import Tracker, TrackerMulti
# from daemon import fire_alert
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from PIL import Image
from celery import Celery
from firebase_config import FIREBASE_CONFIG
import io
import traceback
import time
import numpy as np
import base64
import string
import random
import cv2
import pyrebase
import re
from datetime import datetime


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", message_queue='redis://')
# socketio = SocketIO(app, cors_allowed_origins="*")

celery = Celery(
    app.name, broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'])


extractor = None
searcher = None
database = Database()
detector = None
tracker = None
fire_alarm = FireAlarm()
firebase_app = pyrebase.initialize_app(FIREBASE_CONFIG)
firebase_storage = firebase_app.storage()

count = 0


def random_name_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def search_product(data):
    # Search products name by image
    try:
        products = []
        for prod in data:
            pil_prod = Image.fromarray(prod.astype('uint8'), 'RGB')
            feature = extractor.extract(pil_prod)
            index = searcher.query_products(feature)
            if index is not None:
                image_info = database.get(sql="SELECT * FROM product_image WHERE id = ?", ENTITY=ProductImageModel,
                                          value=(index, ), limit=1)
                print(image_info)
                product = database.get(sql="SELECT * FROM products WHERE id = ?", ENTITY=ProductModel,
                                       value=(image_info.product_id, ), limit=1)
                products.append(str(product.name))
            else:
                products.append(None)
        return products
    except Exception as e:
        traceback.print_exc()
    return None


def detect_search_object(image):
    # Detect candidate object => check what object it is
    data = detector.predict(image)

    if data['products']:
        products = search_product(data['products'])
        bboxes = data['bboxes']
        info = [{'id': random_name_generator(), 'bbox': bboxes[i]}
                for i in range(len(products)) if products[i] is not None]
        products = [product for product in products if product is not None]
        tracker.update(data['image'], info)
        draw_img = tracker.draw()
        result_image = Image.fromarray(draw_img.astype(np.uint8))
        img_byte = io.BytesIO()
        result_image.save(img_byte, format='jpeg')
        base64_image = base64.b64encode(
            img_byte.getvalue()).decode('utf-8')
        return base64_image, products, info
    else:
        img_byte = io.BytesIO()
        image.save(img_byte, format='jpeg')
        base64_image = base64.b64encode(
            img_byte.getvalue()).decode('utf-8')
        return base64_image, [], None


def track_image(data, info):
    image_data = base64.b64decode(data)
    image = Image.open(io.BytesIO(image_data))
    np_image = np.array(image)
    update_ok = False
    if info != None:
        update_ok = tracker.update(np_image, info)
    else:
        update_ok = tracker.update(np_image)
    draw_img = tracker.draw()
    if tracker.check_out_roi() or not update_ok:
        save_image.delay(data)

    result_image = Image.fromarray(draw_img.astype(np.uint8))
    img_byte = io.BytesIO()
    result_image.save(img_byte, format='jpeg')
    base64_image = base64.b64encode(
        img_byte.getvalue()).decode('utf-8')
    return base64_image


@celery.task(ignore_result=True)
def fire_alert(data):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Detecting fire...')
    with app.app_context():
        image_data = base64.b64decode(data)
        image = Image.open(io.BytesIO(image_data))
        result = fire_alarm.check_fire(image)
        socketio.emit('fire', {'fire': result})


@celery.task(ignore_result=True)
def save_image(data):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Saving image...')
    with app.app_context():
        socketio.emit('log', {'log': 'Object is out of ROI. Saving image...'})

    send_image = io.BytesIO(
        base64.b64decode(re.sub("data:image/jpeg;base64", '', data)))
    image_name = random_name_generator() + '.jpg'
    firebase_storage.child(
        "images/{}".format(image_name)).put(send_image)
    url = firebase_storage.child("images/{}".format(image_name)).get_url(None)
    t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    database.insert('INSERT INTO log_image(url, time) VALUES(?,?)', (url, t))


@socketio.on('camera')
def socket_camera(data):
    global count
    if count % 50 == 0:
        socketio.emit('ready', {'ready': True})
    try:
        count += 1
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data))

        if count % 50 == 0:
            print('Fire detection running ...')
            fire_alert.delay(data['image'])

        info = data['info'] if 'info' in data else None

        result_image = track_image(data['image'], info)

        socketio.emit('image', {'image': result_image}, broadcast=True)
    except Exception as err:
        print(err)


@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'hello', 'legit': detector.test()})


@app.route('/product/detect', methods=['POST'])
def watch_product():
    # signal FE to wait
    socketio.emit('ready', {'ready': False})
    # clear tracker
    tracker.clear_all_objects()
    # processing
    image_data = request.files['image'].read()
    image = Image.open(io.BytesIO(image_data))
    result_image, products, info = detect_search_object(image)

    socketio.emit('log',
                  {'log': 'Detected product: {}'.format(', '.join(products))},
                  broadcast=True)
    socketio.emit('image', {'image': result_image}, broadcast=True)

    return jsonify({'success': True, 'info': info})


@app.route('/product/log', methods=['GET'])
def get_all_image_log():
    images = database.get(
        "SELECT * FROM log_image ORDER BY id DESC", LogImageModel)
    json_images = [image.dict() for image in images]
    return jsonify({'success': True, 'data': json_images})


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port='5001', debug=True, use_reloader=False)
    del fire_alarm
    del firebase_app
    del firebase_storage
    detector = Detector()
    extractor = Extractor()
    searcher = Searcher()
    # tracker = Tracker()
    tracker = TrackerMulti()
    socketio.run(app, host='0.0.0.0', port='5001',
                 debug=True, use_reloader=False)
