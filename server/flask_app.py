from db import Database, LogImageModel, ProductImageModel, ProductModel
from detect_engine.detector import Detector
from fire_engine.fire import FireAlarm
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from tracker_engine.tracker import TrackerMulti
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, join_room, leave_room, emit, send
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
cameras = []

######################## Utility function ########################


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
                products.append(product)
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
        info = [{'id': random_name_generator(), 'bbox': bboxes[i], 'product_id': products[i].id}
                for i in range(len(products)) if products[i] is not None]
        # track image
        tracker.update(data['image'], info)
        # draw object
        draw_img = tracker.draw()
        result_image = Image.fromarray(draw_img.astype(np.uint8))
        img_byte = io.BytesIO()
        result_image.save(img_byte, format='jpeg')
        base64_image = base64.b64encode(
            img_byte.getvalue()).decode('utf-8')
        # count object
        c = count_object(products)
        return base64_image, info, c
    else:
        img_byte = io.BytesIO()
        image.save(img_byte, format='jpeg')
        base64_image = base64.b64encode(
            img_byte.getvalue()).decode('utf-8')
        return base64_image, [], []


def count_object(products):
    result = []
    pid = []
    for product in products:
        if product.id not in pid:
            pid.append(product.id)
            result.append(
                {'id': product.id, 'name': product.name, 'quantity': 1})
        else:
            a = pid.index(product.id)
            result[a]['quantity'] += 1
    return result


def track_image(data, info, room):
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
        save_image.delay(data, room)

    result_image = Image.fromarray(draw_img.astype(np.uint8))
    img_byte = io.BytesIO()
    result_image.save(img_byte, format='jpeg')
    base64_image = base64.b64encode(
        img_byte.getvalue()).decode('utf-8')
    return base64_image

######################## Celery background task ########################


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
        if result:
            t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            socketio.emit(
                'log', {'log': '[{}] Fire warning'.format(t)})


@celery.task(ignore_result=True)
def save_image(data, room):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Saving image...')
    with app.app_context():
        t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        socketio.emit(
            'log', {'log': '[{}] Object is out of ROI. Saving image...'.format(t)}, room=room)

    # send_image = io.BytesIO(
    #     base64.b64decode(re.sub("data:image/jpeg;base64", '', data)))
    # image_name = random_name_generator() + '.jpg'
    # firebase_storage.child(
    #     "images/{}".format(image_name)).put(send_image)
    # url = firebase_storage.child("images/{}".format(image_name)).get_url(None)
    # t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # database.insert('INSERT INTO log_image(url, time) VALUES(?,?)', (url, t))


######################## Socket handler ########################
@socketio.on('camera')
def on_send_image(data):
    global count
    room = int(data['id'])
    socketio.emit('ready', {'ready': True}, room=room)
    try:
        count += 1

        if count % 50 == 0:
            print('Fire detection running ...')
            fire_alert.delay(data['image'])

        info = data['info'] if 'info' in data else None

        result_image = track_image(data['image'], info, room)
        print('Sending data to room {}'.format(room))
        socketio.emit('image', {'image': result_image},
                      room=room, broadcast=True)
    except Exception as err:
        print(err)


@socketio.on('join')
def on_join(data):
    room = data['id']
    join_room(room)
    print('Connected to room: {}'.format(room))


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    print('Left room: {}'.format(room))

######################## Products API ########################


@app.route('/product/detect', methods=['POST'])
def watch_product():
    request_data = request.get_json()
    image_data = base64.b64decode(request_data['image'])
    image = Image.open(io.BytesIO(image_data))
    room = int(request_data['id'])
    # signal FE to wait
    socketio.emit('ready', {'ready': False}, room=room, broadcast=True)
    # clear tracker
    tracker.clear_all_objects()
    # processing
    result_image, info, count = detect_search_object(image)
    # logging
    logs = ['{}: {}'.format(c['name'], c['quantity']) for c in count]
    t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    socketio.emit('log',
                  {'log': '[{}] Detected product: {}'.format(
                      t, ', '.join(logs))},
                  room=room,
                  broadcast=True)
    socketio.emit('image', {'image': result_image}, room=room, broadcast=True)

    return jsonify({'success': True, 'info': info})


@app.route('/product/log', methods=['GET'])
def get_all_image_log():
    images = database.get(
        "SELECT * FROM log_image ORDER BY id DESC", LogImageModel)
    json_images = [image.dict() for image in images]
    return jsonify({'success': True, 'data': json_images})

######################## Camera API ########################


@app.route('/camera', methods=['POST'])
def add_camera():
    global cameras
    camera_info = request.get_json()
    # print(camera_info)
    duplicate = False
    for camera in cameras:
        if camera_info['id'] == camera['id']:
            duplicate = True
            break
    if not duplicate:
        print('Sending...')
        cameras.append(camera_info)
        socketio.emit('camera_list', {'cameras': cameras}, broadcast=True)
    return jsonify({'success': True})


@app.route('/camera', methods=['GET'])
def get_camera():
    global cameras
    return jsonify({'success': True, 'cameras': cameras})

######################## User API ########################

######################## Test API ########################


@app.route('/room/test', methods=['POST'])
def test_room():
    data = request.get_json()
    room = data['id']
    print(type(room))
    socketio.emit('log', {'log': 'Send data to client'},
                  room=room, broadcast=True)
    return jsonify({'success': True})

##########################################################


if __name__ == '__main__':
    del fire_alarm
    del firebase_app
    del firebase_storage
    detector = Detector()
    extractor = Extractor()
    searcher = Searcher()
    tracker = TrackerMulti()
    socketio.run(app, host='0.0.0.0', port='5001',
                 debug=True, use_reloader=False)
