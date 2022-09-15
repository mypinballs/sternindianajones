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
import serial
from procgame import config

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

    def __init__(self,game):
        self.log = logging.getLogger('ij.rgb_led_dmd')
        self.log.info( "Init RGB Led DMD Matrix Control")
        
        self.game=game
        self.ser = serial.Serial()
        #self.ser.setPort("/dev/tty.usbmodem1411")
        self.ser.port = config.value_for_key_path('dmd_serial_port')
        self.ser.baudrate = 2500000#57600 #teensy will use max speed of usb port

        #extra setup
        #self.ser.bytesize = 8
        #self.ser.parities = 0
        #self.ser.stopbits = 1
        #self.ser.xonxoff = 0
        #self.ser.rtscts = 0
        self.ser.timeout = 0.1

        #setup transmission vars
        self.terminating_char = "\n"
        self.acknowlegde_char = "k"
        self.packet_queue = []
        self.packet_manager_running = False
        self.packet_sent = False

        self.time_delay=0.01


        self.connect()
        #create the colour palette
        self.create_colours()
     

    def connect(self):
        try:
            self.ser.open()
            self.log.info("Communication Established to Teensy RGB DMD Controller")
        except serial.SerialException as e:
            self.log.error("No Connection to Teensy Board - Is it Plugged in?. Error is:"+str(e))


    def comms_status(self):
        if self.ser.isOpen():
            return "Established v"+self.version()
        else:
            return "Failed"


    def create_colours(self):
        
        #indy jones colour palette 15 colours plus black & white
        #starred colours are different from ccc colour palette
        
        self.colors = [[0,0,0], # blank/black
                      [147,147,147], # color 1 grey
                      [239,180,49], # color 2 sand *
                      [234,226,147], # color 3 light orange *
                      [244,184,168], # color 4 flesh tone
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
                 
        frame_string = frame.get_data()
            
        x = 0
        y = 0
            
        #create the data list
        self.data = []
        #add the usb command data
        self.data.extend([0xBA,0x11,0x00,0x03,0x04,0x00,0x00,0x00])
            
        for index,dot in enumerate(frame_string):
            dot_value = ord(dot)
                
            # set the brightness and color
            #low 4 bits
            brightness = (dot_value&0xf)
            
            # if we have a brightness but no color - use white
            if brightness and (dot_value >>4) == 0:
                color = 16
            # otherwise, find the color 
            #upper 4 bits
            else: 
                color = (dot_value >> 4)
                
            #now, set the brightness
            if brightness <= 1: #3
                bright_value = 0
            elif brightness <= 6: #8
                bright_value = 1
            elif brightness <= 11: #13
                bright_value = 2
            else:
                bright_value = 3 
                
            global_brightness = (bright_value/3.0)*self.get_global_brightness()
                
                 
            #add the frame dot data as RGB values for each dot
            self.data.extend([int(self.colors[color][0]*global_brightness),int(self.colors[color][2]*global_brightness),int(self.colors[color][1]*global_brightness)])
            
            del color
            del bright_value  
            del dot
            del dot_value
            del brightness

            x += 1
                
            if x == 128:
                x = 0
                y += 1

            
        #send the frame as serial data
        #self.log.info('frame data to send:%s',self.data)
        self.ser.write(bytearray(self.data))
        #self.log.info('frame data sent')
             
        
        del x
        del y
        del frame_string
        
        
    def get_global_brightness(self):
        
        brightness = self.game.user_settings['Display']['RGB DMD Brightness']
        value= 0.35+(brightness/100.0)*0.55 #set the global brightness scale. This allows for the dim dmd dots to be still visible at lowest global setting
        
        return value

           
        

#    def __str__(self):
#        return '<Desktop pygame>'

