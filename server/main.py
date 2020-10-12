from db import Database, Image
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from flask import Flask, request, jsonify
from PIL import Image as PILImage
import io
import argparse
import traceback

parser = argparse.ArgumentParser(
    description='App arguments')
parser.add_argument('--build', action="store_true", help='Build tree on load')
args = parser.parse_args()


app = Flask(__name__)
extractor = Extractor()
searcher = Searcher()
database = Database()


def boot_app():
    global extractor
    global searcher
    global database
    session = database.create_session()

    print("Build searching tree for first time")

    try:
        images = session.query(Image).all()
        searcher.build_graph_from_storage(images)
        searcher.save_graph()
    except Exception as e:
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


# @app.route('/init')
# def start_up_app():
#     return


# @app.route('/product/add')
# def add_product():
#     return


# @app.route('/product/remove')
# def remove_product():
#     return


# @app.route('/product/empty')
# def verify_empty_product():
#     return


@app.route('/rasp/test', methods=['POST'])
def test_rasp_camera():
    image_data = request.files['image'].read()
    image = PILImage.open(io.BytesIO(image_data))
    image.show()

    return jsonify({'success': True})


@app.route('/product/search', methods=['POST'])
def search_product_only():
    image_data = request.files['image'].read()
    image = PILImage.open(io.BytesIO(image_data))
    image.show()
    data = extractor.extract(image)
    index = searcher.query_products(data)
    print("Result: ", index)

    return jsonify({'success': True})


if __name__ == '__main__':
    if args.build:
        boot_app()
    app.run(host='0.0.0.0', port='5001', debug=True)
