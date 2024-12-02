import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import os
import sys

class DepthMap:
    def __init__(self,showImages, imgSet):

        # Load images
        root = os.getcwd()
        imgLeftPath = os.path.join(root, f'demoImages//{imgSet}//im0.png')
        imgRightPath = os.path.join(root, f'demoImages//{imgSet}//im1.png')
        self.imgLeft = cv.imread(imgLeftPath,cv.IMREAD_GRAYSCALE)
        self.imgRight = cv.imread(imgRightPath,cv.IMREAD_GRAYSCALE)

        if showImages: # plot the images next to eachother
            plt.figure(1)
            plt.subplot(221)
            plt.imshow(self.imgLeft)
            plt.subplot(222)
            plt.imshow(self.imgRight)
            # plt.show()

    def computeDepthMapBM(self):
        nDispFactor = 16 # adjustable
        stereo = cv. StereoBM.create(numDisparities=16*nDispFactor,
                                    blockSize=21)
        disparity = stereo.compute(self.imgLeft, self.imgRight)

        plt.figure(1)
        plt.subplot(223)
        plt.imshow(disparity,'gray')
        # plt.show()
    
    def computeDepthMapSGBM(self):
        window_size = 7
        min_disp = 16
        nDispFactor = 14 # adjustable (14 is good)
        num_disp = 16 * nDispFactor - min_disp

        stereo = cv.StereoSGBM_create(minDisparity=min_disp,
                                    numDisparities=num_disp,
                                    blockSize=window_size,
                                    P1=8*3*window_size**2,
                                    P2=32*3*window_size**2,
                                    disp12MaxDiff=1,
                                    uniquenessRatio=15,
                                    speckleWindowSize=0,
                                    speckleRange=2,
                                    preFilterCap=63,
                                    mode=cv.STEREO_SGBM_MODE_SGBM_3WAY)

        # compute disparity map
        disparity = stereo.compute(self.imgLeft, self.imgRight).astype(np.float32) / 16.0

        # display disparity map
        plt.figure(1)
        plt.subplot(224)
        plt.imshow(disparity, 'gray')
        plt.colorbar()
        plt.show()


def demoViewPics(imgSet):
    # initializes an object of class "DepthMap", passing in the extra arg of showImages=True so that the images are plotted after being loaded in after initialization
    dp = DepthMap(showImages=True, imgSet=imgSet)

def demoStereoBM():
    dp = DepthMap(showImages=False)
    dp.computeDepthMapBM()

def demoStereoSGBM():
    dp = DepthMap(showImages=False)
    dp.computeDepthMapSGBM()

if __name__ == '__main__':

    # Access arguments directly
    args = sys.argv[1:]  # Skip the script name (sys.argv[0])
    imgSet = args[0]
    print(imgSet)

    # run functions

    demoViewPics(imgSet)
    demoStereoBM()
    demoStereoSGBM()