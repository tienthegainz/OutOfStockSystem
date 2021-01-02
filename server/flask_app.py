from db import Database, ImageModel, ProductModel
from detect_engine.detector import Detector
from fire_engine.fire import FireAlarm
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from tracker_engine.tracker import Tracker
# from daemon import fire_alert
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from PIL import Image
from celery import Celery
import io
import traceback
import time
import numpy as np
import base64


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", message_queue='redis://')

celery = Celery(
    app.name, broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'])


extractor = None
searcher = None
database = None
detector = None
tracker = None
fire_alarm = FireAlarm()

count = 0


# def boot_app():
#     global extractor
#     global searcher
#     global database

#     if not os.path.isfile(config.DATABASE['path']):
#         database.create_table()

#     print("Build searching tree for first time")
#     try:
#         images = database.get(sql="SELECT * FROM images")
#         searcher.build_graph_from_storage(images)
#         searcher.save_graph()
#     except Exception as e:
#         raise e


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


@celery.task
def fire_alert(data):
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    print('Detecting fire...')
    with app.app_context():
        image_data = base64.b64decode(data)
        image = Image.open(io.BytesIO(image_data))
        result = fire_alarm.check_fire(image)
        socketio.emit('fire', {'fire': True})


@socketio.on('camera')
def socket_camera(data):
    global count
    if count == 0:
        socketio.emit('ready', {'ready': True})
    try:
        count += 1
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data))

        if count % 20 == 0:
            print('Run background job')
            fire_alert.delay(data['image'])

        bbox = data['bbox'] if 'bbox' in data else None

        result_image = track_image(image, bbox)

        socketio.emit('image', {'image': result_image}, broadcast=True)
    except Exception as err:
        print(err)


@app.route('/hello', methods=['GET'])
def hello():
    # fire_alert.delay()
    return jsonify({'message': 'hello', 'legit': detector.test()})


@app.route('/product/detect', methods=['POST'])
def watch_product():
    socketio.emit('ready', {'ready': False})
    image_data = request.files['image'].read()
    image = Image.open(io.BytesIO(image_data))
    result_image, products, bbox = detect_search_object(image)

    for product in products:
        socketio.emit('log', {'log': product}, broadcast=True)

    socketio.emit('image', {'image': result_image}, broadcast=True)

    return jsonify({'success': True, 'bbox': bbox})


if __name__ == '__main__':
    # if args.build:
    #     boot_app()
    # app.run(host='0.0.0.0', port='5001', debug=True, use_reloader=False)
    detector = Detector()
    extractor = Extractor()
    searcher = Searcher()
    database = Database()
    tracker = Tracker()
    socketio.run(app, host='0.0.0.0', port='5001',
                 debug=True, use_reloader=False)
