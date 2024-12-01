import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import os

class DepthMap:
    def __init__(self,showImages):

        # Load images
        root = os.getcwd()
        imgLeftPath = os.path.join(root, 'demoImages//sticks//im0.png')
        imgRightPath = os.path.join(root, 'demoImages//sticks//im1.png')
        self.imgLeft = cv.imread(imgLeftPath,cv.IMREAD_GRAYSCALE)
        self.imgRight = cv.imread(imgRightPath,cv.IMREAD_GRAYSCALE)

        if showImages: # plot the images next to eachother
            plt.figure()
            plt.subplot(121)
            plt.imshow(self.imgLeft)
            plt.subplot(122)
            plt.imshow(self.imgRight)
            plt.show()

    def computeDepthMapBM(self):
        nDispFactor = 16 # adjustable
        stereo = cv. StereoBM.create(numDisparities=16*nDispFactor,
                                     blockSize=21)
        disparity = stereo.compute(self.imgLeft, self.imgRight)
        plt.imshow(disparity,'gray')
        plt.show()
    
    def computeDepthMapSGBM(self):
        window_size = 7
        min_disp = 16
        nDispFactor = 14 # adjustable (14 is good)

def demoViewPics():
    # initializes an object of class "DepthMap", passing in the extra arg of showImages=True so that the images are plotted after being loaded in after initialization
    dp = DepthMap(showImages=True)

def demoStereoBM():
    dp = DepthMap(showImages=False)
    dp.computeDepthMapBM()

def demoStereoSGBM():
    dp = DepthMap(showImages=False)
    dp.computeDepthMapSGBM()

if __name__ == '__main__':
    # demoViewPics()
    demoStereoBM()
    # demoStereoSGBM()