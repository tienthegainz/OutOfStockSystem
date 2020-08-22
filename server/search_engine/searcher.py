import hnswlib
import numpy as np
import os
import config
from db import *
from search_engine.extractor import Extractor
import PIL


class Searcher(metaclass=Singleton):
    def __init__(self, dim=2048, space='l2', threshold=0.5):
        """
            Args:
                dim: face embedding feature length
                space: distance algorithm (L2, Inner product, cosine)
                threshold: similarity threshold
        """
        storage = config.STORAGE
        self.graph_path = os.path.join(
            storage['path'], storage['ann'], 'index.bin')
        self.index_path = os.path.join(
            storage['path'], storage['ann'], 'current_index')

        self.p = hnswlib.Index(space=space, dim=dim)
        if os.path.isfile(self.graph_path):
            print('Loading graph: ', self.graph_path)
            self.p.load_index(self.graph_path, max_elements=1000)
        else:
            self.p.init_index(max_elements=1000, ef_construction=200, M=48)
            self.p.set_ef(20)

        self.k = 1
        self.threshold = threshold
        if os.path.isfile(self.index_path):
            with open(self.index_path, 'r') as f:
                a = f.readline()
                print('Loading index {} => value: {} '.format(self.graph_path, a))
                self.max_index = int(a)
        else:
            self.max_index = 0

        self.extractor = Extractor()

    def add_products(self, data, index):
        try:
            if index.shape[0] == 0:
                raise ValueError

            if index.shape[0] != data.shape[0]:
                # TODO: Logging here
                print('Try to assign index with length {} to data with length {}'.format(
                    index.shape[0], data.shape[0]))
            else:
                self.max_index += index.shape[0]
                self.p.add_items(data, index)
        except Exception as err:
            # TODO: Logging here
            print(err)

    def query_products(self, data):
        try:
            index, distance = self.p.knn_query(data, k=1)
            # Filter result
            index = np.squeeze(index)
            distance = np.squeeze(distance)
            print('Index: ', index, '\nDistance: ', distance)
            return index if distance < self.threshold else None
        except Exception as err:
            # TODO: Logging here
            print(err)
            return None

    def build_graph_from_storage(self, images):
        data = list()
        index = list()
        for image in images:
            index.append(image.id)
            data.append(self.extractor.extract(PIL.Image.open(image.path)))

        data = np.squeeze(np.array(data), axis=1)
        index = np.array(index)
        # print(data.shape)
        # print(index)
        self.add_products(data, index)

    def save_graph(self):
        print("Saving index to '%s'" % self.graph_path)
        self.p.save_index(self.graph_path)
        with open(self.index_path, 'w') as f:
            f.write(str(self.max_index))


if __name__ == "__main__":
    import config
    from db import *
    s = Searcher()
    # db_instance = Database(config.DATABASE)
    # session = db_instance.create_session()

    # try:
    #     images = session.query(Image).all()
    #     s.build_graph_from_storage(images)
    #     s.save_graph()
    # except Exception as e:
    #     print('Error: ', e)
    #     session.rollback()
    # finally:
    #     session.close()
    try:
        data = s.extractor.extract(PIL.Image.open(
            '/home/tienhv/GR/OutOfStockSystem/server/storage/image/2/1.jpeg'))
        index = s.query_products(data)
        print(index)
    except Exception as err:
        print(err)
