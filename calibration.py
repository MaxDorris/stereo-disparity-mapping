import cv2
import numpy as np
import glob

# Define the checkerboard dimensions (number of inner corners)
CHECKERBOARD = (9, 6)
SQUARE_SIZE = 25  # Size of each square in mm

# Prepare object points for a 9x6 checkerboard
# (e.g., (0,0,0), (25,0,0), (50,0,0), ..., (200,125,0))
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) * SQUARE_SIZE

# Arrays to store object points and image points
objpoints = []  # 3D points in real-world space
imgpoints = []  # 2D points in image plane

# Load all images from a directory
images = glob.glob('./calibration_images/*.jpg')  # Update with your folder path

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)

        # Refine corner locations for better accuracy
        corners_subpix = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            criteria=cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, (30, 0.001)
        )
        imgpoints.append(corners_subpix)

        # Draw and display the corners on the image (optional visualization)
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners_subpix, ret)
        cv2.imshow('Checkerboard', img)
        cv2.waitKey(100)

cv2.destroyAllWindows()

# Perform camera calibration
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

# Print calibration results
print("Camera Matrix:\n", camera_matrix)
print("Distortion Coefficients:\n", dist_coeffs)

# Save results for future use
np.savez('./calibration_results.npz', camera_matrix=camera_matrix,
         dist_coeffs=dist_coeffs, rvecs=rvecs, tvecs=tvecs)

# Undistort an example image
example_img = cv2.imread('./calibration_images/example.jpg')  # Replace with your test image path
h, w = example_img.shape[:2]
optimal_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs,
                                                           (w,h), 1)

undistorted_img = cv2.undistort(example_img, camera_matrix,
                                dist_coeffs, None,
                                optimal_camera_matrix)

# Crop the image to remove black borders (optional)
x, y, w, h = roi
undistorted_img = undistorted_img[y:y+h, x:x+w]

# Display undistorted image
cv2.imshow("Undistorted Image", undistorted_img)
cv2.waitKey(0)
cv2.destroyAllWindows()