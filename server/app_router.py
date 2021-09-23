from app import app, socketio, db, jwt
from flask import jsonify, request
from PIL import Image
from datetime import datetime, timezone
from common import camera_protected_api, random_name_generator
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
detector = Detector()
extractor = Extractor()
searcher = Searcher()
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


@app.route("/user", methods=["GET"])
@admin_required()
def get_user():
    try:
        results = User.query.all()
        return jsonify({'success': True, 'users': [r.to_dict() for r in results]})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route("/user/<id>", methods=["PUT"])
@admin_required()
def change_user(id):
    try:
        request_data = request.get_json()
        user = User.query.filter(User.id == id).first()
        if user:
            if 'password' in request_data:
                user.password = User.generate_hash(request_data['password'])
            if 'admin' in request_data:
                user.admin = request_data['admin']
            user.save_to_db()
            return jsonify({'success': True, 'user': user.to_dict()}), 200
        else:
            return jsonify({'success': False, 'msg': 'User not found'}), 400
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route("/user/<id>", methods=["DELETE"])
@admin_required()
def delete_user(id):
    try:
        user = User.query.filter(User.id == id).first()
        if user:
            user.delete_in_db()
            return jsonify({'success': True, 'user': user.to_dict()}), 200
        else:
            return jsonify({'success': False, 'msg': 'User not found'}), 400
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


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
                Product.id == ProductImage.product_id).filter(ProductImage.ann_id == index).first()
            if product is not None:
                products.append(product)
        else:
            products.append(None)
    return products


def detect_search_object(image, camera_id):
    # Detect candidate object => check what object it is
    data = detector.predict(image)
    if data['products']:
        products = search_product(data['products'])
        bboxes = data['bboxes']

        cam = Camera.query.filter(
        Camera.id == camera_id).first()
        product_list = [x.product_id for x in cam.products]
        info = []

        for i in range(len(products)):
            if products[i] is not None:
                if products[i].id in product_list:
                    info.append({
                        'id': random_name_generator(), 
                        'bbox': bboxes[i], 
                        'product_id': products[i].id
                    })

        # track image
        tracker.update(data['image'], info, True)
        # draw object
        draw_img = tracker.draw()
        result_image = Image.fromarray(draw_img.astype(np.uint8))
        img_byte = io.BytesIO()
        result_image.save(img_byte, format='jpeg')
        base64_image = base64.b64encode(
            img_byte.getvalue()).decode('utf-8')
        # count object
        c = count_object(products, product_list)
        return base64_image, info, c
    else:
        img_byte = io.BytesIO()
        image.save(img_byte, format='jpeg')
        base64_image = base64.b64encode(
            img_byte.getvalue()).decode('utf-8')
        return base64_image, [], []


def count_object(products, product_list):
    result = []
    pid = []
    for product in products:
        if product is not None:
            if product.id not in pid and product.id in product_list:
                pid.append(product.id)
                result.append(
                    {'id': product.id, 'name': product.name, 'quantity': 1})
            elif product.id in product_list:
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
    try:
        # Pause tracker
        tracker.pause()
        request_data = request.get_json()
        image_data = base64.b64decode(request_data['image'])
        image = Image.open(io.BytesIO(image_data))
        room = int(request_data['id'])
        # signal FE to wait
        socketio.emit('ready', {'ready': False}, room=room, broadcast=True)
        # clear tracker
        tracker.clear_all_objects()
        # processing
        result_image, info, count = detect_search_object(image, room)
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
        socketio.emit('image', {'image': result_image},
                      room=room, broadcast=True)
        # Unpause tracker
        tracker.unpause()
        # Add log to db
        log = LogText(message=message, time=t, camera_id=room)
        log.save_to_db()
        return jsonify({'success': True, 'info': info})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/product', methods=['GET'])
@jwt_required()
def get_product():
    try:
        results = Product.query.all()
        return jsonify({'success': True, 'products': [r.to_dict_bulk() for r in results]})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/product/<id>', methods=['PUT'])
