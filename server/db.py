import config
import sqlite3
from sqlite3 import Error


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=Singleton):

    def __init__(self):
        self.db_config = config.DATABASE
        if self.db_config['type'] == 'sqlite3':
            try:
                self.db_file = self.db_config['path']
                self.conn = sqlite3.connect(
                    self.db_file, check_same_thread=False)
            except Error as e:
                print(e)
        else:
            raise NotImplementedError('Only support sqlite3 now')

    def run_sql(self, create_table_sql):
        """
            For create, drop, ...
        """
        try:
            c = self.create_cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_cursor(self):
        return self.conn.cursor()

    def insert(self, sql, value):
        cur = self.create_cursor()
        cur.execute(sql, value)
        self.conn.commit()
        return cur.lastrowid

    def get(self, sql, ENTITY, value=None, limit=-1):
        if sql == None:
            print('No sql provided')
            return None
        cur = self.create_cursor()
        if value == None:
            cur.execute(sql)
        else:
            cur.execute(sql, value)

        if limit == -1:
            results = cur.fetchall()
            return [ENTITY(r) for r in results] if results else None

        elif limit > 1:
            results = cur.fetchmany(limit)
            return [ENTITY(r) for r in results] if results else None

        elif limit == 1:
            result = cur.fetchone()
            return ENTITY(result) if result else None

        return None


class ProductImageModel():

    drop_table_sql = "DROP TABLE product_image;"
    create_table_sql = """
        CREATE TABLE product_image ( 
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
            path VARCHAR NOT NULL, 
            product_id INTEGER NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE, 
        )
    """

    def __init__(self, value):
        self.id = int(value[0])
        self.path = value[1]
        self.product_id = int(value[2])

    def __repr__(self):
        return "<ProductImage(id = '%d', path='%s', product='%d')>" % (self.id, self.path, self.product_id)

    def dict(self):
        return {'id': self.id, 'path': self.path, 'product_id': self.product_id}


class ProductModel():

    drop_table_sql = "DROP TABLE products;"
    create_table_sql = """
        CREATE TABLE products ( 
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
            name VARCHAR NOT NULL, 
            price INTEGER NOT NULL,
            path VARCHAR NOT NULL, 
        )
    """

    def __init__(self, value):
        self.id = int(value[0])
        self.name = value[1]
        self.price = int(value[2])
        self.image = value[3]

    def __repr__(self):
        return "<Product(id = '%d', name='%s', price='%f', image='%s')>" % (self.id, self.name, self.price, self.image)

    def dict(self):
        return {'id': self.id, 'name': self.name, 'price': self.price}


class LogImageModel():

    drop_table_sql = "DROP TABLE log_image;"
    create_table_sql = """
        CREATE TABLE log_image ( 
            id INTEGER  PRIMARY KEY AUTOINCREMENT UNIQUE, 
            url TEXT NOT NULL, 
            time TEXT NOT NULL, 
        )
    """

    def __init__(self, value):
        self.id = int(value[0])
        self.url = value[1]
        self.time = value[2]

    def __repr__(self):
        return "<LogImage(id = '%d', url='%s', time='%f')>" % (self.id, self.url, self.time)

    def dict(self):
        return {'id': self.id, 'url': self.url, 'time': self.time}


if __name__ == "__main__":
    db = Database()

    # result1 = db.get(sql="SELECT * FROM images", ENTITY=ImageModel)
    # print(result1)

    # result2 = db.get(sql="SELECT * FROM images", ENTITY=ImageModel, limit=1)
    # print(result2)

    result3 = db.get(sql="SELECT * FROM images WHERE id = ?", ENTITY=ImageModel,
                     value=(20, ), limit=1)
    print(result3)
