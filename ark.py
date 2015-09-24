# Ark Mech Logic
# ----------------
# Copyright (C) 2015 myPinballs, Orange Cloud Software Ltd

import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Ark(game.Mode):

	def __init__(self, game, priority):
            super(Ark, self).__init__(game, priority)

            self.log = logging.getLogger('ij.ark')
            self.balls_in_ark = 0 # make this a stored setting
            self.balls_max = int(self.game.user_settings['Gameplay (Feature)']['Max Balls in Ark'])
            self.ark_state="boot"
            self.ark_moving = False
            self.ark_load_in_progress = False
            
            
        def reset(self):
            pass


        def mode_started(self):
            self.initialise()


        def mode_tick(self):
            pass
        
        
        def initialise(self):
            if self.balls_in_ark ==self.balls_max:
                 self.ark_state="ready"
            else:
                self.log.debug('Initialising Ark') 
                self.ark_state="initialise"
                #self.empty() # force a reload of balls to set the vars
                #self.close_ark()
                
        def num_balls(self):
            return self.balls_in_ark
                

        def load_ball_start(self):
            if self.balls_in_ark <self.balls_max:
                self.game.trough.launch_balls(1,callback=self.launch_callback,stealth=True) #stealth true, bip not altered
                
                
        def load_ball_in_progress(self):
            self.game.coils.arkDivertor.patter(2,20,self.game.coils.arkDivertor.default_pulse_time,True)
            self.game.coils.ballLaunch.pulse()
            self.ark_load_in_progress = True
            
            
        def launch_callback(self):
            self.load_ball_in_progress()
            
            
        def load_complete(self):
            self.game.coils.arkDivertor.disable()
            self.ark_load_in_progress = False
            self.balls_in_ark +=1
            self.log.debug('Ark Load Complete. Balls in Ark Now: %s',self.balls_in_ark)
            
            if self.balls_in_ark ==self.balls_max:
                 self.ark_state="ready"
            
            
        def empty(self):
            self.ark_state="empty"
            self.open_ark()
            
        
        
        def open_ark(self):
            if self.game.switches.arkMotorDown.is_active():
                self.log.debug('Ark is Closed, Opening up') 
                self.motor()
                
                
        def close_ark(self):
            if self.game.switches.arkMotorUp.is_active():
                self.log.debug('Ark is open, Closing')
                self.motor()
             
                
        def motor(self,enable=True):
            if enable:
                self.game.coils.arkMotor.enable()
            else:
                self.game.coils.arkMotor.disable()


                
        #switch handlers
                
        def sw_arkAutoLoad_active_for_250ms(self, sw):
            self.load_ball_start()
            
        def sw_arkEnter_active(self, sw):
            self.load_complete()
            
        def sw_arkMotorDown_active(self,sw):
            self.motor(False)
        
        def sw_arkMotorUp_active(self,sw):
            self.motor(False)
            
            if self.ark_state=="empty":
                self.delay(delay=0.5, handler=self.close_ark)
            
            
            
