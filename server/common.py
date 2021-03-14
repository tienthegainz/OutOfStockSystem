import random
import string
from functools import wraps
from flask import jsonify, request


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def random_name_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Flask decorator for camera to send request to server
def camera_protected_api(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        request_data = request.get_json()
        if not request_data or 'pass' not in request_data or request_data['pass'] != '123':
            return jsonify({'success': False, 'msg': 'Access to embbed camera api BLOCKED'}), 400
        return f(*args, **kwargs)

    return wrap


# Flask decorator for camera to send socket to server
def camera_protected_socket(f):
    @wraps(f)
    def wrap(data):
        if 'pass' not in data or data['pass'] != '123':
            return jsonify({'success': False, 'msg': 'Access to embbed camera api BLOCKED'}), 400
        return f(data)

    return wrap
