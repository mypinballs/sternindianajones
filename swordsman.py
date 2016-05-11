# Swordsman Mech Logic
# ----------------
# Copyright (C) 2016 myPinballs, Orange Cloud Software Ltd

import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Swordsman(game.Mode):

	def __init__(self, game, priority):
            super(Swordsman, self).__init__(game, priority)

            self.log = logging.getLogger('ij.swordsman')
            self.swordsman_state="boot"
            self.swordsman_moving = False
            self.cycle_flag = False
            
            
        def reset(self):
            pass


        def mode_started(self):
            self.close()
            

        def mode_tick(self):
            pass
        
        def get_state(self):
            return self.swordsman_state
        
 
        def open(self):
            if self.swordsman_state != "open":
                self.swordsman_state = "opening"
                self.log.debug('Swordsman is Opening')
                self.motor()
            else:
                self.log.debug('Swordsman is Open. No need to Move') 
                self.swordsman_state = "open"
                
                
        def close(self):           
            if self.swordsman_state != "closed":
                self.swordsman_state = "closing"
                self.log.debug('Swordsman is Closing')
                self.motor()
            else:
                self.log.debug('Swordsman is Closed. No need to Move') 
                self.swordsman_state = "closed"
                
        
        def cycle_swordsman(self,enable=True): 
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
                self.game.coils.swordsmanMotor.enable()
                self.log.debug('Motor is on')
            else:
                self.game.coils.swordsmanMotor.disable()
                self.log.debug('Motor is off')
                
           

                
        #switch handlers
        def sw_swordsmanBack_active(self,sw):
            
            if self.swordsman_state=="closing":
                self.motor(False)
                self.swordsman_state = "closed"
            
            if self.cycle_flag:
                self.delay(delay=0.5, handler=self.open)
#            else:
#                self.swordsman_state = "closed"
                
            self.log.info('Swordsman Back Switch is active, State is:%s',self.swordsman_state)
            
        
        def sw_swordsmanForward_active(self,sw):
            
            if self.swordsman_state=="opening":
                self.motor(False)
                self.swordsman_state = "open"
            
            if self.cycle_flag:
                self.delay(delay=0.5, handler=self.close)
#            else:
#                self.swordsman_state = "open"
            
            self.log.info('Swordsman Forward Switch is active, State is:%s',self.swordsman_state)