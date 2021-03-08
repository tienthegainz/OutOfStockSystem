from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
    DATABASE['path']) if DATABASE['type'] == 'sqlite3' else ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "thesis-20202"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)


CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", message_queue='redis://')
db = SQLAlchemy(app)
jwt = JWTManager(app)


if __name__ == '__main__':
    os.environ['SERVER_STATE'] = 'running'
    from app_router import *
    from app_socket import *
    socketio.run(app, host='0.0.0.0', port='5001',
                 debug=True, use_reloader=False)
