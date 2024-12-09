# **Notes For Understanding This Library**

## gen_pattern.py

This script produces a printable calibration image that helps the *calibration.py* file correctly orient the cameras in 3D space. This ensures that depth estimations will remain accurate in case of human error, mechanical drift, etc. The scripts prints a standard 9x6 checkerboard at square width of 25mm by default.


## calibration.py

### Dynamic Recalibration:
After an initial calibration, mechanical shock or temperature fluctuation can change the distance between sensors. Mitigating these factors is important, and the way to do this is by periodically recalibrating to a frequency depenant on the likelihood of these events taking place. Ex: stereo cameras mounted on a military vehicle may need a higher recalibration frequency than two cameras mounted in a temperature controlled operating room.

### Calibration Patterns:
Checkerboard: Most widely used due to its simplicity and high accuracy.
Circle Grid: Useful for applications requiring subpixel accuracy.
AprilTag/ChArUco: Robust under varying lighting conditions and partial occlusions

### Zhang's Method:
This method for localizing