import os
import cv2
import time
import math
import gray2rgb
import threading
import sat_pixels
import imageio.v3
import numpy as np
import gen_states_float
import gen_linstates_cython
import convert_12bit_to_8bit
from datetime import datetime
from harvesters.core import Harvester
# Constants
GENICAM_FILE_PATH = r"C:\Program Files\MATRIX VISION\mvIMPACT Acquire\bin\x64\mvGenTLProducer.cti"
FPS_CALCULATION_INTERVAL = 0.5
FILE_PATH = os.getcwd()
def find_device_index(cam_name_list):
    H = Harvester()
    H.add_file(GENICAM_FILE_PATH)
    H.update()
    dev_list = H.device_info_list
    if len(cam_name_list) == 1:
        for index, device_info in enumerate(dev_list):
            if device_info.user_defined_name == cam_name_list[0]:
                H.reset()
                return index
    elif len(cam_name_list) > 1:
        returns = {}
        for name in cam_name_list:
            for index, device_info in enumerate(dev_list):
                if device_info.user_defined_name == name:
                    returns[name] = index
        H.reset()
        return returns
    else:
        H.reset()
        return None
def grab_size(index):
    H = Harvester()
    H.add_file(GENICAM_FILE_PATH)
    H.update()
    ia = H.create(index)
    h = ia.remote_device.node_map.Height()
    w = ia.remote_device.node_map.Width() 
    H.reset()
    return h, w
def to_truncated_float(value, decimals=2):
    if value is None:
        return 'NaN'
    try:
        num_float = float(value)
        factor = 10 ** decimals
        truncated = math.floor(num_float * factor) / factor
        return truncated
    except ValueError:
        return 'NaN'
