import io
import time
import picamera
import requests

# Create an in-memory stream
stream = io.BytesIO()
url = 'http://10.42.0.1:5001/product/watch'

print("Booting up camera")

t = 0

with picamera.PiCamera() as camera:
    camera.start_preview()
    while(True):
        if t > 10:
            break
        t += 1
        time.sleep(1)
        camera.capture(stream, 'jpeg')
        files = {"image": stream.getvalue()}
        try:
            respond = requests.post(url, files=files, timeout=1)
        except Exception as e:
            print(e)
        # Reset the stream
        stream.seek(0)
        stream.truncate()
