# ----------------------------------------------------------
# Spinner Mode
#
# Controls Spinner Value
#
# Copyright (C) 2016 myPinballs, Orange Cloud Software Ltd
#
# ----------------------------------------------------------

import procgame
import locale
import random
import logging
import audits
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Spinner(game.Mode):

	def __init__(self, game, priority):
            super(Spinner, self).__init__(game, priority)

            self.log = logging.getLogger('ij.spinner')

            self.game.sound.register_sound('spinner', sound_path+"ij400B8_spinner.aiff")
            #self.game.sound.register_sound('spinner', sound_path+"spinner.aiff")

            #self.flashers = ['bottomRightFlasher','rampTopFlasher','rampUMFlasher','rampLMFlasher','rampBottomFlasher']
            #var setup
            self.value = [1,2,5,10]
            self.inc_value = 10
            self.timer = 10
            self.spinner_double_timer = 2.5


        def reset(self):
            #general
            self.level = 0
            self.spins = 0
            self.spin_value=self.value[self.level]

           
        def mode_started(self):
            self.level = self.game.get_player_stats('spinner_level')

            #call reset
            self.reset()


        def mode_stopped(self):
            self.game.set_player_stats('spinner_level',self.level)
     
      
        def spin_text(self):
            #set text layer 
            self.game.score_display.set_text(self.spin_value+'K Per Spin'.upper(),0,'center',seconds=2)
            self.cancel_delayed('remove_text')
            self.delay(name='remove_text', event_type=None, delay=2, handler=lambda: self.game.display.rdc.remove_layer(id=text_layer_id))

  
        def play_animation(self,timer):
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
            name_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center")
            info_layer = dmd.TextLayer(128/2, 15, self.game.fonts['9x7_bold'], "center")

            name_layer.set_text('Spinners Increased'.upper(),color=dmd.BROWN)
            info_layer.set_text(str(self.spin_value)+'K Per Spin'.upper(),color=dmd.GREEN,blink_frames=2)

            #play sound
            self.game.sound.play('collect')

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,name_layer,info_layer])

            self.delay(name='clear_display_delay', event_type=None, delay=timer, handler=self.clear)
            
            
        def clear(self):
            self.layer = None
            
        def reset_level(self):
            self.level = 0
            
        def inc_level(self):
            self.level +=1
            
        def calc_value(self):
            if self.level<=3:
                self.spin_value=self.value[self.level]
            else:
                self.spin_value=(self.level-1)*self.inc_value

            if self.game.switches.leftInlane.time_since_change()<=self.spinner_double_timer+1:
                self.spin_value = self.spin_value*2

        def score(self):
            self.game.score(self.spin_value*1000)


#        def strobe_flashers(self,flashers,time=0.1):
#            timer = 0
#            repeats = 1
#
#            sequence=[]
#            for j in range(repeats):
#                sequence += flashers
#
#            for i in range(len(sequence)):
#
#                def flash(i,time,delay):
#                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='super',time=time+0.1))
#
#                flash(i,time,timer)
#                timer+=time

            
        def progress(self):
            self.spins+=1
            self.score()
            #self.game.sound.play_voice('spinner')
            self.game.sound.play('spinner')
            

        def sw_leftSpinner_active(self, sw):
            self.progress()
            
        def sw_rightSpinner_active(self, sw):
            self.progress()

       
        def sw_leftInlane_active(self,sw):
            self.inc_level()
            self.calc_value()
            self.play_animation(1.5)
            self.game.effects.drive_lamp('rightSpinner','timeout',self.timer)
            self.delay(name='reset_spinner_level',delay=self.timer,handler=self.reset_level)
            
        def sw_rightInlane_active(self,sw):
            self.inc_level()
            self.calc_value()
            self.play_animation(1.5)
            self.game.effects.drive_lamp('leftSpinner','timeout',self.timer)
            self.delay(name='reset_spinner_level',delay=self.timer,handler=self.reset_level)
