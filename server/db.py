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
        db_config = config.DATABASE
        if db_config['type'] == 'sqlite3':
            try:
                self.db_file = db_config['path']
                self.conn = sqlite3.connect(
                    self.db_file, check_same_thread=False)
            except Error as e:
                print(e)
        else:
            raise NotImplementedError('Only support sqlite3 now')

    def create_table(self):
        raise NotImplementedError

    def create_cursor(self):
        return self.conn.cursor()

    def insert(self, table, value):
        placeholder = ','.join(['?' for i in range(len(value))])
        sql = 'INSERT INTO {} VALUES({})'.format(table, placeholder)
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


class ImageModel():
    def __init__(self, value):
        self.id = int(value[0])
        self.path = value[1]
        self.product_id = int(value[2])

    def __repr__(self):
        return "<Image(id = '%d', path='%s', product='%d')>" % (self.id, self.path, self.product_id)


class ProductModel():
    def __init__(self, value):
        self.id = int(value[0])
        self.name = value[1]
        self.weight = float(value[2])

    def __repr__(self):
        return "<Product(id = '%d', name='%s', weight='%f')>" % (self.id, self.name, self.weight)


if __name__ == "__main__":
    db = Database()

    # result1 = db.get(sql="SELECT * FROM images", ENTITY=ImageModel)
    # print(result1)

    # result2 = db.get(sql="SELECT * FROM images", ENTITY=ImageModel, limit=1)
    # print(result2)

    result3 = db.get(sql="SELECT * FROM images WHERE id = ?", ENTITY=ImageModel,
                     value=(20, ), limit=1)
    print(result3)
