from app import app, socketio, cameras, db
from flask import jsonify, request
from PIL import Image
from datetime import datetime
from common import random_name_generator
from detect_engine.detector import Detector
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from tracker_engine.tracker import TrackerMulti
from worker import save_image_product
from model import *
from sqlalchemy import func

import base64
import io
import numpy as np
import re

# Global param
detector = Detector()
extractor = Extractor()
searcher = Searcher()
# extractor = None
# searcher = None
# detector = None
tracker = TrackerMulti()


######################## Utils ########################


def search_product(data):
    # Search products name by image
    products = []
    for prod in data:
        pil_prod = Image.fromarray(prod.astype('uint8'), 'RGB')
        feature = extractor.extract(pil_prod)
        index = searcher.query_products(feature)
        # print('Search with index: ', index)
        if index is not None:
            product = Product.query.join(ProductImage).filter(
                Product.id == ProductImage.product_id).filter(ProductImage.id == index).first()
            products.append(product)
    return products


def detect_search_object(image):
    # Detect candidate object => check what object it is
    data = detector.predict(image)
    if data['products']:
        products = search_product(data['products'])
        bboxes = data['bboxes']
        info = [{'id': random_name_generator(), 'bbox': bboxes[i], 'product_id': products[i].id}
                for i in range(len(products))]
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
    t = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    if logs:
        message = '[{}] Detected product: {}'.format(t, ', '.join(logs))
    else:
        message = '[{}] No object detected'.format(t)
    socketio.emit('log',
                  {'log': message},
                  room=room,
                  broadcast=True)
    socketio.emit('image', {'image': result_image}, room=room, broadcast=True)
    # Add log to db
    log = LogText(message=message, time=t, camera_id=room)
    db.session.add(log)
    db.session.commit()
    return jsonify({'success': True, 'info': info})


@app.route('/product', methods=['GET'])
def get_product():
    results = Product.query.all()
    return jsonify({'success': True, 'products': [r.to_dict() for r in results]})


@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.filter(Product.id == id).first()
    image_ids = [image.id for image in product.images]
    indexes = np.array(image_ids)
    searcher.delete_products(indexes)
    return jsonify({'success': True})


@app.route('/product', methods=['POST'])
def add_product():
    # TODO
    request_data = request.get_json()
    pil_images = []
    base64_images = []
    product = Product(name=request_data['name'], price=request_data['price'])
    db.session.add(product)
    db.session.commit()
    # print('Product id: ', product.id)

    for image_str in request_data['images']:
        imageb64 = re.sub('^data:image/.+;base64,', '', image_str)
        image_data = base64.b64decode(imageb64)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        # pil_images.append(image)
        base64_images.append(imageb64)
        # image.show()

    features = extractor.extract_many(pil_images)
    product_qty = features.shape[0]
    # Get max_id to make index
    max_product_image_id = db.session.query(func.max(ProductImage.id)).scalar()
    if max_product_image_id is None:
        max_product_image_id = 0
    # print('Max image ID: ', max_product_image_id)
    product_index = np.arange(max_product_image_id+1,
                              max_product_image_id+1+product_qty)
    # print('Idx: ', product_index)
    # ##########################

    save_image_product.delay(base64_images, product.id)
    searcher.add_products(features, product_index)
    searcher.save_graph()

    return jsonify({'success': True})

######################## Camera API ########################


@app.route('/camera/active', methods=['POST'])
def add_active_camera():
    global cameras
    camera_id = request.get_json()['id']
    duplicate = False
    for camera in cameras:
        if camera_id == camera['id']:
            duplicate = True
            break
    if not duplicate:
        camera = Camera.query.filter(Camera.id == camera_id).first()
        cameras.append(camera.to_dict())
        socketio.emit('camera_list', {'cameras': cameras}, broadcast=True)
    return jsonify({'success': True})


@app.route('/camera/active', methods=['GET'])
def get_active_camera():
    global cameras
    return jsonify({'success': True, 'cameras': cameras})


