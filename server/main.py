from db import Database, ImageModel, ProductModel
from detect_engine.detector import Detector
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from tracker_engine.tracker import Tracker
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from PIL import Image
import io
import argparse
import traceback
import time
import numpy as np
import config
import os
import base64


parser = argparse.ArgumentParser(
    description='App arguments')
parser.add_argument('--build', action="store_true", help='Build tree on load')
args = parser.parse_args()


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


extractor = Extractor()
searcher = Searcher()
database = Database()
detector = Detector()
tracker = Tracker()

count = 0
ready = True


def boot_app():
    global extractor
    global searcher
    global database

    if not os.path.isfile(config.DATABASE['path']):
        database.create_table()

    print("Build searching tree for first time")
    try:
        images = database.get(sql="SELECT * FROM images")
        searcher.build_graph_from_storage(images)
        searcher.save_graph()
    except Exception as e:
        raise e


def search_product(data):
    try:
        products = []
        for prod in data:
            pil_prod = Image.fromarray(prod.astype('uint8'), 'RGB')
            feature = extractor.extract(pil_prod)
            index = searcher.query_products(feature)
            image_info = database.get(sql="SELECT * FROM images WHERE id = ?", ENTITY=ImageModel,
                                      value=(index, ), limit=1)
            product = database.get(sql="SELECT * FROM products WHERE id = ?", ENTITY=ProductModel,
                                   value=(image_info.product_id, ), limit=1)
            products.append(str(product))

        return products
    except Exception as e:
        traceback.print_exc()
    return None


# def process_image(image):
#     global count, ready
#     products = []

#     if count == 0:
#         if ready:
#             # notify loading
#             # socketio.emit('log', {'log': 'Waiting for boot'}, broadcast=True)
#             ready = False
#             data = detector.predict(image)
#             products = search_product(data['products'])
#             print(
#                 "Bbox: {} - image: {}".format(data['bboxes'][0], data['image'].shape))
#             print("Init track: ", tracker.init_tracker(
#                 data['image'], data['bboxes'][0]))
#             draw_img = tracker.draw()

#             result_image = Image.fromarray(draw_img.astype(np.uint8))
#             img_byte = io.BytesIO()
#             result_image.save(img_byte, format='jpeg')
#             base64_image = base64.b64encode(
#                 img_byte.getvalue()).decode('utf-8')
#             count += 1
#             ready = True
#             # notify loading complete
#             # socketio.emit('log', {'log': 'Booting completed'}, broadcast=True)
#             return True, base64_image, products
#         elif not ready:
#             return False, None, None
#     else:
#         return False, None, None

#     return False, None, None


def detect_search_object(image):
    data = detector.predict(image)
    products = search_product(data['products'])
    tracker.update(data['image'], data['bboxes'][0])
    draw_img = tracker.draw()

    result_image = Image.fromarray(draw_img.astype(np.uint8))
    img_byte = io.BytesIO()
    result_image.save(img_byte, format='jpeg')
    base64_image = base64.b64encode(
        img_byte.getvalue()).decode('utf-8')
    return base64_image, products, data['bboxes'][0]


def track_image(image, bbox=None):
    np_image = np.array(image)
    if bbox != None:
        tracker.update(np_image, bbox)
    else:
        tracker.update_frame(np_image)
    draw_img = tracker.draw()

    result_image = Image.fromarray(draw_img.astype(np.uint8))
    img_byte = io.BytesIO()
    result_image.save(img_byte, format='jpeg')
    base64_image = base64.b64encode(
        img_byte.getvalue()).decode('utf-8')
    return base64_image


@socketio.on('camera')
def socket_camera(data):
    image_data = base64.b64decode(data['image'])
    image = Image.open(io.BytesIO(image_data))
    bbox = data['bbox'] if 'bbox' in data else None

    result_image = track_image(image, bbox)

    socketio.emit('image', {'image': result_image}, broadcast=True)


@app.route('/hello', methods=['POST'])
def hello():
    return jsonify({'message': 'hello'})


@app.route('/product/detect', methods=['POST'])
def watch_product():
    image_data = request.files['image'].read()
    image = Image.open(io.BytesIO(image_data))
    result_image, products, bbox = detect_search_object(image)

    for product in products:
        socketio.emit('log', {'log': product}, broadcast=True)

    socketio.emit('image', {'image': result_image}, broadcast=True)

    return jsonify({'success': True, 'bbox': bbox})


if __name__ == '__main__':
    if args.build:
        boot_app()
    # app.run(host='0.0.0.0', port='5001', debug=True, use_reloader=False)
    socketio.run(app, host='0.0.0.0', port='5001',
                 debug=True, use_reloader=False)
