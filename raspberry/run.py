from socketIO_client import SocketIO, LoggingNamespace
import io
import time
import picamera
from base64 import b64encode
import requests
import numpy as np
import cv2
from threading import Thread
import json
import sys
import signal

socket_url = 'http://10.42.0.1'
post_url = 'http://10.42.0.1:5001'

camera_info = {
    "id": 1,
}


def signal_handler(sig, frame):
    respond = requests.delete(
        '{}/camera/active/{}'.format(post_url, camera_info['id']), timeout=2)
    print(respond)
    print('Exit gracefully')
    sys.exit(0)


if __name__ == '__main__':
    # Handle signal
    signal.signal(signal.SIGINT, signal_handler)
    # Notify server about camera
    respond = requests.post(
        '{}/camera/active'.format(post_url), json=camera_info, timeout=2)
    print('Register camera with id: {} <== {}'.format(
        camera_info['id'], respond.json()))
    try:
        with SocketIO(socket_url, 5001, LoggingNamespace) as socketIO:
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
                    if count % 100 == 0:
                        # POST image to server for detecting
                        multiTracker = cv2.MultiTracker_create()
                        base64_image = b64encode(
                            stream.getvalue()).decode('utf-8')
                        respond = requests.post(
                            '{}/product/detect'.format(post_url), json={
                                'id': camera_info['id'],
                                "image": base64_image
                            }, timeout=4)
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
                        t = time.time()
                        base64_image = b64encode(
                            stream.getvalue()).decode('utf-8')
                        if is_tracked:
                            if count % 5 == 0:
                                data = np.frombuffer(
                                    stream.getvalue(), dtype=np.uint8)
                                image = cv2.imdecode(data, 1)
                                image = image[:, :, ::-1]
                                # (success, box) = tracker.update(image)
                                # if success:
                                #     bbox = [int(v) for v in box]
                                #     print("Bbox: {}".format(bbox))
                                #     states[0]['bbox'] = bbox
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
                                    "fire_check": (count % 50 == 0)
                                })
                        else:
                            socketIO.emit(
                                'camera', {
                                    "id": camera_info['id'],
                                    "image": base64_image,
                                    "fire_check": (count % 50 == 0)
                                })

                        print('sending image after {}'.format(time.time()-t))

                    count += 1
                    # Reset the stream for the next capture
                    stream.seek(0)
                    stream.truncate()
    except Exception as e:
        print(e)
        respond = requests.delete(
            '{}/camera/active/{}'.format(post_url, camera_info['id']), timeout=2)
        print(respond)
