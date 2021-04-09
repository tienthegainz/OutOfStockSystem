from app import db
from passlib.hash import pbkdf2_sha256 as sha256


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    images = db.relationship('ProductImage', backref='products', lazy=True)

    def __repr__(self):
        return "<Product(id = '%d', name='%s', price='%f')>" % (self.id, self.name, self.price)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'price': self.price}

    def to_dict_bulk(self):
        return {
            'id': self.id, 'name': self.name, 'price': self.price,
            'images': [image.to_dict() for image in self.images]
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        for image in self.images:
            image.delete_in_db()
        db.session.delete(self)
        db.session.commit()


class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), nullable=False)
    ann_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<ProductImage(id = '%d', url='%s', product='%d')>" % (self.id, self.url, self.product_id)

    def to_dict(self):
        return {'id': self.id, 'url': self.url, 'product_id': self.product_id}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        db.session.delete(self)
        db.session.commit()


class Camera(db.Model):
    __tablename__ = 'cameras'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, default=False)
    password = db.Column(db.String, nullable=False)
    images = db.relationship('LogImage', backref='cameras', lazy=True)
    texts = db.relationship('LogText', backref='cameras', lazy=True)
    products = db.relationship('CameraProduct', backref='cameras', lazy=True)

    @staticmethod
    def generate_hash(password):

        return sha256.hash(password)

    """
    Verify hash and password
    """

    def verify_hash(self, password):
        return sha256.verify(password, self.password)

    def __repr__(self):
        return "<Camera(id = '%d', name='%s, active='%r')>" % (self.id, self.name, self.active)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'active': self.active,
            # 'images': [image.to_dict() for image in self.images],
            # 'texts': [text.to_dict() for text in self.texts]
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        for image in self.images:
            image.delete_in_db()
        for text in self.texts:
            text.delete_in_db()
        for product in self.products:
            product.delete_in_db()
        db.session.delete(self)
        db.session.commit()


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

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        db.session.delete(self)
        db.session.commit()


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

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        db.session.delete(self)
        db.session.commit()


class CameraProduct(db.Model):
    __tablename__ = 'camera_products'
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), nullable=False, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey(
        'cameras.id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<CameraProduct(product_id = '%d', camera_id = '%d', quantity='%d')>" % (self.product_id, self.camera_id, self.quantity)

    def to_dict(self):
        return {'product_id': self.product_id, 'camera_id': self.camera_id, 'quantity': self.quantity}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    """
    generate hash from password by encryption using sha256
    """
    @staticmethod
    def generate_hash(password):

        return sha256.hash(password)

    """
    Verify hash and password
    """

    def verify_hash(self, password):
        return sha256.verify(password, self.password)

    def __repr__(self):
        return "<User(id = '%d', username = '%s', admin = '%r')>" % (self.id, self.username, self.admin)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'admin': self.admin}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        db.session.delete(self)
        db.session.commit()


class RevokedToken(db.Model):
    __tablename__ = 'revoked_token'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)
    is_expired = db.Column(db.Boolean, nullable=False)
    is_logout = db.Column(db.Boolean, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "<RevokedToken(id = '%d', jti = '%s', is_expired = '%r', is_logout = '%r')>" % (self.id, self.jti, self.is_expired, self.is_logout)

    def to_dict(self):
        return {'id': self.id, 'jti': self.jti, 'is_expired': self.is_expired, 'is_logout': self.is_logout}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_in_db(self):
        db.session.delete(self)
        db.session.commit()
