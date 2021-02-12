from faker import Faker
from db import Database, LogImageModel, LogTextModel, ProductImageModel, ProductModel

if __name__ == '__main__':
    fake = Faker()
    print(fake.text())