@jwt_required()
def change_product(id):
    try:
        request_data = request.get_json()
        product = Product.query.filter(Product.id == id).first()
        if not product:
            return jsonify({'success': False, 'msg': 'Product not found'}), 400
        if 'name' in request_data:
            product.name = request_data['name']
        if 'price' in request_data:
            product.price = request_data['price']
        product.save_to_db()
        return jsonify({'success': True, 'product': product.to_dict()}), 200
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/product/<id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    try:
        product = Product.query.filter(Product.id == id).first()
        indexes = [image.id for image in product.images]
        searcher.delete_products(indexes)
        product.delete_in_db()
        return jsonify({'success': True})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/product', methods=['POST'])
@jwt_required()
def add_product():
    try:
        request_data = request.get_json()
        pil_images = []
        base64_images = []

        # Check for image legit
        for image_str in request_data['images']:
            imageb64 = re.sub('^data:image/.+;base64,', '', image_str)
            image_data = base64.b64decode(imageb64)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            pil_images.append(image)
            base64_images.append(imageb64)

        product = Product(
            name=request_data['name'], price=request_data['price'])
        product.save_to_db()

        # Get features from images
        features = extractor.extract_many(pil_images)
        product_qty = features.shape[0]
        # Get max_id to make index
        max_product_image_id = searcher.max_index
        product_index = np.arange(max_product_image_id,
                                  max_product_image_id+product_qty)
        product_index_list = list(range(max_product_image_id,
                                        max_product_image_id+product_qty))
        save_image_product.delay(base64_images, product.id, product_index_list)
        searcher.add_products(features, product_index)
        searcher.save_graph()

        return jsonify({'success': True, 'product': product.to_dict()})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


######################## Camera API ########################


@app.route('/camera/active', methods=['POST'])
def add_active_camera():
    try:
        data = request.get_json()
        camera_id = data['id']
        camera = Camera.query.filter(Camera.id == camera_id).first()
        if camera is not None:
            if not camera.verify_hash(data['password']):
                return jsonify({'success': False, 'msg': 'Wrong password'}), 400
            camera.active = True
            camera.save_to_db()

            cameras = Camera.query.all()
            socketio.emit('camera_list', {'cameras': [
                cam.to_dict() for cam in cameras if cam.active]}, broadcast=True)
        return jsonify({'success': True})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/active', methods=['GET'])
@jwt_required()
def get_active_camera():
    try:
        cameras = Camera.query.all()
        return jsonify({'success': True, 'cameras': [cam.to_dict() for cam in cameras if cam.active]})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/active/<id>', methods=['DELETE'])
def delete_active_camera(id):
    try:
        data = request.get_json()
        camera_id = data['id']
        camera = Camera.query.filter(Camera.id == camera_id).first()
        if camera is not None:
            if not camera.verify_hash(data['password']):
                return jsonify({'success': False, 'msg': 'Wrong password'}), 400
            camera.active = False
            camera.save_to_db()
            cameras = Camera.query.all()

            socketio.emit('camera_list', {'cameras': [
                cam.to_dict() for cam in cameras if cam.active]}, broadcast=True)

        return jsonify({'success': True, 'deleted_cameras': camera.to_dict()})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera', methods=['GET'])
@jwt_required()
def get_camera():
    try:
        results = Camera.query.all()
        return jsonify({'success': True, 'cameras': [result.to_dict() for result in results]})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera', methods=['POST'])
