from app import app, socketio, cameras
from flask import jsonify, request
from db import Database, LogImageModel, LogTextModel, ProductImageModel, ProductModel
from PIL import Image
from datetime import datetime
from common import random_name_generator
from detect_engine.detector import Detector
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from tracker_engine.tracker import TrackerMulti

import base64
import io
import numpy as np

# Global param
detector = Detector()
extractor = Extractor()
searcher = Searcher()
tracker = TrackerMulti()
database = Database()



######################## Utils ########################


def search_product(data):
    # Search products name by image
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

######################## Logger API ########################


@app.route('/log/text', methods=['POST'])
def get_all_log_text():
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else 5
    offset = (data['page'] - 1) * limit if 'page' in data else 0
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None
    texts = []
    if from_date is None or to_date is None:
        texts = database.get(
            "SELECT * FROM log_text ORDER BY id DESC LIMIT ? OFFSET ?", LogTextModel, value=(limit, offset))
    else:
        texts = database.get(
            "SELECT * FROM log_text WHERE time BETWEEN ? AND ? ORDER BY id DESC LIMIT ? OFFSET ?", LogTextModel, value=(from_date, to_date, limit, offset))
    json_texts = [text.dict()
                  for text in texts] if texts is not None else []
    return jsonify({'success': True, 'data': json_texts})


@app.route('/log/text/<id>', methods=['POST'])
def get_log_text_by_id(id):
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else None
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None
    texts = []
    if from_date is None or to_date is None:
        if limit is not None:
            texts = database.get(
                "SELECT * FROM log_text WHERE camera_id = ? ORDER BY id DESC LIMIT ?",
                LogTextModel, value=(id, limit))
    else:
        if limit is not None:
            texts = database.get(
                "SELECT * FROM log_text WHERE time BETWEEN ? AND ? AND camera_id = ? ORDER BY id DESC LIMIT ?",
                LogTextModel, value=(from_date, to_date, id, limit))
        else:
            texts = database.get(
                "SELECT * FROM log_text WHERE time BETWEEN ? AND ? AND camera_id = ? ORDER BY id DESC",
                LogTextModel, value=(from_date, to_date, id))
    json_texts = [text.dict()
                  for text in texts] if texts is not None else []
    return jsonify({'success': True, 'data': json_texts})


@app.route('/log/image', methods=['POST'])
def get_all_log_image():
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else 5
    offset = (data['page'] - 1) * limit if 'page' in data else 0
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None
    images = []
    if from_date is None or to_date is None:
        images = database.get(
            "SELECT * FROM log_image ORDER BY id DESC LIMIT ? OFFSET ?", LogImageModel, value=(limit, offset))
    else:
        images = database.get(
            "SELECT * FROM log_image WHERE time BETWEEN ? AND ? ORDER BY id DESC LIMIT ? OFFSET ?", LogImageModel, value=(from_date, to_date, limit, offset))
    json_images = [image.dict()
                   for image in images] if images is not None else []
    return jsonify({'success': True, 'data': json_images})


@app.route('/log/image/count/<id>', methods=['POST'])
def count_log_image_by_id(id):
    data = request.get_json()
    from_date = data['from']
    to_date = data['to']
    sql = "SELECT COUNT(*) FROM log_image WHERE camera_id = ? AND time BETWEEN ? AND ?"
    cur = database.create_cursor()
    cur.execute(sql, (id, from_date, to_date))
    result = cur.fetchone()
    total = result[0]
    return jsonify({'success': True, 'total': total})


@app.route('/log/image/<id>', methods=['POST'])
def get_log_image_by_id(id):
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else 5
    offset = (data['page'] - 1) * limit if 'page' in data else 0
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None
    images = []
    if from_date is None or to_date is None:
        images = database.get(
            "SELECT * FROM log_image WHERE camera_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
            LogImageModel, value=(id, limit, offset))
    else:
        images = database.get(
            "SELECT * FROM log_image WHERE time BETWEEN ? AND ? AND camera_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
            LogImageModel, value=(from_date, to_date, id, limit, offset))
    json_images = [image.dict()
                   for image in images] if images is not None else []
    return jsonify({'success': True, 'data': json_images})


######################## Test API ########################


@app.route('/room/test', methods=['POST'])
def test_room():
    data = request.get_json()
    room = data['id']
    print(type(room))
    socketio.emit('log', {'log': 'Send data to client'},
                  room=room, broadcast=True)
    return jsonify({'success': True})


@app.route('/param/test/<id>', methods=['GET'])
def test_param(id=None):
    limit = request.args.get('limit', default=5, type=int)
    start = request.args.get('limit', default=1, type=int)
    return jsonify({'success': True, 'result': id, 'start': start, 'limit': limit})
