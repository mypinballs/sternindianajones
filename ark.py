# Ark Mech Logic
# ----------------
# Copyright (C) 2015 myPinballs, Orange Cloud Software Ltd

import procgame
import locale
import audits
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
            self.ark_state="boot" #ark states are boot, initialise, empty, reload, full
            self.ark_moving = False
            self.ark_load_in_progress = False
            
            
        def reset(self):
            #force an emply and relaod cycle
            self.ark_state="initialise"
            self.open_ark()


        def mode_started(self):
            #load the ark balls game counter
            self.balls_in_ark = audits.display(self.game,'general','arkBallsCounter')
            self.log.info('Balls In Ark:%s',self.balls_in_ark)
            #init the ark
            self.initialise()


        def mode_tick(self):
            pass
        
        
        def initialise(self):
            if self.balls_in_ark ==self.balls_max:
                 self.ark_state="full"
            elif self.ark_state=="boot":
                self.log.info('Balls in Ark is different to what is expected, Initialising Ark') 
                self.ark_state="initialise"
                self.open_ark() # force a reload of balls to set the vars
                
                
        def num_balls(self):
            return self.balls_in_ark
                

        def load_ball_start(self): #add a check of at least one ball at trough1 position and settled, before trough launch???
            if self.balls_in_ark <self.balls_max:
                self.ark_load_in_progress = True
                
                #only launch a ball if the trough has at least 1 ball in the correct place, otherwise wait 1sec and try again
                #this is only needed really when the trough is filling at unkown intervals during multiball
                if self.game.switches.trough1.is_active(0.25):
                    self.game.trough.launch_balls(1,callback=self.launch_callback,stealth=True) #stealth true, bip not altered on launch
                else:
                    self.delay(name='load_ball_start_wait',delay=1,handler=self.load_ball_start)
                   
        def load_ball_in_progress(self):
            self.game.coils.arkDivertor.patter(2,20,self.game.coils.arkDivertor.default_pulse_time,True)
            self.game.coils.ballLaunch.pulse()
            
                
        def launch_callback(self):
            #self.delay(delay=0.5, handler=self.load_ball_in_progress)
            if self.game.switches.shooterLane.is_active(0.5):
                self.load_ball_in_progress()
            else:
                self.cancel_delayed('launch_callback_wait')
                self.delay(name='launch_callback_loop',delay=0.25, handler=self.launch_callback)
            
            
        def load_complete(self):
            self.game.coils.arkDivertor.disable()
            self.ark_load_in_progress = False
            self.balls_in_ark +=1
            #update the ark balls game counter
            audits.update_counter(self.game,'arkBalls',self.balls_in_ark)
            self.log.debug('Ark Load Complete. Balls in Ark Now: %s',self.balls_in_ark)
            
            if self.balls_in_ark ==self.balls_max:
                 self.ark_state="full"
            else:
                self.load_ball_start()
            
            
        def empty(self):
            if self.ark_state == "full":
                self.ark_state="empty"
                self.open_ark()
            else:
                self.log.debug("Problem with Ark! Can't Empty")
            
        
        def open_ark(self):
            #if self.game.switches.arkMotorDown.is_active():    
            self.motor()
                
                            
        def close_ark(self):
            #if self.game.switches.arkMotorUp.is_active():
            self.motor()
             
                
        def motor(self,enable=True):
            if enable:
                self.game.coils.arkMotor.enable()
                self.ark_moving = True
            else:
                self.game.coils.arkMotor.disable()
                self.ark_moving = False

        #---------------------
        #switch handlers
        #---------------------
        
        def sw_arkEnter_active(self, sw):
            self.load_complete()
            
        def sw_arkMotorDown_active(self,sw):
            self.log.debug('Ark is Closed') 
            self.motor(False)
            
            if self.ark_state=="empty":
                self.ark_state = "reload"
            elif self.ark_state=="initialise":
                self.load_ball_start()
        
        def sw_arkMotorUp_active(self,sw):
            self.log.debug('Ark is Open') 
            self.motor(False)
            
            if self.ark_state=="empty" or self.ark_state=="initialise":
                self.balls_in_ark =0
                #update the ark balls game counter
                audits.update_counter(self.game,'arkBalls',self.balls_in_ark)
                self.delay(delay=0.5, handler=self.close_ark)
                