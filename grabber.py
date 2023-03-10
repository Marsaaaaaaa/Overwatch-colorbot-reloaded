from commands import *
import cv2
import win32api
import numpy as np
import threading
import time
import random
import dxcam
from numba import *
import win32con
from win32api import GetSystemMetrics
import pyautogui


class Grabber:
    def __init__(self, x_multiplier, y_multiplier, y_difference, trigger_sleep) -> None:
        # self.lower = np.array([139, 96, 129], np.uint8)
        # self.upper = np.array([169, 255, 255], np.uint8)
        self.lower = np.array([139, 95, 144], np.uint8)
        self.upper = np.array([153, 255, 255], np.uint8)
        self.x_multiplier = x_multiplier         # multiplier on x-coordinate
        self.y_multiplier = y_multiplier         # multiplier on y-coordinate
        self.y_difference = y_difference         # the amount of pixels added to the y-coordinate (aims higher)
        self.sleep = trigger_sleep
        self.c = Commands()

    def build_title(self, length) -> str:
        """return a randomly generated window title to prevent detections"""
        chars = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '@', '#',
            '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '/', '?'
        ]
        return ''.join(random.choice(chars) for character in range(length))
 
    def find_dimensions(self, box_size): 
        """Calculates constants required for the bot."""
        self.screen_width = GetSystemMetrics(0)
        self.screen_height = GetSystemMetrics(1)
    
        self.box_size = box_size
        self.box_middle = int(self.box_size / 2) 
        self.y = int(((self.screen_height / 2) - (self.box_size / 2))) 
        self.x = int(((self.screen_width / 2) - (self.box_size / 2))) 
        

    def process_frame(self, frame):
        """Performs operations on a frame to improve contour detection."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        processed = cv2.inRange(hsv, self.lower, self.upper)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))
        dilatation_size = 2
        dilation_shape = cv2.MORPH_RECT
        element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                    (dilatation_size, dilatation_size))
        processed = cv2.dilate(processed, element)
        #processed = cv2.blur(processed, (8, 8))        
        return processed
    
    def check(self, a, b):
        if a > b:
            return True
        else:
            return False


    def detect_contours(self, frame, minimum_size):
        """Returns contours larger then a specified size in a frame."""
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = []
        if len(contours) != 0:
            for i in contours:
                if self.check(cv2.contourArea(i), minimum_size):
                   if cv2.contourArea(i) > minimum_size:
                       large_contours.append(i)
        return large_contours

    def scale_contour(self,cnt, scale:float, check):
        M = cv2.moments(cnt)
        x = int(M['m10']/M['m00'])
        y = int(M['m01']/M['m00'])

        center = cnt - [x, y]
        cnt_scaled = center * scale
        cnt_scaled = cnt_scaled + [x, y]
        cnt_scaled = cnt_scaled.astype(np.int32)
        if check:
            return cnt_scaled
        else: 
            return x, y

    def on_target(self, contour, hitbox):
        for c in contour:
            cont = self.scale_contour(c, hitbox, True)
            test = cv2.pointPolygonTest(cont,( self.box_middle, self.box_middle),False)
            if test >= 0:
                return True
        return False

    def biggest_target(self, contour):
        """Returns x- and y- coordinates of the center of the largest contour."""
        c = max(contour, key=cv2.contourArea)
        rectangle = np.int0(cv2.boxPoints(cv2.minAreaRect(c)))
        new_box = []
        for point in rectangle:
            point_x = point[0]
            point_y = point[1]
            new_box.append([round(point_x, -1), round(point_y, -1)])
        M = cv2.moments(np.array(new_box))
        if M['m00']:
            center_x = (M['m10'] / M['m00'])
            center_y = (M['m01'] / M['m00'])
            x = -(self.box_middle - center_x)
            y = -(self.box_middle - center_y)
            return [], x, y

    def closest_target(self, contours):
        _check =  99999        
        for c in contours:
            check = cv2.pointPolygonTest(c, ( self.box_middle, self.box_middle), True)
            if check < _check:
                closest = c.astype(np.int32)
        M = cv2.moments(closest)
        x = int(M['m10']/M['m00'])
        y = int(M['m01']/M['m00'])
        x = -(self.box_middle - x)
        y = -(self.box_middle - y)
        return x, y

        

    def smooth(self, x, y):
        yr = y
        if x > self.box_size:
            xr = -(self.screen_width/2 - x)
            if (xr + self.screen_width/2) > self.screen_width:
                xr = 0
        else:
            xr = x

        if y > self.box_size:
            yr = -(self.screen_height/2 - y)
            if (yr + self.screen_height/2) > self.screen_height:
               yr = 0
            else:
                yr = y
        xf = int(xr* self.x_multiplier)
        yf = int((yr - self.y_difference)* self.y_multiplier)
        return xf, yf

    def is_activated(self, key_code):
        if win32api.GetAsyncKeyState(key_code) & 0xFFFF:
            return True
        else:
            return False


    def move_mouse(self, x, y):
        x, y = self.smooth(x, y)
        threading.Thread(target=self._move_mouse, args=[x, y]).start()

    def _move_mouse( self, x, y):
        self.c.move_mouse(x, y)

    def mouse_right(self):
        threading.Thread(target= self._mouse_right).start()

    def _mouse_right(self):
        self.c.rclick()        

    def click(self):
        threading.Thread(target=self._click).start()

    def _click(self):        
        self.c.lclick()

    
    def frame_show(self, og):
        frame = self.process_frame(og)
        contours = self.detect_contours(frame, 700)
        cv2.drawContours(og, contours, -1, (0, 0, 0), 4)
        for c in contours:
            x, y = self.scale_contour(c, 100, False)
            cv2.drawMarker(og, (x, (y - self.y_difference)), (0, 255, 255), cv2.MARKER_CROSS, 5, 7, 8 )
            cv2.line(og, (self.box_middle, self.box_middle), (x, y - self.y_difference), (255,0,0), 1)
        cv2.imshow('frame', og)
        if (cv2.waitKey(1) & 0x2D) == ord('q'):
            cv2.destroyAllWindows()
            exit()


    


