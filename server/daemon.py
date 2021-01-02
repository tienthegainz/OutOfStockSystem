from celery import Celery
from fire_engine.fire import FireAlarm
from flask_socketio import SocketIO
from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

celery = Celery(
    app.name, broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'])

fire_alarm = FireAlarm()


@celery.task
def fire_alert():
    socketio = SocketIO(app, cors_allowed_origins="*",
                        message_queue='redis://')
    # result = fire_alarm.check_fire(image)
    result = True
    with app.app_context():
        socketio.emit('fire', {'fire': result})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='5001',
                 debug=True, use_reloader=False)
