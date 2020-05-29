import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import measure

def mse(imageA, imageB):
    	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def compare_images(imageA, imageB, title):
    # compute the mean squared error and structural similarity
	# index for the images
    m = mse(imageA, imageB)
    s = measure.compare_ssim(imageA, imageB, multichannel=True)

    # setup the figure
    fig = plt.figure(title)
    plt.suptitle("MSE: %.2f SSIM: %.2f" % (m, s))

    # show first image
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(imageA)
    plt.axis("off")
    # show the second image
    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(imageB)
    plt.axis("off")
    # show the images
    plt.show()

def main():
    a = cv2.imread('1.jpg')
    b = cv2.imread('2.jpg')
    # a = cv2.resize(a, (128, 128), interpolation = cv2.INTER_AREA)
    # b = cv2.resize(b, (128, 128), interpolation = cv2.INTER_AREA)

    compare_images(a, b, "O")

if __name__ == "__main__":
    main()