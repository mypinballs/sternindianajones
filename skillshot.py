# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import logging
import random
import audits
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"

#locale.setlocale(locale.LC_ALL, 'en_US')

class Skillshot(game.Mode):

	def __init__(self, game, priority):
            super(Skillshot, self).__init__(game, priority)
            
            self.log = logging.getLogger('ij.skillshot')

            self.game.sound.register_sound('skillshot_made', speech_path+"excellent.aiff")
            self.game.sound.register_sound('skillshot_made', speech_path+'well_done.aiff')
            self.game.sound.register_sound('skillshot_made', speech_path+'incredible.aiff')
            
            self.game.sound.register_sound('skillshot_missed', speech_path+"argh.aiff")
            self.game.sound.register_sound('skillshot_missed', speech_path+'big_problem01.aiff')
            self.game.sound.register_sound('skillshot_missed', speech_path+'ij402D5_kill_you_right_now.aiff')
            self.game.sound.register_sound('skillshot_missed', speech_path+'ij402D6_only_say_sorry_so_many_times.aiff')
            #self.game.sound.register_sound('skillshot_missed', speech_path+'ij40354_oh_my_god.aiff')
            
            self.game.sound.register_sound('fanfare', sound_path+'fanfare_path_modes.aiff')
            

            self.lamps = ['skillIndy','skillSwordsman','skillMystery','skillJets']
           
            self.skill_timer =20 #add setting
            self.skill_value_start = 5000000
            self.skill_value_boost = 5000000
            

        def reset(self):
        
           self.count = 0
           self.level = self.game.get_player_stats('skillshot_level')


        def mode_started(self):
            self.reset()
            
            self.lamp_sequence()
            #self.game.status = 'skillshot'
            self.delay(name='clear', event_type=None, delay=self.skill_timer, handler=self.clear)

        def mode_tick(self):
            pass

        def mode_stopped(self):
            self.cancel_delayed('ss_lamp')
            self.cancel_delayed('ss_repeat')
            self.cancel_delayed('clear')
            self.game.set_player_stats('skillshot_level',self.level)
            

        def lamp_sequence(self):
            #create a strip of moving lights

            timer=0
            interval=0.5 #1.0/(self.speed*self.level)

            for lamp in self.lamps:
                self.delay(name='ss_lamp',delay=timer,handler=self.set_lamp,param=lamp) #lambda: self.game.zwLamps.timedon(num,'white',interval))
                timer+=interval

            self.delay(name='ss_repeat',delay=timer+2,handler=self.lamp_sequence)
            

        def set_lamp(self,lamp):
            self.active = False
            interval=2 #1.0/(self.speed*self.level)

            self.game.lamps[lamp].schedule(schedule=0x99999999, cycle_seconds=interval, now=True)
            self.count +=1
            self.cancel_delayed('skillshot_'+lamp+'_off')
            self.delay(name='skillshot_'+lamp+'_off', delay=interval, handler=self.disable_lamp, param=lamp)
            self.log.info('Skillshot Count:%s',self.count)
            
            
        def disable_lamp(self,lamp):
            self.game.lamps[lamp].disable()
            self.count -=1
        
            
#        def activate_lamps(self):
#             print("activate skillshot lamps")
#             for i in range(len(self.lamps)):
#                self.game.drive_lamp(self.lamps[i],'superfast')
#

        def clear_lamps(self):
            print("stop skillshot lamps")
            for i in range(len(self.lamps)):
                self.game.drive_lamp(self.lamps[i],'off')
                self.cancel_delayed('skillshot_'+self.lamps[i]+'_off')
                
    
        def process(self):
            self.log.info(len(self.lamps))
            if self.count==len(self.lamps):
                self.shot_made()
            else:
                self.shot_missed()



        def shot_made(self):
            
            timer=2
            skill_value = (self.skill_value_boost*self.level) +self.skill_value_start

            self.text_layer = dmd.TextLayer(125, 20, self.game.fonts['num_09Bx7'], "right", opaque=False)
            self.text_layer.composite_op='blacksrc'
            
            #self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+self.dmd_image).frames[0])
            anim = dmd.Animation().load(game_path+"dmd/skillshot_bgnd.dmd")
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            #self.bgnd_layer.add_frame_listener(-1, self.clear)

            #set text layers
            self.text_layer.set_text(locale.format("%d",skill_value,True),color=dmd.CYAN,blink_frames=2)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.text_layer])
            
            self.level+=1
            
            self.game.sound.play_voice('skillshot_made')
            self.game.sound.play('fanfare')
            self.game.score(skill_value)

            #lamp show - and restore previous lamps
            #self.game.lampctrl.save_state('game')
            #self.game.lampctrl.play_show('success', repeat=False,callback=self.restore_lamps)
            self.game.lampctrl.play_show('success', repeat=False,callback=self.game.update_lamps)
            
            
            self.delay(name='clear_display_delay', event_type=None, delay=timer, handler=self.clear)

            
        def shot_missed(self):

            timer=2
            skill_value = ((self.skill_value_boost*self.level) +self.skill_value_start)/100
            
            #update display layer
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
  
            info_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center")
            info_layer.set_text('Skillshot'.upper(),color=dmd.YELLOW)
            
            info_layer2 = dmd.TextLayer(128/2, 15, self.game.fonts['8x6'], "center")
            info_layer2.set_text('Missed'.upper(),color=dmd.RED,blink_frames=2)

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer,info_layer2])
            
            self.delay(name='clear_display_delay', event_type=None, delay=timer, handler=self.clear)

            self.game.sound.play_voice('skillshot_missed')
            self.game.score(skill_value)
            

        def restore_lamps(self):
            self.game.lampctrl.restore_state('game')

        def update_lamps(self):
            pass

        def clear(self):
            self.layer = None
            self.clear_lamps()
            #self.game.status = None
            self.game.modes.remove(self)

        
        def sw_skillShot_active(self,sw):
            if self.game.switches.skillShot.time_since_change()>1:
                self.process()