class gigE_cam(threading.Thread):
    """
    A class representing a live event capturing thread, which handles the acquisition
    of images from a gigE polarization camera.

    Inputs:
        ia (Harvester object): The harvester object for each camera, part of intialization
        r (int): The number of rows in the camera frame.
        c (int): The number of columns in the camera frame.
        mode (str): Whether the camera is displaying raw or linear states.

    Methods:
        run(): Starts the image acquisition process and continually captures frames from the camera.
        is_running(): Checks if the image acquisition is currently active.
        stop(): Stops the image acquisition process.
        run_raw(): Internal method to handle image acquisition in raw mode.
        run_pol(): Internal method to handle image acquisition in polarization mode.
        cleanup(): Cleans up resources after image acquisition.
        mode_and_depth(mode,depth): Sets camera mode.
        get_latest_image(): Retrieves the latest data packet.
        setFps(fps): Sets the frame rate for image acquisition.
        setExp(exp): Sets the exposure value for image acquisition.
        gray2rgb_float(image): Makes a single channel image compatible with float RGB dearpygui format
        resize_im(image,h,w): resizes image array to match user need
    """
    def __init__(self,ia, r, c):
        super(gigE_cam, self).__init__()
        self.lock = threading.Lock()  # For thread-safe operations
        self._is_running = False
        self.r = r
        self.c = c
        try:
            self.ia = ia
            self.ia.remote_device.node_map.ExposureTime.value = 22
            self.ia.remote_device.node_map.TLParamsLocked.value = False
            self.ia.remote_device.node_map.GainSelector.value = 'SensorAll'
            self.ia.remote_device.node_map.Gain.value = 1
            self.ia.remote_device.node_map.GainRaw.value = 1
            self.ia.remote_device.node_map.PixelFormat.value = 'Mono8'
        except Exception as e:
            pass
    def mode_and_depth(self, mode, depth):
        '''
        Sets camera mode: either raw or pol acquisition
        
        Parameters:
            mode (str): either 'raw' or 'pol'
            depth(str): either '8' or '12'
        '''
        self.bit = depth
        if depth == '12':
            self.ia.remote_device.node_map.PixelFormat.value = 'Mono12'
        elif depth == '8':
            self.ia.remote_device.node_map.PixelFormat.value = 'Mono8'
        self.mode = mode
        if mode == 'raw':
            self.latest_image = []
            self.sat = None
            self.mean = None
        elif mode == 'pol':
            self.latest_image = []
            self.sat0 = None
            self.sat1 = None
            self.sat2 = None
            self.sat3 = None
            self.m_h = None
            self.m_v = None
            self.m_p = None
            self.m_m = None
        self.fps = 'NaN'
        self.temp = 'NaN'
    def run(self):
        """
        Starts the image acquisition process based on the specified mode.
        """
        self._is_running = True
        try:
            if self.mode == 'raw':
                self.run_raw()
            elif self.mode == 'pol':
                self.run_pol()
            else:
                raise ValueError("Invalid mode specified")
        except Exception as e:
            print(f'error: {e}')
            pass
        finally:
            pass
    def run_raw(self):
        """
        Internal method to handle image acquisition in raw mode.
        """
        try:
            self.ia.start()
            start_time = time.time()
            frame_count = 0
            while self._is_running:
                with self.ia.fetch() as buffer:
                    im_list = buffer.payload.components[0]
                    self.im = np.array(im_list.data).reshape(self.r, self.c)
                    if self.bit == '12':
                        im = convert_12bit_to_8bit.convert_12bit_to_8bit(self.im)
                    elif self.bit == '8':
                        im = self.im
                    frame_count += 1
                if time.time() - start_time >= FPS_CALCULATION_INTERVAL:
                    self.fps = frame_count / FPS_CALCULATION_INTERVAL 
                    self.temp = self.ia.remote_device.node_map.DeviceTemperature()
                    sat_thread = saturation(im,self.r, self.c)
                    sat_thread.start()
                    sat_thread.join()
                    self.sat = sat_thread.get_saturation()
                    mean_thread = image_mean(im)
                    mean_thread.start()
                    mean_thread.join()
                    self.mean = mean_thread.get_mean()
                    frame_count = 0
                    start_time = time.time()
                with self.lock:
                    self.latest_image = [im, self.fps, self.temp, self.sat, self.im, self.mean]
        except Exception as e:
            print(f"An error occurred: {e}")
            pass
        finally:
            pass
    def run_pol(self):
        """
        Internal method to handle image acquisition in polarization mode.
        """
        try:
            self.ia.start()
            start_time = time.time()
            frame_count = 0
            while self._is_running:
                with self.ia.fetch() as buffer:
                    im_list = buffer.payload.components[0]
                    self.im = np.array(im_list.data).reshape(self.r, self.c)
                    if self.bit == '12':
                        im = convert_12bit_to_8bit.convert_12bit_to_8bit(self.im)
                    else:
                        im = self.im
                    h,v,p,m = gen_linstates_cython.gen_lin_states(im, self.r, self.c) # max fps at ~56 on laptop 80 fps desktop
                    frame_count += 1
                if time.time() - start_time >= FPS_CALCULATION_INTERVAL:
                    self.fps = frame_count / FPS_CALCULATION_INTERVAL
                    self.temp = self.ia.remote_device.node_map.DeviceTemperature()
                    sat0_thread = saturation(h,self.r//2, self.c//2)
                    sat1_thread = saturation(v,self.r//2, self.c//2)
                    sat2_thread = saturation(p,self.r//2, self.c//2)
                    sat3_thread = saturation(m,self.r//2, self.c//2)
                    sat0_thread.start()  # Start threads
                    sat1_thread.start()
                    sat2_thread.start()
                    sat3_thread.start()  
                    sat0_thread.join() # Wait for threads to complete
                    sat1_thread.join()
                    sat2_thread.join()
                    sat3_thread.join()
                    self.sat0 = sat0_thread.get_saturation() # Retrieve saturation values
                    self.sat1 = sat1_thread.get_saturation()
                    self.sat2 = sat2_thread.get_saturation()
                    self.sat3 = sat3_thread.get_saturation()
                    m_h_thread = image_mean(h)
                    m_v_thread = image_mean(v)
                    m_p_thread = image_mean(p)
                    m_m_thread = image_mean(m)
                    m_h_thread.start()  # Start threads
                    m_v_thread.start()
                    m_p_thread.start()
                    m_m_thread.start()  
                    m_h_thread.join() # Wait for threads to complete
                    m_v_thread.join()
                    m_p_thread.join()
                    m_m_thread.join()
                    self.m_h = m_h_thread.get_mean()
                    self.m_v = m_v_thread.get_mean()
                    self.m_p = m_p_thread.get_mean()
                    self.m_m = m_m_thread.get_mean()
                    frame_count = 0
                    start_time = time.time()
                with self.lock:
                    self.latest_image = [h,v,p,m, self.fps, self.temp, self.sat0, self.sat1, self.sat2, self.sat3, self.im, self.m_h, self.m_v, self.m_p, self.m_m]
        except Exception as e:
            print(f"An error occurred: {e}")
            pass
        finally:
            pass
    def cleanup(self):
        """
        Cleans up resources after image acquisition.
        """
        self.ia.stop()
    def stop(self):
        """
        Stops the image acquisition process.
        """
        with self.lock:
            self._is_running = False
        self.cleanup()
    def get_latest_image(self):
        """
        Retrieves a list containing a list of the image(s) and associated stats
        
        'raw' mode =>
        [image, fps, sensor temperature °C, % saturation]
        
        'pol' mode =>
        [h image, v image, p image, m image, fps, sensor temperature °C, % saturation h,  % saturation v,  % saturation p,  % saturation m]
        """
        return self.latest_image
    def is_running(self):
        return self._is_running
    def setFps(self, fps):
        """
        Sets the frame rate for image acquisition.

        Input:
            fps (int): The desired frame rate.
        """
        self.ia.remote_device.node_map.AcquisitionFrameRate.value = int(fps)
    def setExp(self, exp):
        """
        Sets the exposure value for image acquisition.

        Parameters:
            exp (int): The desired exposure value.
        """
        if int(exp) <= (10**(6))*(self.fps**(-1.006)):
            self.ia.remote_device.node_map.ExposureTime.value = int(exp)
        else:
            pass
    def set_gain(self, gain): 
        '''
        Sets gain to be applied to the image before transmission.
        
        Parameters:
            gain (int): The desired gain value.
        """
        '''
        self.ia.remote_device.node_map.Gain.value = 1
    def set_PGAgain(self, gain):
        '''
        Parameters:
            gain (int): The desired gain value.
        '''
        self.ia.remote_device.node_map.GainRaw.value = int(gain)
    def gray2rgb_float(self, image):
        """
        Updates a image single channel image to match float RGB txture for dearpygui.

        Parameters:
            image (array): the single channel image.
        """
        return gray2rgb.gray2rgb_float(image)
    def resize_im(self, image,w,h):
        """
        Resizes image

        Parameters:
            image (array): the desired image to be resized
            w (int): desired image width
            h (int): desired image height
        """
        return cv2.resize(image, dsize=(w, h), interpolation=cv2.INTER_AREA)
class saturation(threading.Thread):
    """
    A class for calculating the saturation level of an image.

    Inputs:
        image (np.uint8 np.ndarray): The image for which saturation needs to be calculated.
        rows (int): The number of rows in the image.
        cols (int): The number of columns in the image.

    Methods:
        run(): Calculates and returns the saturation percentage of the image.
        get_saturation(): returns the saturation % of the image
    """
    def __init__(self, image, rows, cols):
        super(saturation, self).__init__()
        self.image = image
        self.r = rows
        self.c = cols
        self.saturation = None
    def run(self):
        try:
            self.saturation = sat_pixels.sat_pixel_per(self.image, self.r, self.c)
        except Exception as e:
            print(f"Error in calculating saturation: {e}")
    def get_saturation(self):
        return self.saturation
class image_mean(threading.Thread):
    """
    A class for calculating the normalized mean of an image.

    Inputs:
        image (np.uint8 np.ndarray): The image for which saturation needs to be calculated.

    Methods:
        run(): Calculates and returns the saturation percentage of the image.
        get_mean(): returns the normalized mean of the image
    """
    def __init__(self, image):
        super(image_mean, self).__init__()
        self.image = image
    def run(self):
        try:
            self.mean = np.mean(self.image) / 254
        except Exception as e:
            print(f"Error in calculating norm mean: {e}")
    def get_mean(self):
        return self.mean
class singleSave(threading.Thread):
    """
    A class responsible for saving captured images to the filesystem.

    Inputs:
        folder_name (str): The name of the folder where images will be saved.
        im_list (list): The list of images to be processed and saved.
        std_image (np.array): The standard deviation image of the number of images per save.
        bit(str): Bit depth of images.
        r(int): row size of image
        c(int): col size of image
        params(): list of acqusition parameters
        mode (str): determines which file path the images are appended to. "study" will stire images in the studies folder, "calibration" will store images in calibration folder, and "" will go to defualt directory (saved images).
        
    Methods:
        run(): Saves the provided images to the specified folder on the filesystem.
    """
    def __init__(self, folder_name, im_list, bit, r, c, params, mode):
        super(singleSave, self).__init__()
        self.lock = threading.Lock()  # For thread-safe operations
        today = datetime.now().strftime("%m_%d_%Y")
        time = datetime.now().strftime("%H_%M_%S")
        if mode == "":
            self.path = os.path.join(FILE_PATH, f'free hand images\\{folder_name}_{today}_{time}')
            try:   
                self.dict = {'Date':f"{today}", 'Time':f"{time}", 'ADC(bit depth)':f"{params[0]}",'Exposure (us)':f"{params[1]}", 'Analog Gain':f"{params[2]}", 'FW Position':f"{params[3]}", 'Color Position':f"{params[4]}",'Stepper Motor Angle (deg)':f"{params[5]}"}
            except IndexError:
                self.dict = {'Date':f"{today}", 'Time':f"{time}", 'ADC(bit depth)':f"{params[0]}",'Exposure (us)':f"{params[1]}", 'Analog Gain':f"{params[2]}"}
        elif mode == "study":
            self.path = os.path.join(FILE_PATH, f'studies\\study_{today}')
            if os.path.exists(self.path):
                    base_path = self.path
                    subdirectories_og = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
                    num_subdirectories_og = len(subdirectories_og)
                    if num_subdirectories_og >= 6:
                        for i in range(100):
                            new_path = f'{base_path}_{i}'
                            if os.path.exists(new_path):
                                subdirectories = [d for d in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, d))]
                                num_subdirectories = len(subdirectories)
                                if num_subdirectories < 6:
                                    self.path = new_path
                                    break   
                            else:
                                self.path = new_path
                                break
            self.path = os.path.join(self.path, folder_name)
            self.dict = {'Date':f"{today}", 'Time':f"{time}", 'ADC(bit depth)':f"{params[0]}",'Exposure (us)':f"{params[1]}", 'Analog Gain':f"{params[2]}", 'FW Position':f"{params[3]}", 'Color Position':f"{params[4]}",'Stepper Motor Angle (deg)':f"{params[5]}"}
        elif mode == "calibration":
            self.path = os.path.join(FILE_PATH, f'calibration\\cal_{today}')
            if os.path.exists(self.path):
                    base_path = self.path
                    subdirectories_og = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
                    num_subdirectories_og = len(subdirectories_og)
                    if num_subdirectories_og >= 6:
                        for i in range(100):
                            new_path = f'{base_path}_{i}'
                            if os.path.exists(new_path):
                                subdirectories = [d for d in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, d))]
                                num_subdirectories = len(subdirectories)
                                if num_subdirectories < 6:
                                    self.path = new_path
                                    break   
                            else:
                                self.path = new_path
                                break
            self.path = os.path.join(self.path, folder_name)
            self.dict = {'Date':f"{today}", 'Time':f"{time}", 'ADC(bit depth)':f"{params[0]}",'Exposure (us)':f"{params[1]}", 'Analog Gain':f"{params[2]}", 'FW Position':f"{params[3]}", 'Color Position':f"{params[4]}",'Stepper Motor Angle (deg)':f"{params[5]}"}
        self.avg_image = np.mean(np.array(im_list), axis=0).astype(np.float32)
        self.std_image = np.std(np.array(im_list), axis=0).astype(np.float32)
        self.bit = bit
        self.r = r
        self.c = c  
    def run(self):
        with self.lock:
            os.makedirs(self.path, exist_ok=True)
            try:
                self.avg_image = np.array(self.avg_image) 
                self.avg_image = self.avg_image.astype(np.float32)
                h,v,p,m = gen_states_float.gen_states_float(self.avg_image, self.r, self.c) # REMINDER FA of 0 means P and M => R and L 
                imageio.imwrite(os.path.join(self.path, 'raw_avg.tif'), self.avg_image)
                imageio.imwrite(os.path.join(self.path, 'h_avg.tif'), h)
                imageio.imwrite(os.path.join(self.path, 'v_avg.tif'), v)
                imageio.imwrite(os.path.join(self.path, 'p_avg.tif'), p)
                imageio.imwrite(os.path.join(self.path, 'm_avg.tif'), m)
                self.std_image = np.array(self.std_image).astype(np.float32)
                h,v,p,m = gen_states_float.gen_states_float(self.std_image, self.r, self.c) # REMINDER FA of 45 means H and V => R and L
                imageio.imwrite(os.path.join(self.path, 'raw_avg.tif'), self.std_image)
                imageio.imwrite(os.path.join(self.path, 'h_std.tif'), h)
                imageio.imwrite(os.path.join(self.path, 'v_std.tif'), v)
                imageio.imwrite(os.path.join(self.path, 'p_std.tif'), p)
                imageio.imwrite(os.path.join(self.path, 'm_std.tif'), m)
                os.chdir(self.path)
                with open(f'Metadata.txt', 'w') as f:
                    for key, value in self.dict.items():  
                        f.write('%s:%s\n' % (key, value))
                os.chdir(os.getcwd())
            except Exception as e:
                print(e)