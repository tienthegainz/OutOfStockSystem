from app import socketio
from flask_socketio import join_room, leave_room
from common import camera_protected_socket
from tracker_engine.tracker import TrackerMulti
from PIL import Image
from worker import handle_out_of_roi, fire_alert

import base64
import io
import numpy as np

tracker = TrackerMulti()

######################## Utils ########################


def track_image(data, info, room):
    image_data = base64.b64decode(data)
    image = Image.open(io.BytesIO(image_data))
    np_image = np.array(image)
    update_ok = False
    if info is not None and info:
        update_ok = tracker.update(np_image, info)
    else:
        update_ok = tracker.update(np_image)
    draw_img = tracker.draw()
    if tracker.check_out_roi() or not update_ok:
        print('Out of ROI')
        handle_out_of_roi.delay(data, room)

    result_image = Image.fromarray(draw_img.astype(np.uint8))
    img_byte = io.BytesIO()
    result_image.save(img_byte, format='jpeg')
    base64_image = base64.b64encode(
        img_byte.getvalue()).decode('utf-8')
    return base64_image

######################## Socket list ########################


@socketio.on('camera')
@camera_protected_socket
def on_send_image(data):
    room = int(data['id'])
    try:
        if data['fire_check']:
            fire_alert.delay(data['image'], room)
        
        if data['track_start']:
            socketio.emit('ready', {'ready': True}, room=room, broadcast=True)

        info = data['info'] if 'info' in data else None

        result_image = track_image(data['image'], info, room)
        # print('Sending data to room {}'.format(room))
        socketio.emit('image', {'image': result_image},
                      room=room, broadcast=True)
    except Exception as err:
        print(err)


@socketio.on('dummy')
def on_join(data):
    print('Data: ', data)


@socketio.on('join')
def on_join(data):
    room = int(data['id'])
    join_room(room)
    print('Connected to room: {}'.format(room))


@socketio.on('leave')
def on_leave(data):
    room = int(data['id'])
    leave_room(room)
    print('Left room: {}'.format(room))
