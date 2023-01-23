import ctypes
from grabber import *
import time
from os import system
import math
import win32gui
import win32con
import os
import cv2
import threading
import tkinter as tk
from commands import *
from listener import *
from interception import *
import win32api
from consts import *


# fov, over 290 will break shit, 
fov = 290
# lower to get more fps but worse performance
fps = 72
# list of virtual keys: https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes
# default = mouse1
aim_key = 0x01

# default = v
trigger_key = 0x12

hitbox_size = 0.6

sleep = 1

magnet_accel = 1.2

no_hud = False

right_click_key = 0x12

grabber = Grabber(
    # x and y accel. higher = faster
    x_multiplier = 0.52,
    y_multiplier = 0.22,
    # idk this shit is supposed to set the height of where u aim but I think its broken
    y_difference = 6,
    trigger_sleep = sleep

)




left, top = (GetSystemMetrics(0) - fov) // 2, (GetSystemMetrics(1)- fov) // 2
right, bottom = left + fov, top + fov
region = (left, top, right, bottom)
time.sleep(1)
camera = dxcam.create(region=region, output_color="BGR")
camera.start(target_fps=fps)

grabber.find_dimensions(fov)
random_title = grabber.build_title(20)
system('title ' + f"'{random_title}'")
system('cls')

print(f'box_size = {grabber.box_size}')
print(f'random_title = {random_title}')
print(f"x accel = {grabber.x_multiplier}")
print(f"y accel = {grabber.y_multiplier}")

#################################################################################################

com = Commands()

while True:   
    og = np.array(camera.get_latest_frame())
    threading.Thread(target = grabber.frame_show(og), args = [og])
    if grabber.is_activated(aim_key):
        frame = grabber.process_frame(og)
        contours = grabber.detect_contours(frame, 700)
        if contours:
           rec, x, y = grabber.biggest_target(contours)            
           #x, y = grabber.closest_target(contours)
           if no_hud:
               com.no_hud()
               grabber.move_mouse(x, y)
               com.no_hud
           else:
                grabber.move_mouse(x, y)


    #if grabber.is_activated(trigger_key):
    #    frame = grabber.process_frame(og)
    #    contours = grabber.detect_contours(frame, 500)
    #    if contours:            
    #        if grabber.on_target(contours, hitbox_size):
    #           grabber.click()



