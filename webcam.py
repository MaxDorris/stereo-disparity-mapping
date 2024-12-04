import cv2
from cv2_enumerate_cameras import enumerate_cameras

for camera_info in enumerate_cameras():
    print(f'{camera_info.index}: {camera_info.name}')



# # Access the webcam (usually 0 for the default camera)
# cap = cv2.VideoCapture(0)



# while True:
#     # Read a frame from the webcam
#     ret, frame = cap.read()

#     # Check if the frame was captured successfully
#     if not ret:
#         break

#     # Display the frame
#     cv2.imshow("Webcam Stream", frame)

#     # Exit the loop if the 'q' key is pressed
#     if cv2.waitKey(1) == ord('q'):
#         break

# # Release the webcam and close the window
# cap.release()
# cv2.destroyAllWindows()