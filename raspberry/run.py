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
            tracker = cv2.TrackerKCF_create()
            time.sleep(0.1)
            stream = io.BytesIO()
            count = 0

            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                if count % 3000 == 0:
                    files = {"image": stream.getvalue()}
                    respond = requests.post(post_url, files=files, timeout=4)
                    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                    image = cv2.imdecode(data, 1)
                    image = image[:, :, ::-1]
                    data = respond.json()
                    tracker.init(image, tuple(data['bbox']))
                    print('Init done')
                else:
                    t = time.time()
                    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                    image = cv2.imdecode(data, 1)
                    image = image[:, :, ::-1]
                    (success, box) = tracker.update(image)
                    if success:
                        bbox = [int(v) for v in box]
                        # print("Bbox: {}".format(bbox))
                        print(b64encode(stream.getvalue()))
                    #     socketIO.emit(
                    #         'camera', {"image": b64encode(stream.getvalue())})
                    # else:
                    #     socketIO.emit(
                    #         'camera', {"image": b64encode(stream.getvalue())})
                    print('sending image after {}'.format(time.time()-t))

                count += 1
                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
