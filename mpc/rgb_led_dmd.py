import sys
import procgame
import pinproc
from threading import Thread
import random
import string
import time
import locale
import math
import copy
import ctypes
import itertools
from procgame.events import EventManager
import os
import logging

from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions


#try:
#    import pygame
#    import pygame.locals
#except ImportError:
#    print "Error importing pygame; ignoring."
#    pygame = None
#
#if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
#   Py_ssize_t = ctypes.c_int
#elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
#   Py_ssize_t = ctypes.c_int64
#else:
#   raise TypeError("Cannot determine type of Py_ssize_t")
#
#PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
#PyObject_AsWriteBuffer.restype = ctypes.c_int
#PyObject_AsWriteBuffer.argtypes = [ctypes.py_object,
#                                  ctypes.POINTER(ctypes.c_void_p),
#                                  ctypes.POINTER(Py_ssize_t)]
#
#def array(surface):
#   buffer_interface = surface.get_buffer()
#   address = ctypes.c_void_p()
#   size = Py_ssize_t()
#   PyObject_AsWriteBuffer(buffer_interface,
#                          ctypes.byref(address), ctypes.byref(size))
#   bytes = (ctypes.c_byte * size.value).from_address(address.value)
#   bytes.object = buffer_interface
#   return bytes


class rgbLedDMDMatrix():
    """Sends frame data from the DMDcontroller to the RGB Led matrix panel. Uses the last_Frame method"""

#    exit_event_type = 99
#    """Event type sent when Ctrl-C is received."""
#
#    key_map = {}

    def __init__(self):
        self.log = logging.getLogger('ij.rgb_led_dmd')
        self.log.info( "Init RGB Led DMD Matrix Panel")
#        self.ctrl = 0
#        self.i = 0
#        self.HD = False
#        self.frame_data_store = ['0'] * 4096
#        #self.line_store=[]
#
#        self.add_key_map(pygame.locals.K_LSHIFT, 3)
#        self.add_key_map(pygame.locals.K_RSHIFT, 1)
        
        #configuration for the matrix
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 2
        options.parallel = 1
        options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
        options.brightness = 75
        options.show_refresh_rate = True
        options.disable_hardware_pulsing = True
        #options.gpio_slowdown = 1
        #options.daemon = 1

        #setup matrix
        self.matrix = RGBMatrix(options = options)
        self.matrix_cols = options.cols*options.chain_length
        self.matrix_rows = options.rows
        
        #create the colour palette
        self.create_colours()


    def create_colours(self):
        
        #indy jones colour palette 15 colours plus black & white
        #starred colours are different from ccc colour palette
        
        self.colors = [[0,0,0], # blank/black
                      [147,147,147], # color 1 grey
                      [239,180,49], # color 2 sand *
                      [234,226,147], # color 3 light orange *
                      [158,74,237], # color 4 flesh tone
                      [158,74,237], # color 5 purple
                      [129,17,8], # color 6 dark red
                      [197,176,80], # color 7 - brown
                      [137,106,20], # color 8 dark brown
                      [239,40,25], # color 9 - red
                      [0,214,41], # color 10 - green
                      [239,234,49], # color 11 - yellow
                      [56,100,254], # color 12 blue
                      [242,115,24], # color 13 orange
                      [2,237,239], # color 14 - cyan
                      [239,72,237], # color 15 - magenta
                      [255,255,255]] # default color - white

#    def add_key_map(self, key, switch_number):
#        """Maps the given *key* to *switch_number*, where *key* is one of the key constants in :mod:`pygame.locals`."""
#        self.key_map[key] = switch_number
#
#    def clear_key_map(self):
#        """Empties the key map."""
#        self.key_map = {}
#
#    def get_keyboard_events(self):
#        """Asks :mod:`pygame` for recent keyboard events and translates them into an array
#        of events similar to what would be returned by :meth:`pinproc.PinPROC.get_events`.#"""
#        key_events = []
#        for event in pygame.event.get():
#            EventManager.default().post(name=self.event_name_for_pygame_event_type(event.type), object=self, info=event)
#            key_event = {}
#            if event.type == pygame.locals.KEYDOWN:
#                if event.key == pygame.locals.K_RCTRL or event.key == pygame.locals.K_LCTRL:
#                    self.ctrl = 1
#                if event.key == pygame.locals.K_c:
#                    if self.ctrl == 1:
#                        key_event['type'] = self.exit_event_type
#                        key_event['value'] = 'quit'
#                elif (event.key == pygame.locals.K_ESCAPE):
#                    key_event['type'] = self.exit_event_type
#                    key_event['value'] = 'quit'
#                elif event.key in self.key_map:
#                    key_event['type'] = pinproc.EventTypeSwitchClosedDebounced
#                    key_event['value'] = self.key_map[event.key]
#            elif event.type == pygame.locals.KEYUP:
#                if event.key == pygame.locals.K_RCTRL or event.key == pygame.locals.K_LCTRL:
#                    self.ctrl = 0
#                elif event.key in self.key_map:
#                    key_event['type'] = pinproc.EventTypeSwitchOpenDebounced
#                    key_event['value'] = self.key_map[event.key]
#            if len(key_event):
#                key_events.append(key_event)
#        return key_events
#
#
#    event_listeners = {}
#
#    def event_name_for_pygame_event_type(self, event_type):
#        return 'pygame(%s)' % (event_type)


    def draw(self, frame):
        """Draw the given :class:`~procgame.dmd.Frame` in the window."""
        # Use adjustment to add a one pixel border around each dot, if
        # the screen size is large enough to accomodate it.
        frame_string = frame.get_data()
            
        x = 0
        y = 0
            
        #create the image and pixel map
        image = Image.new("RGB", (self.matrix_cols,self.matrix_rows), "black") #(0, 0, 0)
        pixels = image.load() # create the pixel map
            
        for index,dot in enumerate(frame_string):
            dot_value = ord(dot)
                
            # set the brightness and color
            brightness = (dot_value&0xf)
            
            # if we have a brightness but no color - use white
            if brightness and (dot_value >>4) == 0:
                color = 16
            # otherwise, find the color 
            else: 
                color = (dot_value >> 4)
                
            #now, set the brightness
            if brightness <= 3:
                bright_value = 0
            elif brightness <= 8:
                bright_value = 1
            elif brightness <= 13:
                bright_value = 2
            else:
                bright_value = 3 
                
            #update the pixel data
            pixels[x,y] = (int(self.colors[color][0]*(bright_value/3)),int(self.colors[color][1]*(bright_value/3)),int(self.colors[color][2]*(bright_value/3))) # set the colour accordingly
                                     
            del color
            del bright_value  
            del dot
            del dot_value
            del brightness

            x += 1
                
            if x == 128:
                x = 0
                y += 1

            
        #update the matrix with the image
        self.matrix.Clear()
        self.matrix.SetImage(image)
             
        
        del x
        del y
        del frame_string

           
        

#    def __str__(self):
#        return '<Desktop pygame>'

