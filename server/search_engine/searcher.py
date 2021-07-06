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
        storage_config = config.STORAGE
        search_config = config.SEARCHER
        self.graph_path = os.path.join(
            storage_config['path'], storage_config['ann'], 'index.bin')
        self.index_path = os.path.join(
            storage_config['path'], storage_config['ann'], 'current_index')

        self.p = hnswlib.Index(
            space=search_config['space'], dim=search_config['dim'])
        if os.path.isfile(self.graph_path):
            print('Loading graph: ', self.graph_path)
            self.p.load_index(self.graph_path, max_elements=1000)
        else:
            print('Init search tree')
            self.p.init_index(max_elements=1000, ef_construction=200, M=48)
            self.p.set_ef(20)

        if os.path.isfile(self.index_path):
            with open(self.index_path, 'r') as f:
                a = f.readline()
                print('Loading index {} => value: {} '.format(self.index_path, a))
                self.max_index = int(a)
        else:
            print('Init search tree index from 0')
            self.max_index = 0

        self.k = 1
        self.threshold = search_config['threshold']

        self.extractor = Extractor()
        print('Searcher booted with index: {} - thres: {}'.format(self.max_index, self.threshold))

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

    def delete_products(self, indexes):
        try:
            if len(indexes) == 0:
                raise ValueError('Index is empty')
            for index in indexes:
                self.p.mark_deleted(index)
            print('Mark idx: {} as deleted in tree'.format(indexes))
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

    def save_graph(self):
        print("Saving index to '%s'" % self.graph_path)
        self.p.save_index(self.graph_path)
        with open(self.index_path, 'w') as f:
            f.write(str(self.max_index))
