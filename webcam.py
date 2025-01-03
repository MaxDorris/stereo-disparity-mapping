import cv2
import time
from cv2_enumerate_cameras import enumerate_cameras

def main():

    for camera_info in enumerate_cameras():
        print(f'{camera_info}')

    # Access the webcam (usually 0 for the default camera)
    cam_list = []
    for i in range(15):
        print(f'Connecting to Camera {i}')
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        except:
            print('NO CAMERA FOUND FOR {i}')
            reset_camera(cap)
            continue

        print(f'Testing camera {i}\n')
        timer = time.time()
        while True:
            tick = time.time()
            # Read a frame from the webcam
            ret, frame = cap.read()

            # Check if the frame was captured successfully
            if not ret:
                break

            # Display the frame
            cv2.imshow(f"Webcam Stream {i}", frame)

            # Exit the loop if the 'q' key is pressed
            if tick - timer >= 8:
                print(f'Camera {i}: NOT FOUND')
                reset_camera(cap)
                break
            elif cv2.waitKey(1) == ord('q'):
                print(f'Camera {i}: FOUND')
                cam_list.append(i)
                print(f"Camera {i} added to cam_list.")
                reset_camera(cap)
                break

def reset_camera(cap):
    # Release the webcam and close the window
    print('Disconnecting from camera and resetting window\n')
    cap.release()
    cv2.destroyAllWindows()
    time.sleep(5)

if __name__=='__main__':
    main()