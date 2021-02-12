from re import search
from search_engine.searcher import Searcher
from search_engine.extractor import Extractor
from db import Database, LogTextModel, ProductImageModel, ProductModel, LogImageModel
import config
import os
import argparse

parser = argparse.ArgumentParser(
    description='App arguments')
parser.add_argument('--table', action="store_true",
                    help='Create new table in Database')
parser.add_argument('--value', action="store_true",
                    help='Insert value into Database')
parser.add_argument('--tree', action="store_true",
                    help='Build search tree')
args = parser.parse_args()

database = Database()

if __name__ == "__main__":
    if args.table:
        database.run_sql(ProductModel.drop_table_sql)
        database.run_sql(ProductImageModel.drop_table_sql)
        database.run_sql(LogImageModel.drop_table_sql)
        database.run_sql(LogTextModel.drop_table_sql)
        database.run_sql(ProductModel.create_table_sql)
        database.run_sql(ProductImageModel.create_table_sql)
        database.run_sql(LogImageModel.create_table_sql)
        database.run_sql(LogTextModel.create_table_sql)
    if args.value:
        image_folder = os.path.join(
            config.STORAGE['path'], config.STORAGE['image'])
        # insert all image in storage into db
        insert_sql = 'INSERT INTO product_image(path, product_id) VALUES(?,?)'
        for product in os.listdir(image_folder):
            product_id = int(product)
            product_folder = os.path.join(image_folder, product)
            images = [os.path.join(product_folder, image)
                      for image in os.listdir(product_folder)]
            for image in images:
                database.insert(insert_sql, (image, product_id))
    if args.tree:
        searcher = Searcher()
        try:
            images = database.get(
                "SELECT * FROM product_image", ProductImageModel)
            searcher.build_graph_from_storage(images)
            searcher.save_graph()
        except Exception as e:
            raise e
