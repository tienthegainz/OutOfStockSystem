from app import app, socketio, db, jwt
from flask import jsonify, request
from PIL import Image
from datetime import datetime, timezone
from common import random_name_generator
from detect_engine.detector import Detector
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from tracker_engine.tracker import TrackerMulti
from worker import handle_missing_object, save_image_product
from model import *
from sqlalchemy import func
from flask_jwt_extended import create_access_token, verify_jwt_in_request, current_user, get_jwt, jwt_required
from functools import wraps

import base64
import io
import numpy as np
import re

# Global param
# detector = Detector()
# extractor = Extractor()
# searcher = Searcher()
extractor = None
searcher = None
detector = None
tracker = TrackerMulti()


######################## User API ########################

# Utilities
@jwt.user_identity_loader
def user_identity_lookup(user):
    # Convert object to JSON serializable format for token
    return user.username


@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_payload):
    identity = jwt_payload["sub"]
    return User.query.filter(User.username == identity).one_or_none()


@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    revoked_token = RevokedToken.query.filter(RevokedToken.jti == jti).first()
    if revoked_token is None:
        now = datetime.now(timezone.utc)
        revoked_token = RevokedToken(
            jti=jti, is_expired=True, is_logout=False, revoked_at=now)
        try:
            revoked_token.save_to_db()
        except Exception as e:
            print(e)
    return jsonify({'success': False, 'msg': 'Token has expired'}), 401


@jwt.revoked_token_loader
def my_revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'success': False, 'msg': 'Token has been revoked'}), 401


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = RevokedToken.query.filter_by(jti=jti).first()
    return token is not None


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_admin"]:
                return fn(*args, **kwargs)
            else:
                return jsonify({'success': False, 'msg': 'Admins only'}), 403

        return decorator

    return wrapper

# API


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.find_by_username(data['username'])
    if not user:
        return jsonify({'success': False, 'msg': 'User not existed'}), 400
    elif user.verify_hash(data['password']):
        access_token = create_access_token(
            identity=user, additional_claims={"is_admin": user.admin}
        )
        return jsonify({'success': True, 'access_token': access_token, 'user': user.to_dict()}), 200
    else:
        return jsonify({'success': False, 'msg': 'Wrong password'}), 400


@app.route('/register', methods=['POST'])
@admin_required()
def register():
    data = request.get_json()
    if User.find_by_username(data['username']):
        return jsonify({'success': False, 'msg': 'User already existed'}), 400
    else:
        user = User(username=data['username'],
                    password=User.generate_hash(data['password']))
        try:
            user.save_to_db()
            return jsonify({'success': True, 'user': user.to_dict()}), 200
        except:
            return jsonify({'success': False, 'msg': 'Something went wrong'}), 500


@app.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    name = current_user.username
    now = datetime.now(timezone.utc)
    revoked_token = RevokedToken(
        jti=jti, is_expired=False, is_logout=True, revoked_at=now)
    try:
        revoked_token.save_to_db()
        return jsonify({'success': True, 'msg': 'User {} logged out'.format(name)}), 200
    except:
        return jsonify({'success': False, 'msg': 'Something went wrong'}), 500


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    print(current_user)
    return jsonify({'success': True}), 200


@app.route("/admin", methods=["GET"])
@admin_required()
def admin():
    print(current_user)
    return jsonify({'success': True}), 200


######################## Products API ########################

# Utilities


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
            if product is not None:
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


def check_missing(products, camera_id):
    cp = CameraProduct.query.filter(
        CameraProduct.camera_id == camera_id).all()
    require_products = [r.to_dict() for r in cp]
    results = []
    for rp in require_products:
        quantity = 0
        name = None
        for product in products:
            if rp['product_id'] == product['id']:
                quantity = product['quantity']
                name = product['name']
        if rp['quantity'] > quantity:
            if name is None:
                product = Product.query.filter(
                    Product.id == rp['product_id']).first()
                if product is None:
                    name = '*Unknown object'
                else:
                    name = product.name

            results.append({'id': rp['product_id'], 'name': name,
                            'quantity': rp['quantity']-quantity})

    return results

# API


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
    missing = check_missing(count, room)
    if missing:
        handle_missing_object.delay(
            {'image': request_data['image'], 'missing': missing}, room)
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
    log.save_to_db()
    return jsonify({'success': True, 'info': info})


@app.route('/product', methods=['GET'])
@jwt_required()
def get_product():
    results = Product.query.all()
    return jsonify({'success': True, 'products': [r.to_dict_bulk() for r in results]})


