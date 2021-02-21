import hnswlib
import numpy as np
import os
import config
from search_engine.extractor import Extractor
from common import Singleton
import PIL


class Searcher(metaclass=Singleton):
    """
        Search which product by its image
    """

    def __init__(self):
        """
            Args:
                dim: face embedding feature length
                space: distance algorithm (L2, Inner product, cosine)
                threshold: similarity threshold
        """
        print('Init search engine')
        storage_config = config.STORAGE
        search_config = config.SEARCHER
        self.graph_path = os.path.join(
            storage_config['path'], storage_config['ann'], 'index.bin')

        self.p = hnswlib.Index(
            space=search_config['space'], dim=search_config['dim'])
        if os.path.isfile(self.graph_path):
            print('Loading graph: ', self.graph_path)
            self.p.load_index(self.graph_path, max_elements=1000)
        else:
            self.p.init_index(max_elements=1000, ef_construction=200, M=48)
            self.p.set_ef(20)

        self.k = 1
        self.threshold = search_config['threshold']

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
                # self.max_index += index.shape[0]
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
            return int(index) if distance < self.threshold else None
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
        self.add_products(data, index)

    def save_graph(self):
        print("Saving index to '%s'" % self.graph_path)
        self.p.save_index(self.graph_path)
