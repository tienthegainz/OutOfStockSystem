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
            camera.framerate = 30
            print('Resolution: {}\nFramerate: {}\n'.format(
                camera.resolution, camera.framerate))
            tracker = None
            time.sleep(0.1)
            stream = io.BytesIO()
            is_tracked = False
            count = 0
            states = []

            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                if count % 300 == 0:
                    tracker = cv2.TrackerKCF_create()
                    files = {"image": stream.getvalue()}
                    respond = requests.post(post_url, files=files, timeout=4)
                    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                    image = cv2.imdecode(data, 1)
                    image = image[:, :, ::-1]
                    data = respond.json()
                    if data['info'] != None:
                        tracker.init(image, tuple(data['info'][0]['bbox']))
                        states.append(data['info'][0])
                        print('Init done')
                        is_tracked = True
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
                            (success, box) = tracker.update(image)
                            if success:
                                bbox = [int(v) for v in box]
                                print("Bbox: {}".format(bbox))
                                states[0]['bbox'] = bbox

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
