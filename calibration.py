import PySpin
import cv2 as cv
import numpy as np
import os

# Parameters for calibration
CHECKERBOARD = (9, 6)  # Checkerboard dimensions (number of inner corners per row and column)
SQUARE_SIZE = 0.025  # Size of a square in meters (adjust based on your checkerboard)

def capture_calibration_images(system, num_images=20):
    """
    Captures calibration images from two cameras.
    """
    cam_list = system.GetCameras()
    if cam_list.GetSize() < 2:
        print("At least two cameras are required.")
        cam_list.Clear()
        system.ReleaseInstance()
        return None, None

    # Initialize cameras
    camera_left = cam_list[0]
    camera_right = cam_list[1]
    camera_left.Init()
    camera_right.Init()

    # Start acquisition
    camera_left.BeginAcquisition()
    camera_right.BeginAcquisition()

    print(f"Capturing {num_images} calibration images...")
    left_images = []
    right_images = []

    try:
        for i in range(num_images):
            print(f"Capturing image pair {i+1}/{num_images}...")
            # Capture left image
            image_left_result = camera_left.GetNextImage()
            if image_left_result.IsIncomplete():
                print("Left image incomplete. Skipping...")
                continue
            left_image = image_left_result.GetNDArray()
            left_images.append(left_image)
            image_left_result.Release()

            # Capture right image
            image_right_result = camera_right.GetNextImage()
            if image_right_result.IsIncomplete():
                print("Right image incomplete. Skipping...")
                continue
            right_image = image_right_result.GetNDArray()
            right_images.append(right_image)
            image_right_result.Release()

        print("Finished capturing images.")

    finally:
        # Stop acquisition and deinitialize cameras
        camera_left.EndAcquisition()
        camera_right.EndAcquisition()
        camera_left.DeInit()
        camera_right.DeInit()
        cam_list.Clear()

    return left_images, right_images


def calibrate_stereo_camera(left_images, right_images):
    """
    Performs stereo calibration using captured images.
    """
    # Prepare object points (3D points in real-world space)
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    objpoints = []  # 3D points in real-world space
    imgpoints_left = []  # 2D points in left images
    imgpoints_right = []  # 2D points in right images

    # Detect checkerboard corners in both sets of images
    for left_image, right_image in zip(left_images, right_images):
        gray_left = cv.cvtColor(left_image, cv.COLOR_BGR2GRAY)
        gray_right = cv.cvtColor(right_image, cv.COLOR_BGR2GRAY)

        ret_left, corners_left = cv.findChessboardCorners(gray_left, CHECKERBOARD, None)
        ret_right, corners_right = cv.findChessboardCorners(gray_right, CHECKERBOARD, None)

        if ret_left and ret_right:
            objpoints.append(objp)
            imgpoints_left.append(corners_left)
            imgpoints_right.append(corners_right)

            # Optional: Draw and display the corners for visual verification
            cv.drawChessboardCorners(left_image, CHECKERBOARD, corners_left, ret_left)
            cv.drawChessboardCorners(right_image, CHECKERBOARD, corners_right, ret_right)
            cv.imshow("Left Camera", left_image)
            cv.imshow("Right Camera", right_image)
            cv.waitKey(500)

    cv.destroyAllWindows()

    # Perform intrinsic calibration for each camera
    print("Calibrating individual cameras...")
    _, mtx_left, dist_left, _, _ = cv.calibrateCamera(objpoints, imgpoints_left, gray_left.shape[::-1], None, None)
    _, mtx_right, dist_right, _, _ = cv.calibrateCamera(objpoints, imgpoints_right, gray_right.shape[::-1], None, None)

    # Stereo calibration to find relative positions between cameras
    print("Performing stereo calibration...")
    _, _, _, _, _, R, T, E, F = cv.stereoCalibrate(
        objpoints,
        imgpoints_left,
        imgpoints_right,
        mtx_left,
        dist_left,
        mtx_right,
        dist_right,
        gray_left.shape[::-1],
        criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6),
        flags=cv.CALIB_FIX_INTRINSIC,
    )

    # Stereo rectification to align images for depth mapping
    print("Performing stereo rectification...")
    R1, R2, P1, P2, Q, _, _ = cv.stereoRectify(
        mtx_left,
        dist_left,
        mtx_right,
        dist_right,
        gray_left.shape[::-1],
        R,
        T,
        alpha=0,
    )

    return {
        "mtx_left": mtx_left,
        "dist_left": dist_left,
        "mtx_right": mtx_right,
        "dist_right": dist_right,
        "R": R,
        "T": T,
        "E": E,
        "F": F,
        "R1": R1,
        "R2": R2,
        "P1": P1,
        "P2": P2,
        "Q": Q,
    }


def save_calibration_data(calibration_data, filename="stereo_calibration_data.npz"):
    """
    Saves stereo calibration data to a file.
    """
    np.savez(filename, **calibration_data)
    print(f"Calibration data saved to {filename}")


def main():
    system = PySpin.System.GetInstance()

    try:
        # Step 1: Capture calibration images from both cameras
        left_images, right_images = capture_calibration_images(system)

        if not left_images or not right_images:
            print("Failed to capture calibration images.")
            return

        # Step 2: Perform stereo calibration
        calibration_data = calibrate_stereo_camera(left_images, right_images)

        # Step 3: Save calibration data to a file
        save_calibration_data(calibration_data)

    finally:
        system.ReleaseInstance()


if __name__ == "__main__":
    main()