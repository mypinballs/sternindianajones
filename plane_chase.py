# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"

class Plane_Chase(game.Mode):

	def __init__(self, game, priority):
            super(Plane_Chase, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.text_layer.composite_op ="blacksrc"
            self.text_layer.tracking = -1
            #self.text_layer.transition = dmd.ExpandTransition(direction='vertical')

            self.game.sound.register_sound('stall', sound_path+"plane_stall.aiff")
            self.game.sound.register_sound('flight', sound_path+"plane_1.aiff")
            self.game.sound.register_sound('flight', sound_path+"plane_2.aiff")
            self.game.sound.register_sound('plane_crash', sound_path+"plane_crash.aiff")

            #setup score vars
            self.ramp_made_score = 1000000
            self.ramp_entered_score = 5000
            self.dog_fight_base_value = 40000000
            self.dog_fight_boost = 10000000
            self.dog_fight_min_value = 3000000

            self.plane_lamps = ['leftPlaneBottom','rightPlaneBottom','leftPlaneMiddle','rightPlaneMiddle','leftPlaneTop','rightPlaneTop','leftRampArrow','rightRampArrow']
            self.plane_lamps = []
            

        def reset(self):
            #set the ramps made count
            if self.game.user_settings['Gameplay (Feature)']['Plane Chase Memory'].startswith('Y'):
                self.ramps_made=self.game.get_player_stats('ramps_made')
            else:
                self.ramps_made = 0
                
            self.dog_fights_completed = self.game.get_player_stats('dog_fights_completed')
            
            self.text_layer.y = 5
            
            self.dog_fight_value = self.dog_fight_base_value+(self.dog_fight_boost*self.dog_fights_completed)
            self.dog_fight_running = False
            self.game.set_player_stats('dog_fight_running',self.dog_fight_running)
            #flags to enable shot sequence to be progressed
            self.left_ramp_enabled = False
            self.right_ramp_enabled = True
            
            self.bottom_left_wings = False
            self.middle_left_wings = False
            self.top_left_wings = False
            self.bottom_right_wings = False
            self.middle_right_wings = False
            self.top_right_wings = False
            
            self.game.coils.flasherSankara.disable()
            
            #self.game.effects.drive_lamp('leftRampArrow','superfast')
            #self.game.effects.drive_lamp(self.plane_lamps[0],'fast')

            self.update_lamps()

        def reset_lamps(self):
            for i in range(len(self.plane_lamps)):
                self.game.effects.drive_lamp(self.plane_lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.plane_lamps)):
                if i<=self.ramps_made:
                    self.game.effects.drive_lamp(self.plane_lamps[i],'on')
                elif i==(self.ramps_made+1):
                    self.game.effects.drive_lamp(self.plane_lamps[i],'fast')
                else:
                    self.game.effects.drive_lamp(self.plane_lamps[i],'off')

#            if self.left_ramp_enabled:
#                self.game.effects.drive_lamp('rightRampArrow','off')
#                self.game.effects.drive_lamp('leftRampArrow','superfast')
#
#            elif self.right_ramp_enabled:
#                self.game.effects.drive_lamp('leftRampArrow','off')
            self.game.effects.drive_lamp('rightRampArrow','superfast')

        def sequence(self,number):
            print("sequence: "+str(number))
            if number>0 and number<6:
