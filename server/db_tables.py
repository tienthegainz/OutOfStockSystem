from sqlalchemy import Column, Integer, String, Float
from db import Database


class Product(Database.Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weight = Column(Float)

    def __repr__(self):
        return "<Product(name='%s', weight='%f')>" % (self.name, self.weight)


if __name__ == "__main__":
    print(Product.__table__)
