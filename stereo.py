import numpy as np
import tkinter as tk
import dearpygui.dearpygui as dpg
from tkinter import messagebox as mb
from harvesters.core import Harvester
from stereo_module import find_device_index, grab_size, to_truncated_float, gigE_cam, singleSave
VERSION_NUMBER = '1.0'
GENICAM_FILE_PATH = r"C:\Program Files\MATRIX VISION\mvIMPACT Acquire\bin\x64\mvGenTLProducer.cti"
CAM_LIST = ['cam2', 'cam3']
# pyinstaller --onefile --windowed --icon=icon.ico stereo.py
# credit to https://www.flaticon.com/authors/paul-j for the icon
class CameraApp:
    def __init__(self):
        INDEX_DICT = find_device_index(CAM_LIST)
        self.num_avgs = ['Number of averages', '2', '4','8','16','32','64']
        self.time_btwn_captures = ['Time between captures', '1','2','4']
        self.case_num = 0
        self.im1_list = []
        self.im2_list = []
        self.save_ctrl = None
        self.im = None
        self.im2 = None
        self.cam1 = None
        self.cam2 = None
        self.ia1 = None
        self.ia2 = None
        dpg.create_context()
        dpg.create_viewport(title=f'PHASE 1 UI ({VERSION_NUMBER})', width=1460, height=820) 
        dpg.set_viewport_large_icon("icon.ico") 
        try:
            self.hh,self.ww = grab_size(INDEX_DICT[CAM_LIST[0]])
            self.H = Harvester()
            self.H.add_file(GENICAM_FILE_PATH)
            self.H.update()
            self.ia1 = self.H.create(INDEX_DICT[CAM_LIST[0]])
            self.ia2 = self.H.create(INDEX_DICT[CAM_LIST[1]])
            self.cam1 = gigE_cam(self.ia1, self.hh,self.ww)
            self.cam2 = gigE_cam(self.ia2, self.hh,self.ww)
            if self.cam1 and self.cam2:
                self.message_box(title= "Pairing Status", message="Cameras connected!")
            elif self.cam1 == None or self.cam2 == None:
                raise Exception('Camera pairing issue! Please ensure the cameras are connected properly and restart the application.')
        except Exception:
            self.message_box(title='Pairing Status!', message= 'Camera pairing issue! Please ensure the cameras are connected properly and restart the application.')
        self.default_setup()  
        dpg.setup_dearpygui() # Setup Dear PyGui
        dpg.show_viewport()   
    
    
    def default_setup(self):
        with dpg.window(label="Camera Initialization", width=400, height=100, pos= [0,0], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win1: # Create the Dear PyGui window
            items = ['Select bit depth', '8', '12'] 
            self.bitdepth = dpg.add_combo(items=items, width = 150, label="Camera ADC Bit Depth", callback=self.set_depth) # add callback function
            dpg.set_value(self.bitdepth, items[0])
            mode = ['Select display mode for both cameras', 'raw', 'pol', 'stereo']
            self.get_mode = dpg.add_combo(items=mode, width = 150, label="Display Type", callback=self.set_mode) # add callback function
            dpg.set_value(self.get_mode, mode[0])

    def setup_state(self, state):
        if state == 'raw':
            try:
                                                    # dpg.delete_item(self.win2)
                                                    # dpg.delete_item(self.win3)
                                                    # dpg.delete_item(self.win4)
                                                    # dpg.delete_item(self.win5)
                                                    # dpg.delete_item(self.win6)
                                                    # dpg.delete_item(self.win7)
                                                    # dpg.delete_item(self.win8)
                                                    # dpg.delete_item(self.win9)
                # DELETE pol-mode windows
                dpg.delete_item(self.win10)
                dpg.delete_item(self.win11)
                dpg.delete_item(self.win12)
                dpg.delete_item(self.win13)
                dpg.delete_item(self.win14)
                dpg.delete_item(self.win15)
                dpg.delete_item(self.win16)
                dpg.delete_item(self.win17)
                dpg.delete_item(self.win18)
                dpg.delete_item(self.win19)
                dpg.delete_item(self.win20)
                dpg.delete_item(self.win21)
                dpg.delete_item(self.win22)
                dpg.delete_item(self.win23)
                dpg.delete_item(self.win25)
                dpg.delete_item(self.win26)
                dpg.delete_item(self.win27)
                dpg.delete_item(self.win28)
                dpg.delete_item(self.win29)
                dpg.delete_item(self.win30)

                # DELETE stereo-mode windows



            except AttributeError:
                pass

            with dpg.window(label="Camera 1 Control", width=400, height=160, pos= [0,101], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win2: # Create the Dear PyGui window
                self.fps_slider = dpg.add_slider_int(label="FPS", default_value=24, min_value=1, max_value=24)
                with dpg.group(horizontal=True):
                    self.button = dpg.add_button(label="Start Camera 1", callback=self.toggle_camera1) 
                    self.status_label = dpg.add_text("Cam 1 Status: Off")
                self.exp_slider = dpg.add_slider_int(label="Exp (µs)", default_value=22, min_value=22, max_value=41447, callback= self.update_exp1)
                with dpg.group(horizontal=True):
                    self.exposure_cam1_entry = dpg.add_input_text()
                    dpg.add_button(label="Set Exposure", callback=self.set_cam1_exp)
                self.ag = dpg.add_slider_int(label="Sensor Gain", default_value=0, min_value=1, max_value=480, callback=self.update_PGAgain1)  

            with dpg.window(label="Camera 2 Control", width=400, height=160, pos= [0,262], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win3: # Create the Dear PyGui window
                self.fps_slider2 = dpg.add_slider_int(label="FPS", default_value=24, min_value=1, max_value=24)
                with dpg.group(horizontal=True):
                    self.button2 = dpg.add_button(label="Start Camera 2", callback=self.toggle_camera2) 
                    self.status_label2 = dpg.add_text("Cam 2 Status: Off")
                self.exp_slider2 = dpg.add_slider_int(label="Exp (µs)", default_value=22, min_value=22, max_value=41447, callback= self.update_exp2)
                with dpg.group(horizontal=True):
                    self.exposure_cam2_entry = dpg.add_input_text()
                    dpg.add_button(label="Set Exposure", callback=self.set_cam2_exp)
                self.ag2 = dpg.add_slider_int(label="Sensor Gain", default_value=0, min_value=1, max_value=480, callback=self.update_PGAgain2)
            
            with dpg.window(label="Save Options", width=400, height=100, pos= [0,423], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win4: # Create the Dear PyGui window
                    self.num_pic_avg = dpg.add_combo(items=self.num_avgs, width = 150, label="Number of average images per save") # add callback function
                    dpg.set_value(self.num_pic_avg, self.num_avgs[0])
                    with dpg.group(horizontal=True):
                        self.folder_name = dpg.add_input_text(label="Folder name")
                        self.save_button = dpg.add_button(label="Save Images", callback=self.save)
    
            with dpg.window(label="Statistics Cam 1", width=400, height=120, pos= [0,524], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win5: 
                self.sat_label1 = dpg.add_text("Image Saturation: NaN | Norm Mean: NaN")
                self.fps_label1 = dpg.add_text("Acquisition FPS: NaN")    
                self.temp_label1 = dpg.add_text("Camera Sensor Temperature: NaN")

            with dpg.window(label="Statistics Cam 2", width=400, height=120, pos= [0,645], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win6: 
                self.sat_label2 = dpg.add_text("Image Saturation: NaN | Norm Mean: NaN")
                self.fps_label2 = dpg.add_text("Acquisition FPS: NaN")    
                self.temp_label2 = dpg.add_text("Camera Sensor Temperature: NaN")

            empty_image = np.array([0, 0, 0], dtype=np.float32) # Create a numpy array with black color (RGB format)
            self.h, self.w = int(self.hh/4), int(self.ww//4)
            texture_data = np.tile(empty_image, (self.h * self.w)) # Repeat the black color to fill the entire texture
            
            with dpg.texture_registry() as self.win7:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="texture_tag_1")
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="texture_tag_2")
            
            with dpg.window(label="Real Time Viewer Cam 1", width=self.w+30, height=self.h+40, pos = [401,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win8:  # Create a window for the image display
                dpg.add_image("texture_tag_1")
            
            with dpg.window(label="Real Time Viewer Cam 2", width=self.w+30, height=self.h+40, pos = [1048,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win9:  # Create a window for the image display
                dpg.add_image("texture_tag_2")    
        
        elif state == 'pol':
            try:
                dpg.delete_item(self.win2)
                dpg.delete_item(self.win3)
                dpg.delete_item(self.win4)
                dpg.delete_item(self.win5)
            except AttributeError:
                pass

            with dpg.window(label="Camera 1 Control", width=400, height=160, pos= [0,101], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win10: # Create the Dear PyGui window
                self.fps_slider = dpg.add_slider_int(label="FPS", default_value=24, min_value=1, max_value=24)
                with dpg.group(horizontal=True):
                    self.button = dpg.add_button(label="Start Camera 1", callback=self.toggle_camera1) 
                    self.status_label = dpg.add_text("Cam 1 Status: Off")
                self.exp_slider = dpg.add_slider_int(label="Exp (µs)", default_value=22, min_value=22, max_value=41447, callback= self.update_exp1)
                with dpg.group(horizontal=True):
                    self.exposure_cam1_entry = dpg.add_input_text()
                    dpg.add_button(label="Set Exposure", callback=self.set_cam1_exp)
                self.ag = dpg.add_slider_int(label="Sensor Gain", default_value=0, min_value=1, max_value=480, callback=self.update_PGAgain1)  

            with dpg.window(label="Camera 2 Control", width=400, height=160, pos= [0,262], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win11: # Create the Dear PyGui window
                self.fps_slider2 = dpg.add_slider_int(label="FPS", default_value=24, min_value=1, max_value=24)
                with dpg.group(horizontal=True):
                    self.button2 = dpg.add_button(label="Start Camera 2", callback=self.toggle_camera2) 
                    self.status_label2 = dpg.add_text("Cam 2 Status: Off")
                self.exp_slider2 = dpg.add_slider_int(label="Exp (µs)", default_value=22, min_value=22, max_value=41447, callback= self.update_exp2)
                with dpg.group(horizontal=True):
                    self.exposure_cam2_entry = dpg.add_input_text()
                    dpg.add_button(label="Set Exposure", callback=self.set_cam2_exp)
                self.ag2 = dpg.add_slider_int(label="Sensor Gain", default_value=0, min_value=1, max_value=480, callback=self.update_PGAgain2)
            
            with dpg.window(label="Save Options", width=400, height=100, pos= [0,423], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win12: # Create the Dear PyGui window
                    self.num_pic_avg = dpg.add_combo(items=self.num_avgs, width = 150, label="Number of average images per save") # add callback function
                    dpg.set_value(self.num_pic_avg, self.num_avgs[0])
                    with dpg.group(horizontal=True):
                        self.folder_name = dpg.add_input_text(label="Folder name")
                        self.save_button = dpg.add_button(label="Save Images", callback=self.save)
            
            with dpg.window(label="Statistics Cam 1", width=400, height=190, pos= [0,524], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win13:
                self.sat_label0 = dpg.add_text("H-SOP Image Saturation: NaN | Norm Mean: NaN")   
                self.sat_label1 = dpg.add_text("v-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label2 = dpg.add_text("P-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label3 = dpg.add_text("M-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.fps_label = dpg.add_text("Acquisition FPS: NaN")  
                self.temp_label = dpg.add_text("Camera Sensor Temperature: NaN")
            
            with dpg.window(label="Statistics Cam 2", width=400, height=200, pos= [0,715], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win14:                  
                self.sat_label02 = dpg.add_text("H-SOP Image Saturation: NaN | Norm Mean: NaN")   
                self.sat_label12 = dpg.add_text("v-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label22 = dpg.add_text("P-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label32 = dpg.add_text("M-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.fps_label2= dpg.add_text("Acquisition FPS: NaN")  
                self.temp_label2 = dpg.add_text("Camera Sensor Temperature: NaN")
            
            empty_image = np.array([0, 0, 0], dtype=np.float32) # Create a numpy array with black color (RGB format)
            self.h, self.w = int(self.hh/8), int(self.ww//8)
            texture_data = np.tile(empty_image, (self.h * self.w)) # Repeat the black color to fill the entire texture
            
            with dpg.texture_registry() as self.win15:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="H SOP Cam 1")
            with dpg.window(label="H SOP Image Cam 1", width=self.w+30, height=self.h+40, pos = [401,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win16:  # Create a window for the image display
                dpg.add_image("H SOP Cam 1") 
            with dpg.texture_registry() as self.win17:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="V SOP Cam 1")
            with dpg.window(label="V SOP Image Cam 1", width=self.w+30, height=self.h+40, pos = [401,self.h+41], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win18:  # Create a window for the image display
                dpg.add_image("V SOP Cam 1")
            with dpg.texture_registry() as self.win19:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="P SOP Cam 1")
            with dpg.window(label="P SOP Image Cam 1", width=self.w+30, height=self.h+40, pos = [self.w+431,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win20:  # Create a window for the image display
                dpg.add_image("P SOP Cam 1")
            with dpg.texture_registry() as self.win21:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="M SOP Cam 1")
            with dpg.window(label="M SOP Image Cam 1", width=self.w+30, height=self.h+40, pos = [self.w+431,self.h+41], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win22:  # Create a window for the image display
                dpg.add_image("M SOP Cam 1")
            
            with dpg.texture_registry()  as self.win23:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="H SOP Cam 2")
            with dpg.window(label="H SOP Image Cam 2", width=self.w+30, height=self.h+40, pos = [1076,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win24:  # Create a window for the image display
                dpg.add_image("H SOP Cam 2") 
            with dpg.texture_registry()  as self.win25:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="V SOP Cam 2")
            with dpg.window(label="V SOP Image Cam 2", width=self.w+30, height=self.h+40, pos = [1076,self.h+41], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win26:  # Create a window for the image display
                dpg.add_image("V SOP Cam 2")
            with dpg.texture_registry() as self.win27:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="P SOP Cam 2")
            with dpg.window(label="P SOP Image Cam 2", width=self.w+30, height=self.h+40, pos = [self.w+1105,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win28:  # Create a window for the image display
                dpg.add_image("P SOP Cam 2")
            with dpg.texture_registry() as self.win29:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="M SOP Cam 2")
            with dpg.window(label="M SOP Image Cam 2", width=self.w+30, height=self.h+40, pos = [self.w+1105,self.h+41], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win30:  # Create a window for the image display
                dpg.add_image("M SOP Cam 2") 
        
        elif state == 'stereo':
            try:
                # delete raw-mode windows
                dpg.delete_item(self.win1)
                dpg.delete_item(self.win2)
                dpg.delete_item(self.win3)
                dpg.delete_item(self.win4)
                dpg.delete_item(self.win5)

                # shares these windows with pol-mode, but need to regenerate upon mode switch
                dpg.delete_item(self.win6)
                dpg.delete_item(self.win7)

                # delete pol-mode windows
                dpg.delete_item(self.win8)
                dpg.delete_item(self.win9)
                dpg.delete_item(self.win10)
                dpg.delete_item(self.win11)
                dpg.delete_item(self.win12)
                dpg.delete_item(self.win13)
                dpg.delete_item(self.win14)
                dpg.delete_item(self.win15)
                dpg.delete_item(self.win16)
                dpg.delete_item(self.win17)
                dpg.delete_item(self.win18)
                dpg.delete_item(self.win19)
                dpg.delete_item(self.win20)
                dpg.delete_item(self.win21)
                dpg.delete_item(self.win22)
                dpg.delete_item(self.win23)
            except AttributeError:
                pass

            # TODO: Configure STEREO Windows and add new function accordingly

            with dpg.window(label="Stereo Calibration", width=400, height=100, pos= [0,101], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win31: # Create the Dear PyGui window
                    self.cal_rate = dpg.add_combo(items=self.time_btwn_captures, width = 150, label="Time Between Captures") # add callback function
                    dpg.set_value(self.cal_rate, self.time_btwn_captures[0])
                    with dpg.group(horizontal=True):
                        self.calibration_status = dpg.add_input_text(label="LOADING BAR...") # ADD PROGRESS BAR
                        self.calibration_start_button = dpg.add_button(label="Start", callback=self.save)

            with dpg.window(label="Stereo Camera Control", width=400, height=160, pos= [0,202], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win32: # Create the Dear PyGui window
                self.fps_slider = dpg.add_slider_int(label="FPS", default_value=24, min_value=1, max_value=24)
                with dpg.group(horizontal=True):
                    self.button = dpg.add_button(label="Start Camera 1", callback=self.toggle_camera1) 
                    self.status_label = dpg.add_text("Cam 1 Status: Off")
                self.exp_slider = dpg.add_slider_int(label="Exp (µs)", default_value=22, min_value=22, max_value=41447, callback= self.update_exp1)
                with dpg.group(horizontal=True):
                    self.exposure_cam1_entry = dpg.add_input_text()
                    dpg.add_button(label="Set Exposure", callback=self.set_cam1_exp)
                self.ag = dpg.add_slider_int(label="Sensor Gain", default_value=0, min_value=1, max_value=480, callback=self.update_PGAgain1)

            
            with dpg.window(label="Save Options", width=400, height=100, pos= [0,363], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win33: # Create the Dear PyGui window
                    self.num_pic_avg = dpg.add_combo(items=self.num_avgs, width = 150, label="Number of average images per save") # add callback function
                    dpg.set_value(self.num_pic_avg, self.num_avgs[0])
                    with dpg.group(horizontal=True):
                        self.folder_name = dpg.add_input_text(label="Folder name")
                        self.save_button = dpg.add_button(label="Save Images", callback=self.save)

            # TODO: Create Stats windows for polarized data from each camera
            with dpg.window(label="Statistics Cam 1", width=400, height=190, pos= [0,464], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win34:
                self.sat_label0 = dpg.add_text("H-SOP Image Saturation: NaN | Norm Mean: NaN")   
                self.sat_label1 = dpg.add_text("v-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label2 = dpg.add_text("P-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label3 = dpg.add_text("M-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.fps_label = dpg.add_text("Acquisition FPS: NaN")  
                self.temp_label = dpg.add_text("Camera Sensor Temperature: NaN")
            
            with dpg.window(label="Statistics Cam 2", width=400, height=200, pos= [0,655], no_close=True, no_move=True, no_collapse=True, no_resize=True) as self.win35:                  
                self.sat_label02 = dpg.add_text("H-SOP Image Saturation: NaN | Norm Mean: NaN")   
                self.sat_label12 = dpg.add_text("v-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label22 = dpg.add_text("P-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.sat_label32 = dpg.add_text("M-SOP Image Saturation: NaN | Norm Mean: NaN")  
                self.fps_label2= dpg.add_text("Acquisition FPS: NaN")  
                self.temp_label2 = dpg.add_text("Camera Sensor Temperature: NaN")

            empty_image = np.array([0, 0, 0], dtype=np.float32) # Create a numpy array with black color (RGB format)
            self.h, self.w = int(self.hh/4), int(self.ww//4)
            texture_data = np.tile(empty_image, (self.h * self.w)) # Repeat the black color to fill the entire texture
            
            with dpg.texture_registry() as self.win36:
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="texture_tag_1")
                dpg.add_raw_texture(width=self.w, height=self.h, default_value=texture_data, format= dpg.mvFormat_Float_rgb, tag="texture_tag_2")
            with dpg.window(label="Real Time Viewer Cam 1", width=self.w+30, height=self.h+40, pos = [401,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win37:  # Create a window for the image display
                dpg.add_image("texture_tag_1")
            with dpg.window(label="Real Time Viewer Cam 2", width=self.w+30, height=self.h+40, pos = [1048,0], no_close=True,no_move=True, no_collapse=True, no_resize=True) as self.win38:  # Create a window for the image display
                dpg.add_image("texture_tag_2") 
    
    def set_depth(self):
        self.bit = dpg.get_value(self.bitdepth)
        if self.bit:
            if self.bit == '8':
                dpg.configure_item(self.fps_slider, max_value=24)
                dpg.configure_item(self.fps_slider2, max_value=24)
            elif self.bit == '12':
                dpg.configure_item(self.fps_slider, max_value=12)
                dpg.configure_item(self.fps_slider2, max_value=12)
    
    
    def set_mode(self):
        self.mode = dpg.get_value(self.get_mode)
        if self.mode:
            self.setup_state(self.mode)
            self.cam1.mode_and_depth(self.mode,self.bit) 
            self.cam2.mode_and_depth(self.mode,self.bit)         
    
    
    def run(self):
        while dpg.is_dearpygui_running():
            if self.cam1 is not None and self.cam2 is not None:
                if not self.cam1.is_running():
                    self.update_flag1 = False
                    self.i = 0
                else:
                    self.update_flag1 = True
                    self.update('')
                if not self.cam2.is_running():
                    self.update_flag2 = False
                    self.i = 0
                else:
                    self.update_flag2 = True
                    self.update(2)
                if self.save_ctrl:
                    if self.update_flag1:
                        if len(self.im1_list) < int(dpg.get_value(self.num_pic_avg)):
                            self.im1_list.append(self.im)
                        elif len(self.im1_list) == int(dpg.get_value(self.num_pic_avg)):
                            self.start_save_thread(1, self.im1_list)
                            self.im1_list = []
                            self.save_ctrl = False
                    if self.update_flag2:
                        if len(self.im2_list) < int(dpg.get_value(self.num_pic_avg)):
                            self.im2_list.append(self.im2)
                        elif len(self.im2_list) == int(dpg.get_value(self.num_pic_avg)):
                            self.start_save_thread(2, self.im2_list)
                            self.im2_list = []
                            self.save_ctrl = False
            dpg.render_dearpygui_frame()            
    
    
    def toggle_camera1(self,sender):
        if self.cam1.is_running():
            self.cam1.stop()
            dpg.set_item_label(sender, "Start Camera 1")
            dpg.set_value(self.status_label, "Cam 1 Status: Off")
            self.cam1 = gigE_cam(self.ia1, self.hh,self.ww)
            self.cam1.mode_and_depth(self.mode,self.bit)
            dpg.set_value(self.exp_slider, 22)
            if self.bit == 8:
                dpg.set_value(self.fps_slider, 24)
            elif self.bit == 12:
                dpg.set_value(self.fps_slider, 12)
            dpg.set_value(self.ag, 0)
        else:
            self.update_fps1()
            self.cam1.start()
            dpg.set_item_label(sender, "Stop Camera 1")
            dpg.set_value(self.status_label, "Cam 1 Status: Running")    
    
    
    def toggle_camera2(self,sender):
        if self.cam2.is_running():
            self.cam2.stop()
            dpg.set_item_label(sender, "Start Camera 2")
            dpg.set_value(self.status_label2, "Cam 2 Status: Off")
            self.cam2 = gigE_cam(self.ia2, self.hh,self.ww)
            self.cam2.mode_and_depth(self.mode,self.bit)
            dpg.set_value(self.exp_slider2, 22)
            if self.bit == '8':
                dpg.set_value(self.fps_slider2, 24)
            elif self.bit == '12':
                dpg.set_value(self.fps_slider2, 12)
            dpg.set_value(self.ag2, 0)
        else:
            self.update_fps2()
            self.cam2.start()
            dpg.set_item_label(sender, "Stop Camera 2")
            dpg.set_value(self.status_label2, "Cam 2 Status: Running")                      
    
    
    def start_save_thread(self, num, im_list):
        params = []
        if dpg.get_value(self.op) == self.op_mode[1]:
            if self.mode == 'pol':
                params.append(self.bitdepth)
                
                if num == 1:
                    params.append(dpg.get_value(self.exp_slider))
                    params.append(dpg.get_value(self.ag))
                elif num == 2:
                    params.append(dpg.get_value(self.exp_slider2))
                    params.append(dpg.get_value(self.ag2))
                else:
                    params.append('NaN')
                    params.append('NaN')
                params.append(self.fw_pos)
                params.append(self.color_pos_set)
                params.append(self.angle)
                save_thread = singleSave(F"{dpg.get_value(self.folder_name)}_cam{num}", im_list, self.bit, self.hh, self.ww, params, "")
            
            else:
                if num == 1:
                    params.append(dpg.get_value(self.exp_slider))
                    params.append(dpg.get_value(self.ag))
                elif num == 2:
                    params.append(dpg.get_value(self.exp_slider2))
                    params.append(dpg.get_value(self.ag2))
                else:
                    params.append('NaN')
                    params.append('NaN')
                params.append(self.color_pos_set)
                save_thread = singleSave(F"{dpg.get_value(self.folder_name)}_cam{num}", im_list, self.bit, self.hh, self.ww, params, "")
            save_thread.start()
            save_thread.join()
        
        elif dpg.get_value(self.op) == self.op_mode[2]:
            params.append(self.bitdepth)
            if num == 1:
                params.append(self.exposures1[self.case_num])
                params.append(self.gains1[self.case_num])
            elif num == 2:
                params.append(self.exposures2[self.case_num])
                params.append(self.gains2[self.case_num])
            else:
                params.append('NaN')
                params.append('NaN')
            params.append(self.fw_case[self.case_num])
            params.append(self.color_pos_set)
            params.append(self.pol_rot_case[self.case_num])
            save_thread = singleSave(F"{self.cases[self.case_num]}{num}", im_list, self.bit, self.hh, self.ww, params, "calibration")
            save_thread.start()
            save_thread.join()
        
        elif dpg.get_value(self.op) == self.op_mode[3]:
            params.append(self.bitdepth)
            if num == 1:
                params.append(self.exposures1[self.case_num])
                params.append(self.gains1[self.case_num])
            elif num == 2:
                params.append(self.exposures2[self.case_num])
                params.append(self.gains2[self.case_num])
            else:
                params.append('NaN')
                params.append('NaN')
            params.append(self.fw_case[self.case_num])
            params.append(self.color_pos_set)
            params.append(self.pol_rot_case[self.case_num])
            save_thread = singleSave(F"{self.cases[self.case_num]}{num}", im_list, self.bit, self.hh, self.ww, params, "study")
            save_thread.start()
            save_thread.join()
    
    
    def save(self):
        if self.cam1.is_running():
            self.im1_list = []
        if self.cam2.is_running():
            self.im2_list = []
        self.save_ctrl = True        
    
    
    def update(self, num):
        if num == 2:
            if not self.update_flag2:  # Stop updating if the flag is False
                return
            else:
                data_packet = self.cam2.get_latest_image()
        else:
            if not self.update_flag1:  # Stop updating if the flag is False
                return
            else:
                data_packet = self.cam1.get_latest_image()
        
        if self.mode == 'raw':
            if data_packet:
                fps = to_truncated_float(data_packet[1])
                temp = to_truncated_float(data_packet[2]) 
                sat = to_truncated_float(data_packet[3]) 
                norm_mean = to_truncated_float(data_packet[5]) 
                
                if num == 2:
                    self.im2 = np.array(data_packet[4]) if data_packet[4] is not None else False
                    dpg.set_value(self.fps_label2, f'FPS: {fps}')
                    dpg.set_value(self.sat_label2,f'Image Saturation: {sat} % | Norm Mean: {norm_mean}')
                    dpg.set_value(self.temp_label2,f'Camera Sensor Temperature: {temp} °C')
                    
                    if data_packet[0] is not None:    
                        dpg.set_value("texture_tag_2", self.cam2.gray2rgb_float(self.cam2.resize_im(data_packet[0],self.w,self.h))) # Update the texture 
                
                else:
                    self.im = np.array(data_packet[4]) if data_packet[4] is not None else False
                    dpg.set_value(self.fps_label1, f'FPS: {fps}')
                    dpg.set_value(self.sat_label1,f'Image Saturation: {sat} % | Norm Mean: {norm_mean}')
                    dpg.set_value(self.temp_label1,f'Camera Sensor Temperature: {temp} °C')
                    
                    if data_packet[0] is not None:    
                        dpg.set_value("texture_tag_1", self.cam1.gray2rgb_float(self.cam1.resize_im(data_packet[0],self.w,self.h))) # Update the texture     
        
        elif self.mode == 'pol':
            if data_packet:
                fps = to_truncated_float(data_packet[4]) if data_packet[4] is not None else 'NaN'
                temp = to_truncated_float(data_packet[5]) if data_packet[5] is not None else 'NaN'
                sat_h = to_truncated_float(data_packet[6]) if data_packet[6] is not None else 'NaN'
                sat_v = to_truncated_float(data_packet[7]) if data_packet[7] is not None else 'NaN'
                sat_p = to_truncated_float(data_packet[8]) if data_packet[8] is not None else 'NaN'
                sat_m = to_truncated_float(data_packet[9]) if data_packet[9] is not None else 'NaN'
                norm_h = to_truncated_float(data_packet[11]) if data_packet[11] is not None else 'NaN'
                norm_v = to_truncated_float(data_packet[12]) if data_packet[12] is not None else 'NaN'
                norm_p = to_truncated_float(data_packet[13]) if data_packet[13] is not None else 'NaN'
                norm_m = to_truncated_float(data_packet[14]) if data_packet[14] is not None else 'NaN'
                
                if num == 2:
                    self.im2 = np.array(data_packet[10]) if data_packet[10] is not None else False
                    dpg.set_value(self.fps_label2, f'FPS: {fps}')
                    dpg.set_value(self.temp_label2,f'Camera Sensor Temperature: {temp} °C')
                    dpg.set_value(self.sat_label02,f'H-SOP Image Saturation: {sat_h} % | Norm Mean: {norm_h}')
                    dpg.set_value(self.sat_label12,f'V-SOP Image Saturation: {sat_v} % | Norm Mean: {norm_v}')
                    dpg.set_value(self.sat_label22,f'P-SOP Image Saturation: {sat_p} % | Norm Mean: {norm_p}')
                    dpg.set_value(self.sat_label32,f'M-SOP Image Saturation: {sat_m} % | Norm Mean: {norm_m}')
                    
                    if data_packet[0] is not None:
                        dpg.set_value("H SOP Cam 2", self.cam2.gray2rgb_float(self.cam2.resize_im(data_packet[0],self.w,self.h))) # Update the texture
                        dpg.set_value("V SOP Cam 2", self.cam2.gray2rgb_float(self.cam2.resize_im(data_packet[1],self.w,self.h))) # Update the texture
                        dpg.set_value("P SOP Cam 2", self.cam2.gray2rgb_float(self.cam2.resize_im(data_packet[2],self.w,self.h))) # Update the texture
                        dpg.set_value("M SOP Cam 2", self.cam2.gray2rgb_float(self.cam2.resize_im(data_packet[3],self.w,self.h))) # Update the texture
                else:
                    self.im = np.array(data_packet[10]) if data_packet[10] is not None else False
                    dpg.set_value(self.fps_label, f'FPS: {fps}')
                    dpg.set_value(self.temp_label,f'Camera Sensor Temperature: {temp} °C')
                    dpg.set_value(self.sat_label0,f'H-SOP Image Saturation: {sat_h} % | Norm Mean: {norm_h}')
                    dpg.set_value(self.sat_label1,f'V-SOP Image Saturation: {sat_v} % | Norm Mean: {norm_v}')
                    dpg.set_value(self.sat_label2,f'P-SOP Image Saturation: {sat_p} % | Norm Mean: {norm_p}')
                    dpg.set_value(self.sat_label3,f'M-SOP Image Saturation: {sat_m} % | Norm Mean: {norm_m}')
                    
                    if data_packet[0] is not None:
                        dpg.set_value("H SOP Cam 1", self.cam1.gray2rgb_float(self.cam1.resize_im(data_packet[0],self.w,self.h))) # Update the texture
                        dpg.set_value("V SOP Cam 1", self.cam1.gray2rgb_float(self.cam1.resize_im(data_packet[1],self.w,self.h))) # Update the texture
                        dpg.set_value("P SOP Cam 1", self.cam1.gray2rgb_float(self.cam1.resize_im(data_packet[2],self.w,self.h))) # Update the texture
                        dpg.set_value("M SOP Cam 1", self.cam1.gray2rgb_float(self.cam1.resize_im(data_packet[3],self.w,self.h))) # Update the texture
    
    
    def update_fps1(self):
        data = int(dpg.get_value(self.fps_slider))
        dpg.configure_item(self.exp_slider, max_value=(10**(6))*(int(data)**(-1.001))-100)
        self.cam1.setFps(data)
    
    
    def update_fps2(self):
        data = int(dpg.get_value(self.fps_slider2))
        dpg.configure_item(self.exp_slider2, max_value=(10**(6))*(int(data)**(-1.001))-100)
        self.cam2.setFps(data)           
    
    
    def update_exp1(self, sender, data):
        if self.cam1.is_running():
            self.cam1.setExp(data) 
    
    
    def update_exp2(self, sender, data):
        if self.cam2.is_running():
            self.cam2.setExp(data)                    
    
    
    def set_cam1_exp(self):
        self.cam1_exp_txt_box = dpg.get_value(self.exposure_cam1_entry)
        dpg.set_value(self.exp_slider, float(self.cam1_exp_txt_box))
        self.cam1.setExp(self.cam1_exp_txt_box)
    
    
    def set_cam2_exp(self):
        self.cam2_exp_txt_box = dpg.get_value(self.exposure_cam2_entry)
        dpg.set_value(self.exp_slider2, float(self.cam2_exp_txt_box))
        self.cam2.setExp(self.cam2_exp_txt_box)
    
    
    def update_PGAgain1(self, sender, data):
        if self.cam1.is_running():
            self.cam1.set_PGAgain(data)
    
    
    def update_PGAgain2(self, sender, data):
        if self.cam2.is_running():
            self.cam2.set_PGAgain(data)
    
    
    def message_box(self, title, message):
        root = tk.Tk()
        root.withdraw() # Hide the main Tkinter window
        root.iconbitmap('icon.ico')
        mb.showinfo(title, message)
        root.destroy()
    
    
    def cleanup(self):
        self.ia1.stop() 
        self.ia2.stop()
        dpg.destroy_context() # Cleanup resources   


if __name__ == "__main__": # Usage example
    ui = CameraApp()
    try:
        ui.run()
        ui.cleanup()
    except Exception as e:
        ui.message_box(title='Error!', message=e)