#                self.game.effects.drive_lamp(self.plane_lamps[number-1],'on')
#                self.game.effects.drive_lamp(self.plane_lamps[number],'fast')
#
#                if self.left_ramp_enabled:
#                    self.right_ramp_enabled = True
#                    self.left_ramp_enabled = False
#                    self.game.effects.drive_lamp('leftRampArrow','off')
#                    self.game.effects.drive_lamp('rightRampArrow','superfast')
#
#                elif self.right_ramp_enabled:
#                    self.right_ramp_enabled = False
#                    self.left_ramp_enabled = True
#                    self.game.effects.drive_lamp('rightRampArrow','off')
#                    self.game.effects.drive_lamp('leftRampArrow','superfast')

                #self.game.lampctrl.save_state('game')
                
                bgnd = dmd.Animation().load(game_path+"dmd/blank.dmd")
                self.bgnd_layer = dmd.FrameLayer(frame=bgnd.frames[0])
                
                anim = dmd.Animation().load(game_path+"dmd/plane_chase.dmd")
                self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=6)
                #add the made text before the end of the animation
                self.animation_layer.add_frame_listener(-3,self.ramp_made_text)
                #queue the clean up at the animation end
                self.animation_layer.add_frame_listener(-1,self.queue_clear)
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.animation_layer,self.text_layer])
                
                self.game.lampctrl.play_show('success', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
                self.game.score(self.ramp_made_score)

            else:
                self.dog_fight()
                self.game.coils.flasherSankara.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
                self.delay(name='dog_fight_expired', event_type=None, delay=self.game.user_settings['Gameplay (Feature)']['Dog Fight Timer'], handler=self.dog_fight_timeout)


        def ramp_made_text(self):
            self.text_layer.set_text(locale.format("%d",self.ramp_made_score,True),blink_frames=4, color=dmd.CYAN)


        def dog_fight(self):
            self.dog_fight_running = True
            self.game.set_player_stats('dog_fight_running',self.dog_fight_running)
            #reset ramps_made
            self.ramps_made = 0
            self.game.set_player_stats('ramps_made',self.ramps_made)
            self.game.temple.open()
            
            bgnd = dmd.Animation().load(game_path+"dmd/dog_fight_border.dmd") #possibly change the bgnd here
            self.bgnd_layer = dmd.FrameLayer(frame=bgnd.frames[0])
                
            self.text_layer.y = 4
            self.text_layer.set_text(locale.format("%d",self.dog_fight_value,True), color=dmd.PURPLE)

            if self.dog_fight_value>self.dog_fight_min_value:
                self.dog_fight_value -=152750
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.text_layer])
                self.delay(name='update_time', event_type=None, delay=0.1, handler=self.dog_fight)
            else:
                self.dog_fight_timeout()
                
        
            
        def dog_fight_timeout(self):
            self.cancel_delayed('update_time')
            
            if not self.game.get_player_stats('lock_lit'):
                self.game.temple.close()
                
            self.clear()
            self.reset()
            
            
        def dog_fight_award(self):
            #cancel timers
            self.cancel_delayed('update_time')
            self.cancel_delayed('dog_fight_expired')
            self.game.coils.flasherSankara.disable()
            self.game.temple.close()
            
            self.dog_fights_completed+=1
            self.game.set_player_stats('dog_fights_completed',self.dog_fights_completed)
            
            #play animation
            anim = dmd.Animation().load(game_path+"dmd/dog_fight.dmd")
            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=6)
            self.animation_layer.add_frame_listener(-1,self.dog_fight_final_score)
            self.layer = self.animation_layer
            
            
            #play sound
            self.game.sound.play('plane_crash')

        
        def dog_fight_final_score(self):
             self.text_layer.set_text(locale.format("%d",self.dog_fight_value,True),blink_frames=2,seconds=1.5,color=dmd.GREEN)
             self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.text_layer])
             self.game.score(self.dog_fight_value)
             self.queue_clear()
             self.reset()
             
             if self.game.get_player_stats('lock_lit'): #lock ball if needed once dog fight completed
                 self.game.base_game_mode.multiball.lock_ball()

        def mode_started(self):
            self.reset()

        
        def mode_stopped(self):
            if self.dog_fight_running:
                self.dog_fight_timeout()
            else:
                self.reset()

        def queue_clear(self):
            self.delay(name='clear_delay', delay=1.5, handler=self.clear)
            
        def clear(self):
            self.layer = None
            self.text_layer.set_text('')

#        def sw_leftRampEnter_active(self,sw):
#            self.game.score(self.ramp_entered_score)
#            self.game.sound.play("stall")


        def sw_rightRampEnter_active(self,sw):
            if self.game.switches.rightRampEnter.time_since_change()>1:
                self.game.score(self.ramp_entered_score)
                self.game.sound.play("stall")


#        def sw_leftRampMade_active(self,sw):
#            if self.left_ramp_enabled:
#                self.ramps_made+=1
#                self.sequence(self.ramps_made)
#                self.game.sound.play("flight")
#            else:
#                self.game.score(self.ramp_made_score/2)
#
#            self.game.set_player_stats('ramps_made',self.ramps_made)



        def sw_rightRampMade_active(self,sw):
            if self.game.switches.rightRampMade.time_since_change()>1:
                if self.right_ramp_enabled:
                    self.ramps_made+=1
                    self.sequence(self.ramps_made)
                    self.game.sound.play("flight")
                else:
                    self.game.score(self.ramp_made_score/2)

                self.game.set_player_stats('ramps_made',self.ramps_made)
            
            
        def sw_subway_active(self, sw):
            if self.dog_fight_running:
                self.dog_fight_award()