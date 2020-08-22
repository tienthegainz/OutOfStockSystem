import sqlite3
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=Singleton):
    Base = declarative_base()

    def __init__(self, db_config):
        self.db_config = db_config
        if self.db_config['type'] == 'sqlite3':
            try:
                self.engine = create_engine(
                    'sqlite:///{}'.format(self.db_config['path']), echo=True)
                self.Session = sessionmaker(bind=self.engine)
            except Exception as e:
                print(e)
                raise Exception
        else:
            raise NotImplementedError(
                '{} not supported'.format(self.db_config['type']))

    def create_table(self):
        Database.Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.Session()


class Product(Database.Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weight = Column(Float)
    image = relationship("Image", back_populates="product",
                         cascade="delete",
                         passive_deletes=True
                         )

    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return "<Product(name='%s', weight='%f')>" % (self.name, self.weight)


class Image(Database.Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    path = Column(String)
    product_id = Column(Integer, ForeignKey('products.id', ondelete="CASCADE"))
    product = relationship("Product", back_populates="image")

    def __init__(self, path, product_id):
        self.path = path
        self.product_id = product_id

    def __repr__(self):
        return "<Image(path='%s', product='%f')>" % (self.path, self.product_id)


if __name__ == '__main__':
    import config
    db = Database(config.DATABASE)
    # db.create_table()
    session = db.create_session()

    try:
        # product1 = Product(name="Mi Hao Hao", weight=20)
        # print(product1)
        # product2 = Product(name="Chai nuoc Lavie", weight=20)
        # print(product2)

        # session.add(product1)
        # session.add(product2)
        # session.commit()
        for id, in session.query(Product.id):
            print(id)
    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.close()
