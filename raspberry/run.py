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

socket_url = 'http://10.42.0.1'
post_url = 'http://10.42.0.1:5001/product/detect'


if __name__ == '__main__':

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

            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                if count % 50 == 0:
                    multiTracker = cv2.MultiTracker_create()
                    # tracker = cv2.TrackerKCF_create()
                    files = {"image": stream.getvalue()}
                    respond = requests.post(post_url, files=files, timeout=4)
                    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                    image = cv2.imdecode(data, 1)
                    image = image[:, :, ::-1]
                    data = respond.json()
                    print(data)
                    if data['info'] != None:
                        # tracker.init(image, tuple(data['info'][0]['bbox']))
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
                    base64_image = b64encode(stream.getvalue()).decode('utf-8')
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
                                    states[i]['bbox'] = [int(v) for v in bbox]
                            print(states)
                        socketIO.emit(
                            'camera', {
                                "image": base64_image,
                                "info": states
                            })
                    else:
                        socketIO.emit(
                            'camera', {"image": base64_image})

                    print('sending image after {}'.format(time.time()-t))

                count += 1
                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
