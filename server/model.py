from app import db


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    images = db.relationship('ProductImage', backref='products', lazy=True)

    def __repr__(self):
        return "<Product(id = '%d', name='%s', price='%f')>" % (self.id, self.name, self.price)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'price': self.price,
            'images': [image.to_dict() for image in self.images]
        }


class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), nullable=False)

    def __repr__(self):
        return "<ProductImage(id = '%d', url='%s', product='%d')>" % (self.id, self.url, self.product_id)

    def to_dict(self):
        return {'id': self.id, 'url': self.url, 'product_id': self.product_id}


class Camera(db.Model):
    __tablename__ = 'cameras'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    images = db.relationship('LogImage', backref='cameras', lazy=True)
    texts = db.relationship('LogText', backref='cameras', lazy=True)

    def __repr__(self):
        return "<Camera(id = '%d', name='%s')>" % (self.id, self.name)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name,
            'images': [image.to_dict() for image in self.images],
            'texts': [text.to_dict() for text in self.texts]
        }


class LogImage(db.Model):
    __tablename__ = 'log_images'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey(
        'cameras.id'), nullable=False)

    def __repr__(self):
        return "<LogImage(id = '%d', url='%s', time='%s' product='%d')>" % (self.id, self.url, self.time, self.camera_id)

    def to_dict(self):
        return {'id': self.id, 'url': self.url, 'time': self.time, 'camera_id': self.camera_id}


class LogText(db.Model):
    __tablename__ = 'log_texts'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey(
        'cameras.id'), nullable=False)

    def __repr__(self):
        return "<LogImage(id = '%d', message='%s', time='%s' product='%d')>" % (self.id, self.message, self.time, self.camera_id)

    def to_dict(self):
        return {'id': self.id, 'message': self.message, 'time': self.time, 'camera_id': self.camera_id}
