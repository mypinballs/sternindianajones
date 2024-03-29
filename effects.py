# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import random
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"

class Effects(game.Mode):

	def __init__(self, game, priority):
            super(Effects, self).__init__(game, priority)


        def drive_lamp(self, lamp_name, style='on',time=2):
            if style == 'slow':
       		self.game.lamps[lamp_name].schedule(schedule=0x00ff00ff, cycle_seconds=0, now=True)
            elif style == 'medium':
      		self.game.lamps[lamp_name].schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            elif style == 'fast':
		self.game.lamps[lamp_name].schedule(schedule=0x99999999, cycle_seconds=0, now=True)
            elif style == 'superfast':
		self.game.lamps[lamp_name].schedule(schedule=0xaaaaaaaa, cycle_seconds=0, now=True)
            elif style == 'on':
		self.game.lamps[lamp_name].enable()
            elif style == 'off':
                self.clear_lamp_timers(lamp_name)
		self.game.lamps[lamp_name].disable()
            elif style == 'smarton':
		self.game.lamps[lamp_name].schedule(schedule=0xaaaaaaaa, cycle_seconds=0, now=True)
                self.cancel_delayed(lamp_name+'on')
                self.delay(name=lamp_name+'_on', event_type=None, delay=0.6, handler=self.game.lamps[lamp_name].enable)
            elif style == 'timedon':
		self.game.lamps[lamp_name].enable()
                self.cancel_delayed(lamp_name+'_off')
                self.delay(name=lamp_name+'_off', event_type=None, delay=time, handler=self.game.lamps[lamp_name].disable)
            elif style == 'timeout':

                if time>10:
                    self.cancel_delayed(lamp_name+'_medium')
                    self.delay(name=lamp_name+'_medium', event_type=None, delay=time-10, handler=self.drive_medium, param=lamp_name)
                if time>5:
                    self.cancel_delayed(lamp_name+'_fast')
                    self.delay(name=lamp_name+'_fast', event_type=None, delay=time-5, handler=self.drive_fast, param=lamp_name)
                if time>1:
                    self.cancel_delayed(lamp_name+'_superfast')
                    self.delay(name=lamp_name+'_superfast', event_type=None, delay=time-1, handler=self.drive_super_fast, param=lamp_name)
                self.delay(name=lamp_name+'_off', event_type=None, delay=time, handler=self.game.lamps[lamp_name].disable)
        
        def clear_lamp_timers(self,lamp_name):
            self.cancel_delayed(lamp_name+'_medium')
            self.cancel_delayed(lamp_name+'_fast')
            self.cancel_delayed(lamp_name+'_superfast')
            self.cancel_delayed(lamp_name+'on')
            self.cancel_delayed(lamp_name+'_off')

        def drive_super_fast(self, lamp_name):
            self.game.lamps[lamp_name].schedule(schedule=0x99999999, cycle_seconds=0, now=True)

        def drive_fast(self, lamp_name):
            self.game.lamps[lamp_name].schedule(schedule=0x55555555, cycle_seconds=0, now=True)

        def drive_medium(self, lamp_name):
            self.game.lamps[lamp_name].schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)


        def drive_flasher(self, data, style='medium',cycle=0,time=2):

            if isinstance(data, basestring):
                flasher_name=data
            else:
                flasher_name=data[0]
                style = data[1]
                time = data[2]
                
            self.cancel_delayed(flasher_name+'_off')
            
            if style == 'slow':
       		self.game.coils[flasher_name].schedule(schedule=0x00003000, cycle_seconds=cycle, now=True)
            elif style == 'medium':
      		self.game.coils[flasher_name].schedule(schedule=0x30003000, cycle_seconds=cycle, now=True)
            elif style == 'fast':
		self.game.coils[flasher_name].schedule(schedule=0x11111111, cycle_seconds=cycle, now=True)
            elif style == 'super':
		self.game.coils[flasher_name].schedule(schedule=0x55555555, cycle_seconds=cycle, now=True)
            elif style == 'super2':
		self.game.coils[flasher_name].schedule(schedule=0x55055055, cycle_seconds=cycle, now=True)
            elif style == 'strobe':
		self.game.coils[flasher_name].schedule(schedule=0xeeeeeeee, cycle_seconds=cycle, now=True)
            elif style == 'chaos':
		self.game.coils[flasher_name].schedule(schedule=0x019930AB, cycle_seconds=cycle, now=True)
            elif style == 'fade':
		self.game.coils[flasher_name].schedule(schedule=0xAAA99933, cycle_seconds=cycle, now=True)
            elif style == 'off':
                self.game.coils[flasher_name].disable()
            if time>0:
                self.delay(name=flasher_name+'_off', event_type=None, delay=time, handler=self.game.coils[flasher_name].disable)

#        def strobe_flasher_set(self,flasher_list,time=0.5):
#            timer = 0
#            for fname in flasher_list:
#                self.delay(name=fname+'strobe', event_type=None, delay=timer, handler=self.drive_flasher, param=[fname,'fast',time])
#                timer+=time

        def strobe_flasher_set(self,flasher_list,time=1,overlap=0.2,repeats=1,enable=True):
            timer = 0
            for i in range(repeats):
                for fname in flasher_list:
                    if enable:
                        self.delay(name=fname+'strobe', event_type=None, delay=timer, handler=self.drive_flasher, param=[fname,'fast',time+overlap])
                        timer+=time
                    else:
                        self.cancel_delayed(fname+'strobe')
                        self.game.coils[fname].disable() 
        
        
        def drive_shaker(self,style='medium',time=0.75):

            if self.game.user_settings['Machine (Standard)']['Shaker Installed'].startswith('Y'): 
                if style == 'slow':
                    num=random.randint(130,200)
                    self.game.coils['shakerMotor'].pulse(num)
                    #self.game.coils['shakerMotor'].schedule(schedule=0x00003000, cycle_seconds=0, now=True)
                elif style == 'medium':
                    #self.game.coils['shakerMotor'].schedule(schedule=0x30003000, cycle_seconds=0, now=True)
                    time=0.75
                    #self.game.coils['shakerMotor'].enable()
                    self.game.coils['shakerMotor'].patter(on_time=10,off_time=2)
                elif style == 'fast':
                    #self.game.coils['shakerMotor'].schedule(schedule=0x11111111, cycle_seconds=0, now=True)
                    time=1.2
                    #self.game.coils['shakerMotor'].enable()
                    self.game.coils['shakerMotor'].patter(on_time=10,off_time=0)
                
                self.delay(name='shaker_off', event_type=None, delay=time, handler=self.game.coils['shakerMotor'].disable)
                
                #self.delay(name='spin_wheels_repeat',delay=0.7,handler=self.drive)
            