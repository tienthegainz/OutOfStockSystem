import os
from db import Database, Singleton, Product, Image


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

    def map_image_cls(self):
        cls_list = []
        session = self.db.create_session()
        try:
            for id, in session.query(Product.id):
                cls_list.append(id)
        except Exception as e:
            print(e)
            raise Exception('Problem querying products\n')
        finally:
            session.close()

        for cls in os.listdir(self.img_path):
            cls_id = int(cls)
            if cls_id in cls_list:
                session = self.db.create_session()
                try:
                    print("Processing class {}".format(cls_id))
                    cls_path = os.path.join(self.img_path, cls)
                    images_path = [os.path.join(cls_path, image)
                                   for image in os.listdir(cls_path)]

                    for image_path in images_path:
                        a = Image(image_path, cls_id)
                        print(a)
                        session.add(a)
                    session.commit()
                except Exception as e:
                    print(e)
                    session.rollback()
                finally:
                    session.close()
            print('=================================')
        return


if __name__ == "__main__":
    import config
    s = Storage(storage_config=config.STORAGE, database_config=config.DATABASE)
    s.map_image_cls()
