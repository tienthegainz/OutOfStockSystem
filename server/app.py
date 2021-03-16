from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
import logging
import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': 'app.log',
        }
    },
    'loggers': {
        'console': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': 'no',
        },
        'file': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': 'no',
        }
    },
    'root': {
        'level': 'INFO',
        # 'handlers': ['console', 'file']
        'handlers': ['console']
    },

})


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
    DATABASE['path']) if DATABASE['type'] == 'sqlite3' else ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "809f597a682d5d8c578f400da1d5dcba26ca366d855df2b4"
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