@app.route('/camera/active/<id>', methods=['DELETE'])
def delete_active_camera(id):
    global cameras
    cam_id = int(id)
    cameras = [cam for cam in cameras if cam['id'] != cam_id]
    socketio.emit('camera_list', {'cameras': cameras}, broadcast=True)
    return jsonify({'success': True, 'deleted_cameras': cameras})


@app.route('/camera', methods=['GET'])
def get_camera():
    results = Camera.query.all()
    # print(results)
    return jsonify({'success': True, 'cameras': [result.to_dict() for result in results]})

######################## User API ########################

######################## Logger API ########################


@app.route('/log/text', methods=['POST'])
def get_all_log_text():
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else 5
    offset = (data['page'] - 1) * limit if 'page' in data else 0
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None

    if from_date is not None and to_date is not None:
        query = LogText.query.filter(LogText.time.between(from_date, to_date)).order_by(
            LogText.id.desc()).limit(limit).offset(offset)
    else:
        query = LogText.query.order_by(
            LogText.id.desc()).limit(limit).offset(offset)
    results = query.all()
    texts = [r.to_dict() for r in results]
    return jsonify({'success': True, 'data': texts})


@app.route('/log/text/<id>', methods=['POST'])
def get_log_text_by_id(id):
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else 5
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None

    if from_date is None or to_date is None:
        if limit is not None:
            query = LogText.query.filter(LogText.camera_id == id).order_by(
                LogText.id.desc()).limit(limit)
        else:
            return jsonify({'success': False, 'message': 'No log limit on No-Date request'})
    else:
        if limit is not None:
            query = LogText.query.filter(LogText.camera_id == id).filter(
                LogText.time.between(from_date, to_date)).order_by(LogText.id.desc()).limit(limit)
        else:
            query = LogText.query.filter(LogText.camera_id == id).filter(
                LogText.time.between(from_date, to_date)).order_by(LogText.id.desc())

    results = query.all()
    # print(results)
    texts = [r.to_dict() for r in results]
    return jsonify({'success': True, 'data': texts})


@app.route('/log/image', methods=['POST'])
def get_all_log_image():
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else 5
    offset = (data['page'] - 1) * limit if 'page' in data else 0
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None

    if from_date is not None and to_date is not None:
        query = LogImage.query.filter(LogImage.time.between(from_date, to_date)).order_by(
            LogImage.id.desc()).limit(limit).offset(offset)
    else:
        query = LogImage.query.order_by(
            LogImage.id.desc()).limit(limit).offset(offset)
    results = query.all()
    images = [r.to_dict() for r in results]
    return jsonify({'success': True, 'data': images})


@app.route('/log/image/count/<id>', methods=['POST'])
def count_log_image_by_id(id):
    data = request.get_json()
    from_date = data['from']
    to_date = data['to']
    total = LogImage.query.filter(LogImage.camera_id == id).filter(
        LogImage.time.between(from_date, to_date)).count()
    # print(total)
    return jsonify({'success': True, 'total': total})


@app.route('/log/image/<id>', methods=['POST'])
def get_log_image_by_id(id):
    data = request.get_json()
    limit = data['limit'] if 'limit' in data else 5
    offset = (data['page'] - 1) * limit if 'page' in data else 0
    from_date = data['from'] if 'from' in data else None
    to_date = data['to'] if 'to' in data else None

    if from_date is None or to_date is None:
        query = LogImage.query.filter(LogImage.camera_id == id).order_by(
            LogImage.id.desc()).limit(limit).offset(offset)
    else:
        query = LogImage.query.filter(LogImage.camera_id == id).filter(LogImage.time.between(from_date, to_date)).order_by(
            LogImage.id.desc()).limit(limit).offset(offset)
    results = query.all()
    # print(results)
    images = [r.to_dict() for r in results]
    return jsonify({'success': True, 'data': images})
