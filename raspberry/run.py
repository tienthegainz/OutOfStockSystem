import io
import time
import picamera
from base64 import b64encode
import requests
import numpy as np
import cv2
import sys
import signal
import socketio
from socketio.exceptions import BadNamespaceError

socket_url = 'http://10.42.0.1'
post_url = 'http://10.42.0.1:5001'

camera_info = {
    "id": 1,
    "password": "123"
}


def signal_handler(sig, frame):
    respond = requests.delete(
        '{}/camera/active/{}'.format(post_url, camera_info['id']), json=camera_info, timeout=2)
    print(respond)
    print('Exit gracefully')
    sys.exit(0)


if __name__ == '__main__':
    # Handle signal
    signal.signal(signal.SIGINT, signal_handler)
    # Notify server about camera
    respond = requests.post(
        '{}/camera/active'.format(post_url), json=camera_info, timeout=2)

    if respond.status_code != 200:
        print('Activate camera failed with respond: {}'.format(respond.json()))
        raise Exception('Request error')
    else:
        print('Registered camera with id: {}'.format(camera_info['id']))

    try:
        socketIO = socketio.Client()
        socketIO.connect('http://10.42.0.1:5001')
        with picamera.PiCamera() as camera:
            # config
            camera.framerate = 15
            print('Resolution: {}\nFramerate: {}\n'.format(
                camera.resolution, camera.framerate))
            time.sleep(1)
            stream = io.BytesIO()
            is_tracked = False
            count = 0
            states = []
            multiTracker = None
            # Notify server about camera
            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                if count % 450 == 0:
                    # POST image to server for detecting
                    multiTracker = cv2.MultiTracker_create()
                    base64_image = b64encode(
                        stream.getvalue()).decode('utf-8')
                    respond = requests.post(
                        '{}/product/detect'.format(post_url), json={
                            'id': camera_info['id'],
                            "image": base64_image
                        }, timeout=4)
                    if respond.status_code != 200:
                        raise Exception('Request error {}'.format(respond.status_code))
                    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                    image = cv2.imdecode(data, 1)
                    image = image[:, :, ::-1]
                    data = respond.json()
                    print(data)
                    if data['info'] != None:
                        states = data['info']
                        print('Init done: {}'.format(states))
                        is_tracked = True
                        # assign tracker
                        for state in states:
                            bbox = tuple(state['bbox'])
                            multiTracker.add(
                                cv2.TrackerKCF_create(), image, bbox)

                    else:
                        print('No object detected')
                        is_tracked = False
                else:
                    try:
                        t = time.time()
                        base64_image = b64encode(
                            stream.getvalue()).decode('utf-8')
                        if is_tracked:
                            if count % 5 == 0:
                                data = np.frombuffer(
                                    stream.getvalue(), dtype=np.uint8)
                                image = cv2.imdecode(data, 1)
                                image = image[:, :, ::-1]
                                success, boxes = multiTracker.update(image)
                                if success:
                                    for i, bbox in enumerate(boxes):
                                        states[i]['bbox'] = [
                                            int(v) for v in bbox]
                                print(states)
                            socketIO.emit(
                                'camera', {
                                    "id": camera_info['id'],
                                    "image": base64_image,
                                    "info": states,
                                    "fire_check": (count % 300 == 0),
                                    "track_start": (count % 450 == 1)
                                })
                        else:
                            socketIO.emit(
                                'camera', {
                                    "id": camera_info['id'],
                                    "password": camera_info['password'],
                                    "image": base64_image,
                                    "fire_check": (count % 300 == 0),
                                    "track_start": (count % 450 == 1)
                                })

                        print('sending image after {}'.format(time.time()-t))
                    except BadNamespaceError:
                        print('The socket message has been lost')
                count += 1
                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
    except Exception as e:
        print(e)
        respond = requests.delete(
            '{}/camera/active/{}'.format(post_url, camera_info['id']), json=camera_info, timeout=2)
        print(respond)
