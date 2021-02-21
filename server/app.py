from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
    DATABASE['path']) if DATABASE['type'] == 'sqlite3' else ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


CORS(app)
# socketio = SocketIO(app, cors_allowed_origins="*", message_queue='redis://')
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)

# Active camera list on runtime
cameras = []

if __name__ == '__main__':
    from app_router import *
    from app_socket import *
    socketio.run(app, host='0.0.0.0', port='5001',
                 debug=True, use_reloader=False)