@jwt_required()
def add_camera():
    try:
        request_data = request.get_json()
        camera = Camera()
        camera.name = request_data['name']
        camera.password = Camera.generate_hash(request_data['password'])
        camera.save_to_db()
        return jsonify({'success': True, 'camera': camera.to_dict()}), 200
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/<id>', methods=['PUT'])
@jwt_required()
def change_camera(id):
    try:
        request_data = request.get_json()
        camera = Camera.query.filter(Camera.id == id).first()
        if not camera:
            return jsonify({'success': False, 'msg': 'Camera not found'}), 400
        if 'name' in request_data:
            camera.name = request_data['name']
        if 'password' in request_data:
            camera.password = Camera.generate_hash(request_data['password'])
        camera.save_to_db()
        return jsonify({'success': True, 'camera': camera.to_dict()}), 200
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/<id>', methods=['DELETE'])
@jwt_required()
def delete_camera(id):
    try:
        camera = Camera.query.filter(Camera.id == id).first()
        if not camera:
            return jsonify({'success': False, 'msg': 'Camera not found'}), 400
        camera.delete_in_db()
        return jsonify({'success': True, 'camera': camera.to_dict()}), 200
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/product', methods=['GET'])
@jwt_required()
def get_camera_product():
    try:
        cameras = Camera.query.all()
        camera_products = CameraProduct.query.join(
            Product, CameraProduct.product_id == Product.id)\
            .add_columns(Product.name, Product.price)\
            .all()
        data = []
        for camera in cameras:
            info = [{
                'id': c[0].product_id,
                'name': c[1],
                'price': c[2],
                'quantity': c[0].quantity
            } for c in camera_products if c[0].camera_id == camera.id]
            cam = camera.to_dict()
            cam['products'] = info
            data.append(cam)
        return jsonify({'success': True, 'cameras': data})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/product', methods=['POST'])
@jwt_required()
def add_camera_product():
    try:
        request_data = request.get_json()
        camera_product = CameraProduct.query.filter(CameraProduct.camera_id == request_data['camera_id'])\
            .filter(CameraProduct.product_id == request_data['product_id']).first()
        if camera_product is not None:
            camera_product.quantity += request_data['quantity']
            camera_product.save_to_db()
        else:
            camera = Camera.query.filter(
                Camera.id == request_data['camera_id']).first()
            if camera is None:
                return jsonify({'success': False, 'msg': 'Camera not found'}), 400

            product = Product.query.filter(
                Product.id == request_data['product_id']).first()
            if product is None:
                return jsonify({'success': False, 'msg': 'Product not found'}), 400

            camera_product = CameraProduct(camera_id=request_data['camera_id'],
                                           product_id=request_data['product_id'],
                                           quantity=request_data['quantity'])
            camera_product.save_to_db()

        return jsonify({'success': True, 'added': camera_product.to_dict()})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/<camera_id>/product/<product_id>', methods=['PUT'])
@jwt_required()
def change_product_quantity(camera_id, product_id):
    try:
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
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/camera/<camera_id>/product/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_camera_product(camera_id, product_id):
    try:
        result = CameraProduct.query.filter(CameraProduct.camera_id == camera_id)\
            .filter(CameraProduct.product_id == product_id).first()
        if result is None:
            return jsonify({'success': False, 'error': 'Product not found'}), 400
        else:
            result.delete_in_db()
            return jsonify({'success': True, 'deleted': result.to_dict()})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500

######################## Logger API ########################


@app.route('/log/text', methods=['POST'])
@jwt_required()
def get_all_log_text():
    try:
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
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/log/text/<id>', methods=['POST'])
@jwt_required()
def get_log_text_by_id(id):
    try:
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
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/log/image', methods=['POST'])
@jwt_required()
def get_all_log_image():
    try:
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
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/log/image/count/<id>', methods=['POST'])
@jwt_required()
def count_log_image_by_id(id):
    try:
        data = request.get_json()
        from_date = data['from']
        to_date = data['to']
        total = LogImage.query.filter(LogImage.camera_id == id).filter(
            LogImage.time.between(from_date, to_date)).count()
        # print(total)
        return jsonify({'success': True, 'total': total})
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500


@app.route('/log/image/<id>', methods=['POST'])
@jwt_required()
def get_log_image_by_id(id):
    try:
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
    except Exception as err:
        return jsonify({'success': False, 'msg': repr(err)}), 500