@app.route('/product/<id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.filter(Product.id == id).first()
    indexes = [image.id for image in product.images]
    searcher.delete_products(indexes)
    product.delete_in_db()
    return jsonify({'success': True})


@app.route('/product', methods=['POST'])
@jwt_required()
def add_product():
    # TODO
    request_data = request.get_json()
    pil_images = []
    base64_images = []
    product = Product(name=request_data['name'], price=request_data['price'])
    product.save_to_db()
    # print('Product id: ', product.id)

    for image_str in request_data['images']:
        imageb64 = re.sub('^data:image/.+;base64,', '', image_str)
        image_data = base64.b64decode(imageb64)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        pil_images.append(image)
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
    camera_id = request.get_json()['id']
    camera = Camera.query.filter(Camera.id == camera_id).first()
    if camera is not None:
        camera.active = True
        camera.save_to_db()

        cameras = Camera.query.all()
        socketio.emit('camera_list', {'cameras': [
                      cam.to_dict() for cam in cameras if cam.active]}, broadcast=True)
    return jsonify({'success': True})


@app.route('/camera/active', methods=['GET'])
@jwt_required()
def get_active_camera():
    cameras = Camera.query.all()
    return jsonify({'success': True, 'cameras': [cam.to_dict() for cam in cameras if cam.active]})


@app.route('/camera/active/<id>', methods=['DELETE'])
def delete_active_camera(id):
    camera_id = int(id)
    camera = Camera.query.filter(Camera.id == camera_id).first()
    if camera is not None:
        camera.active = False
        camera.save_to_db()
        cameras = Camera.query.all()

        socketio.emit('camera_list', {'cameras': [
                      cam.to_dict() for cam in cameras if cam.active]}, broadcast=True)

    return jsonify({'success': True, 'deleted_cameras': camera.to_dict()})


@app.route('/camera', methods=['GET'])
@jwt_required()
def get_camera():
    results = Camera.query.all()
    # print(results)
    return jsonify({'success': True, 'cameras': [result.to_dict() for result in results]})


@app.route('/camera/product', methods=['GET'])
@jwt_required()
def get_camera_product():
    results = db.session.query(Camera, CameraProduct, Product)\
        .join(Camera, Camera.id == CameraProduct.camera_id)\
        .join(Product, Product.id == CameraProduct.product_id)\
        .all()
    if results:
        data = []
        for camera, info, product in results:
            new = True
            product_info = product.to_dict()
            product_info['quantity'] = info.quantity
            for i in range(len(data)):
                if camera.id == data[i]['id']:
                    data[i]['products'].append(product_info)
                    new = False
                    break
            if new:
                a = camera.to_dict()
                a['products'] = [product_info]
                data.append(a)

        return jsonify({'success': True, 'cameras': data})
    else:
        cameras = Camera.query.all()
        data = []
        for camera in cameras:
            c = camera.to_dict()
            c['products'] = []
            data.append(c)
        return jsonify({'success': True, 'cameras': data})


@app.route('/camera/product', methods=['POST'])
@jwt_required()
def add_camera_product():
    request_data = request.get_json()
    camera_product = CameraProduct.query.filter(CameraProduct.camera_id == request_data['camera_id'])\
        .filter(CameraProduct.product_id == request_data['product_id']).first()
    if camera_product is not None:
        camera_product.quantity += request_data['quantity']
        camera_product.save_to_db()
    else:
        camera_product = CameraProduct(camera_id=request_data['camera_id'],
                                       product_id=request_data['product_id'],
                                       quantity=request_data['quantity'])
        try:
            camera_product.save_to_db()
        except Exception as err:
            return jsonify({'success': False, 'error': err})

    return jsonify({'success': True, 'added': camera_product.to_dict()})


@app.route('/camera/<camera_id>/product/<product_id>', methods=['PUT'])
@jwt_required()
def change_product_quantity(camera_id, product_id):
    request_data = request.get_json()
    quantity = request_data['quantity'] if 'quantity' in request_data else None
    if quantity is None:
        return jsonify({'success': False, 'error': 'Product quantity not found'}), 400

    result = CameraProduct.query.filter(CameraProduct.camera_id == camera_id)\
        .filter(CameraProduct.product_id == product_id).first()
    if result is None:
        return jsonify({'success': False, 'error': 'Product not found'}), 400
    else:
        result.quantity = quantity
        result.save_to_db()
        return jsonify({'success': True, 'product': result.to_dict()})


@app.route('/camera/<camera_id>/product/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_camera_product(camera_id, product_id):
    result = CameraProduct.query.filter(CameraProduct.camera_id == camera_id)\
        .filter(CameraProduct.product_id == product_id).first()
    if result is None:
        return jsonify({'success': False, 'error': 'Product not found'}), 400
    else:
        result.delete_in_db()
        return jsonify({'success': True, 'deleted': result.to_dict()})

######################## Logger API ########################


@app.route('/log/text', methods=['POST'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def count_log_image_by_id(id):
    data = request.get_json()
    from_date = data['from']
    to_date = data['to']
    total = LogImage.query.filter(LogImage.camera_id == id).filter(
        LogImage.time.between(from_date, to_date)).count()
    # print(total)
    return jsonify({'success': True, 'total': total})


@app.route('/log/image/<id>', methods=['POST'])
@jwt_required()
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
