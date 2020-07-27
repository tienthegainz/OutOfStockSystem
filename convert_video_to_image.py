import cv2

if __name__ == "__main__":
    vidcap = cv2.VideoCapture('GR1-test.mp4')
    success, image = vidcap.read()
    count = 0
    while success:
        if count % 100 == 0:
            cv2.imwrite("test_data/frame%d.jpg" % count, image)
        success, image = vidcap.read()
        count += 1
