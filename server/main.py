from db import Database, ImageModel, ProductModel
from detect_engine.detector import Detector
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from flask import Flask, request, jsonify
from PIL import Image as PILImage
import io
import argparse
import traceback
import numpy as np
import config
import os
import threading

parser = argparse.ArgumentParser(
    description='App arguments')
parser.add_argument('--build', action="store_true", help='Build tree on load')
args = parser.parse_args()


app = Flask(__name__)


extractor = Extractor()
searcher = Searcher()
database = Database()
detector = Detector()


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


def detect_search_image(image):
    try:
        data = detector.predict(image)
        products = []
        for prod in data['products']:
            pil_prod = PILImage.fromarray(prod.astype('uint8'), 'RGB')
            feature = extractor.extract(pil_prod)
            index = searcher.query_products(feature)
            image_info = database.get(sql="SELECT * FROM images WHERE id = ?", ENTITY=ImageModel,
                                      value=(index, ), limit=1)
            product = database.get(sql="SELECT * FROM products WHERE id = ?", ENTITY=ProductModel,
                                   value=(image_info.product_id, ), limit=1)
            print(product)
    except Exception as e:
        traceback.print_exc()


@app.route('/rasp/test', methods=['POST'])
def test_rasp_camera():
    image_data = request.files['image'].read()
    image = PILImage.open(io.BytesIO(image_data))
    image.show()

    return jsonify({'success': True})


@app.route('/product/watch', methods=['POST'])
def watch_product():
    image_data = request.files['image'].read()
    image = PILImage.open(io.BytesIO(image_data))
    image = np.array(image)
    x = threading.Thread(target=detect_search_image, args=(image,))
    x.start()
    # detect_search_image(image)
    return jsonify({'success': True})


if __name__ == '__main__':
    if args.build:
        boot_app()
    app.run(host='0.0.0.0', port='5001', debug=True, use_reloader=False)
