import os
from db import Database, Singleton


class Storage(metaclass=Singleton):
    def __init__(self, storage_config, database_config):
        if storage_config['type'] == 'local':
            self.path = storage_config['path']
            if 'image' in storage_config:
                self.img_path = os.path.join(
                    storage_config['path'], storage_config['image'])
        else:
            raise NotImplementedError(
                '{} not supported'.format(self.db_config['type']))
        self.db = Database(database_config)

    def get_k_image_all_classes(self, k=8, db_map=True):
        """
            Get k or less(in case not enough k) from each class, label them
        """
        result = dict()
        for cls in os.listdir(self.img_path):
            cls_id = int(cls)
            if self.db.check_product_id(cls_id):
                print("Processing class {}".format(cls))
                cls_path = os.path.join(self.img_path, cls)
                image_path = [os.path.join(cls_path, image)
                              for image in os.listdir(cls_path)[:k]]
                for i in range(len(image_path)):
                    img_id = cls_id*10+i
                    print(
                        "Class: {} - Image: {} - Path: {}".format(cls_id, img_id, image_path[i]))
                    result[img_id] = image_path[i]
            else:
                print("Skip class {} not valid".format(cls))
        if db_map:
            print("Saved to db")
        return result


if __name__ == "__main__":
    import config
    s = Storage(storage_config=config.STORAGE, database_config=config.DATABASE)
    s.get_k_image_all_classes()
