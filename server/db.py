import sqlite3
from sqlite3 import Error


class Database():
    def __init__(self, db_config):
        self.db_config = db_config
        if self.db_config['type'] == 'sqlite3':
            try:
                self.conn = sqlite3.connect(self.db_config['path'])
            except Error as e:
                print(e)
                raise Error
        else:
            raise NotImplementedError(
                '{} not supported'.format(self.db_config['type']))

    def init_tables(self):
        sql_create_products_table = """ CREATE TABLE IF NOT EXISTS `products`(
                                    `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                    `name`	TEXT NOT NULL,
                                    `wgt`	REAL NOT NULL
                                    ); """
        sql_create_products_images_table = """ CREATE TABLE IF NOT EXISTS `products_images`(
                                    `pid`	INTEGER NOT NULL,
                                    `iid`	INTEGER NOT NULL,
                                    `name`	TEXT NOT NULL,
                                    PRIMARY KEY (pid, iid),
                                    FOREIGN KEY(pid) REFERENCES products(id)
                                    ); """
        try:
            c = self.conn.cursor()
            c.execute(sql_create_products_table)
            c.execute(sql_create_products_images_table)
            self.conn.commit()
        except Error as e:
            print(e)
            raise Error

    def insert_products(self, values):
        sql_insert_tb = """INSERT INTO products (name, wgt) VALUES(?, ?)"""
        try:
            c = self.conn.cursor()
            c.execute(sql_insert_tb, values)
            self.conn.commit()
        except Error as e:
            print(e)
            raise Error

    def insert_products_images(self, values):
        sql_insert_tb = """INSERT INTO products_images (pid, iid, name) VALUES(?, ?, ?)"""
        try:
            c = self.conn.cursor()
            c.execute(sql_insert_tb, values)
            self.conn.commit()
        except Error as e:
            print(e)
            raise Error


if __name__ == '__main__':
    import config
    db = Database(config.DATABASE)
    db.init_tables()
