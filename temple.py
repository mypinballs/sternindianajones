# Temple Mech Logic
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

class Temple(game.Mode):

	def __init__(self, game, priority):
            super(Temple, self).__init__(game, priority)

            self.log = logging.getLogger('ij.temple')
            self.temple_state="boot"
            self.temple_moving = False
            self.cycle_flag = False
            self.balls = 0
            
            
        def reset(self):
            pass


        def mode_started(self):
            self.close()
            

        def mode_tick(self):
            pass
        
        def get_state(self):
            return self.temple_state
        
        def get_balls(self):
            return self.balls
        
 
        def open(self):
            if self.temple_state != "open":
                self.temple_state = "opening"
                self.log.debug('Temple is Opening')
                self.motor()
            else:
                self.log.debug('Temple is Open. No need to Move') 
                self.temple_state = "open"
                
                
        def close(self):           
            if self.temple_state != "closed":
                self.temple_state = "closing"
                self.log.debug('Temple is Closing')
                self.motor()
            else:
                self.log.debug('Temple is Closed. No need to Move') 
                self.temple_state = "closed"
                
        
        def cycle_temple(self,enable=True): 
            self.cycle_flag = enable
            if enable:
                self.open()
            else:
                self.close()
        
        
        def disable(self):
            self.motor(False)
            self.cycle_flag = False
            
            
             
        def motor(self,enable=True):
            if enable:
                self.game.coils.templeMotor.enable()
                self.log.debug('Motor is on')
            else:
                self.game.coils.templeMotor.disable()
                self.log.debug('Motor is off')
                
           

                
        #switch handlers
        def sw_templeMotorDown_inactive_for_50ms(self,sw):
            
            if self.temple_state=="closing":
                self.motor(False)
                self.temple_state = "closed"
            
            if self.cycle_flag:
                self.delay(delay=0.5, handler=self.open)
#            else:
#                self.temple_state = "closed"
                
            self.log.info('Temple Motor Down Switch is inactive, State is:%s',self.temple_state)
            
        
        def sw_templeMotorUp_inactive_for_50ms(self,sw):
            
            if self.temple_state=="opening":
                self.motor(False)
                self.temple_state = "open"
            
            if self.cycle_flag:
                self.delay(delay=0.5, handler=self.close)
#            else:
#                self.temple_state = "open"
            
            self.log.info('Temple Motor Up Switch is inactive, State is:%s',self.temple_state)