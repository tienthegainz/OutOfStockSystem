import hnswlib
import numpy as np


class Searcher(object):
    def __init__(self, dim=2048, space='l2', threshold=0.5):
        """
            Args:
                dim: face embedding feature length
                space: distance algorithm (L2, Inner product, cosine)
                threshold: similarity threshold
        """
        self.p = hnswlib.Index(space=space, dim=dim)
        self.p.init_index(max_elements=1000, ef_construction=200, M=48)
        self.p.set_ef(20)
        self.k = 1
        self.threshold = threshold

    def add_products(self, data, index):
        try:
            if index.shape[0] != data.shape[0]:
                # TODO: Logging here
                print('Try to assign index with length {} to data with length {}'.format(
                    index.shape[0], data.shape[0]))
            else:
                self.p.add_items(data, index)
        except Exception as err:
            # TODO: Logging here
            print(err)

    def query_products(self, data):
        try:
            index, distance = self.p.knn_query(data, k=self.k)
            # Filter result
            index = np.squeeze(index)
            distance = np.squeeze(distance)
            print('Index: ', index, '\nDistance: ', distance)
            return index if distance < self.threshold else None
        except Exception as err:
            # TODO: Logging here
            print(err)
            return None
