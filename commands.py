
from interception import *
from win32api import GetSystemMetrics
from consts import *
import win32con
import threading
from threading import Event
import time
import ctypes

class Commands():

    def __init__(self):

        PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

        self.context = interception()      
        
        self.mouse = 0
        self.kb = 0
        print("Loading Interception")
        for i in range(MAX_DEVICES):
            if interception.is_mouse(i):
                self.mouse = i
                break

        if (self.mouse == 0):
            print("Interception failed to load - No device found")
            exit(0)

        #self.move_context.set_filter(interception.is_mouse, 
        #                             interception_filter_mouse_state.INTERCEPTION_FILTER_MOUSE_MOVE.value)

        print("Interception loaded")

    def rclick(self):
        mstroke = self.context.receive(self.mouse)        
        mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN.value
        self.lclick_context.send(self.mouse, mstroke)
        time.sleep(0.05)
        mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP.value
        self.context.send(self.mouse, mstroke)


    def lclick(self):
        mstroke = self.context.receive(self.mouse)        
        mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN.value
        self.context.send(self.mouse, mstroke)
        time.sleep(0.05)
        mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_UP.value
        self.context.send(self.mouse, mstroke)

        
    def move_mouse(self, x, y):     
        mstroke = self.context.receive(self.mouse)   
        mstroke.flags =  interception_mouse_flag.INTERCEPTION_MOUSE_MOVE_RELATIVE.value
        mstroke.x = x
        mstroke.y = y
        self.context.send(self.mouse, mstroke)


    #def no_hud(self):
    #    kstroke = self.context.receive(self.kb)
    #    kstroke.code = 0x70
    #    kstroke.state = interception_key_state.INTERCEPTION_KEY_DOWN.value
    #    self.context.send(self.kb, kstroke)
    #    time.sleep(0.05)
    #    kstroke.state = interception_key_state.INTERCEPTION_KEY_UP.value
    #    self.context.send(self.kb, kstroke)





    


