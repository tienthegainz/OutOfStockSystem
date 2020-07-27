import cv2

if __name__ == "__main__":
    vidcap = cv2.VideoCapture('GR-test-2.mp4')
    success, image = vidcap.read()
    count = 0
    while success:
        if count % 50 == 0:
            cv2.imwrite("test_data_2/frame%d.jpg" % count, image)
        success, image = vidcap.read()
        count += 1
