# Steal The Stones Game Mode

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import random
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Steal_The_Stones(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Steal_The_Stones, self).__init__(game, priority)
            
            #logging
            self.log = logging.getLogger('ij.steal_the_stones')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Steal The Stones Timer'])
            print("Steal The Stones Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(76, 10, self.game.fonts['num_09Bx7'],self)
            self.award_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            
            #sound setup
            self.game.sound.register_music('sts_background_play', music_path+"steal_the_stones.aiff")
            self.game.sound.register_sound('sts_shot_hit', sound_path+"poa_start.aiff")
            self.game.sound.register_sound('sts_fanfare', sound_path+"fanfare_path_modes.aiff")
            self.game.sound.register_sound('sts_target_lit', sound_path+'poa_lane_lit.aiff')
            self.game.sound.register_sound('sts_target_unlit', sound_path+'poa_lane_unlit_1.aiff')
            self.game.sound.register_sound('sts_target_unlit', sound_path+'poa_lane_unlit_2.aiff')
            self.game.sound.register_sound('sts_target_unlit', sound_path+'poa_lane_unlit_3.aiff')
            
            self.game.sound.register_sound('sts_s0', speech_path+"the_stones_are_mine.aiff")
            self.game.sound.register_sound('sts_s1', speech_path+"what_a_vivid_imagination.aiff")
            self.game.sound.register_sound('sts_s2', speech_path+"moran_prepare_to_meet_kali.aiff")
            self.game.sound.register_sound('sts_s3', speech_path+"you_dare_not_do_that.aiff")
            
            self.game.sound.register_sound('sts_well_done', speech_path+"well_done_my_friend-01.aiff")
            self.game.sound.register_sound('sts_well_done', speech_path+"well_done-03.aiff")
            self.game.sound.register_sound('sts_well_done', speech_path+"nice_shot_1-01.aiff")
            self.game.sound.register_sound('sts_well_done', speech_path+"nice_shot_2-01.aiff")
            self.game.sound.register_sound('sts_well_done', speech_path+"nice_shot_3-01.aiff")
            

            #lamps setup
            self.lamps = ['rightRampArrow']
            self.jones_lamps = ['jonesJ','jonesO','jonesN','jonesE','jonesS']
            
            #score defaults
            self.score_value_boost = 1000000
            self.score_value_start = 8000000
            self.score_value_extra = 2000000
            self.jones_target_score = 5000000
            self.jones_target_missed_score = 50000
            self.jones_completed_score = 2000000
            
            
        def reset(self):
            #var setup
            self.count = 0
            #self.num_of_stones = 8
            
        
        def reset_jones(self):
            self.jones_sequence_running = False
            self.jones_flags = [False,False,False,False,False]
            self.jones_sequence_flags = [False,False,False,False,False]
            

        def load_progress_anim(self):
            anim = dmd.Animation().load(game_path+"dmd/5_million.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            self.delay(name='instructions', event_type=None, delay=1, handler=lambda:self.load_scene_anim(self.count))
                    
                    
        def load_scene_anim(self,count):
            scene_num=1

            self.scene_anim = "dmd/sts_scene_"+str(scene_num)+".dmd"
            anim = dmd.Animation().load(game_path+self.scene_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=True,frame_time=2)
            info_layer_1 = dmd.TextLayer(128/2, 8, self.game.fonts['07x5'], "center", opaque=False)
            info_layer_1.set_text("GET ALL LIT TARGETS",blink_frames=4, color=dmd.MAGENTA)
            self.layer = dmd.GroupedLayer(128, 32, [self.scene_layer,info_layer_1,self.timer_layer])

#        def load_mp_instructions(self):
#            anim = dmd.Animation().load(game_path+"dmd/poa_instructions.dmd")
#            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)
        

        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/steal_the_stones_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)
            self.score_layer.justify='center'
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


        def mode_started(self):
            self.reset()
            self.reset_jones()
            
            #load player stats
            self.stones_collected = self.game.get_player_stats('stones_collected');
            #update path mode var
            self.game.set_player_stats("path_mode_started",True)
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, 25, self.game.fonts['07x5'],self.timer,"right")
            self.info_layer = dmd.TextLayer(80, 20, self.game.fonts['07x5'], "center", opaque=False)
            self.info_layer.set_text("SHOOT RIGHT RAMP",blink_frames=4, color=dmd.MAGENTA)

            #turn on coils and flashers
            self.game.coils.flasherKingdom.schedule(0x30003000, cycle_seconds=0, now=True)
            #self.game.coils.divertorMain.pulse(50)
            #self.game.coils.divertorHold.pulse(0)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('sts_background_play', loops=-1)
            #self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.play_dialog)
            self.play_dialog(0.5)

            #update_lamps
            self.update_lamps()

        def mode_stopped(self):
            #save player stats
            self.stones_collected+=self.count
            self.game.set_player_stats('stones_collected',self.stones_collected)

            score_value = self.score_value_start*self.count
            self.game.set_player_stats('steal_the_stones_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)

            #turn off coils & flashers
            self.game.coils.flasherKingdom.disable()
            #self.game.coils.divertorHold.disable()

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #update poa player stats
            self.game.set_player_stats("path_mode_started",False)
            self.game.set_player_stats("poa_queued",False)

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass



        def voice_call(self,count,delay=None,label="sts_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

        def play_dialog(self,delay):
            #play mode speech calls at various points
            interval = 6
            self.voice_call(0,delay)
            self.voice_call(1,delay+interval/3)
            self.voice_call(2,delay+(interval*2))
            self.voice_call(3,delay+(interval*3))


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
     
        
        def setup_jones_sequence(self,count):
            
            for i in range(count+1):
                posn = random.randint(0,len(self.jones_sequence_flags)-1)
                self.jones_sequence_flags[posn] = True
            
            
            for i in range(len(self.jones_lamps)):
                if self.jones_sequence_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'fast')
                else:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'off')
            
            self.jones_sequence_running = True
            self.log.info('Jones Sequence Created:%s',self.jones_sequence_flags)
            
        
        def mode_progression(self):
            if not self.jones_sequence_running:
                self.count+=1
                self.timer+=10
                self.mode_select.mode_paused(sw=None)
                
#               if (self.count==1):
#                   self.game.mini_playfield.sts_path_sequence(self.num_of_stones)

                #stop the ball
                self.stop_ball()
            
                #clear mode lamps
                self.reset_lamps()
                #turn off flasher
                self.game.coils.flasherKingdom.disable()
            
                #setup the jones targets
                self.setup_jones_sequence(self.count)

                #load progression animations
                self.load_scene_anim(self.count)
                #self.load_mp_instructions()
                #self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)

                #release ball
                self.delay(name='release_ball', event_type=None, delay=3, handler=self.release_ball)

                #play sound
                self.game.sound.play('sts_shot_hit')
            else:
                self.game.sound.play('sts_target_unlit')
                self.game.score(self.score_value_extra)  
            
            
        def mode_continue(self):
            self.reset_jones()
            self.game.coils.flasherKingdom.schedule(0x30003000, cycle_seconds=0, now=True)
            #load animation
            self.load_bgnd_anim()
            #update_lamps
            self.update_lamps()


        def jones_progress(self,num):
            if self.jones_sequence_flags[num] and self.jones_sequence_running:
                self.jones_flags[num]=True

                self.load_progress_anim()
                self.set_jones_lamps(num)
                self.game.score(self.jones_target_score)
                self.game.sound.play('sts_target_lit')
                    
                #test for a completed set of targets
                complete=True
                for i in range(len(self.jones_lamps)):
                    if self.jones_sequence_flags[i] and not self.jones_flags[i]:
                        complete=False

                if complete:
                    self.delay(name='jones_completed_delay',delay=1,handler=self.jones_completed)
                    
                    
            elif self.jones_sequence_running:
                self.game.sound.play('sts_target_unlit')
                self.game.score(self.jones_target_missed_score) 
                
                    
                
                    
        def jones_completed(self):
            self.completed_jones_lamps()
            #self.game.effects.drive_flasher("flasherBackpanel", "fade", time=1)
            self.game.sound.play('sts_fanfare')
            self.game.sound.play_voice('sts_well_done')
                    
            self.game.score(self.jones_completed_score)
            
            self.delay(name='next_level', delay=1, handler=self.mode_continue)  
            

        def award_score(self,score_value=0):
            score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3)
            self.game.score(score_value)
      
            
        def stop_ball(self):
            self.game.coils.rampBallStop.patter(2,20,self.game.coils.rampBallStop.default_pulse_time,True)
            
    
        def release_ball(self):
            self.game.coils.rampBallStop.disable()
            self.mode_select.mode_unpaused()

            #clear display
            #self.clear()

        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')
            
            self.reset_jones_lamps()

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'fast')
                
            self.update_jones_lamps()
                
        
        def set_jones_lamps(self,id):
            self.game.effects.drive_lamp(self.jones_lamps[id],'smarton')
                     
        def update_jones_lamps(self):
            for i in range(len(self.jones_lamps)):
                if self.jones_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'on')
                elif self.jones_sequence_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'fast')
                else:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'off')
        
        def completed_jones_lamps(self):
            for i in range(len(self.jones_lamps)):
                if self.jones_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'superfast')
        
        def reset_jones_lamps(self):
            for i in range(len(self.jones_lamps)):
                self.game.effects.drive_lamp(self.jones_lamps[i],'off')
                

        def clear(self):
            self.layer = None


        #switch handlers
        
        def sw_rightRampMade_active(self, sw):
            if self.game.switches.rightRampMade.time_since_change()>1:
                self.mode_progression()
            return procgame.game.SwitchStop


        def sw_jonesJ_active(self,sw):
            self.jones_progress(0)
            return procgame.game.SwitchStop
        
        def sw_jonesO_active(self,sw):         
            self.jones_progress(1)
            return procgame.game.SwitchStop
            
        def sw_jonesN_active(self,sw):
            self.jones_progress(2)
            return procgame.game.SwitchStop
        
        def sw_jonesE_active(self,sw):         
            self.jones_progress(3)
            return procgame.game.SwitchStop
            
        def sw_jonesS_active(self,sw):
            self.jones_progress(4)
            return procgame.game.SwitchStop
            
#        def sw_miniBottomLeft_active(self, sw):
#            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
#
#        def sw_miniBottomRight_active(self, sw):
#            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
#
#        def sw_miniTopHole_active(self, sw):
#            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
#            return procgame.game.SwitchStop
#
#        def sw_miniBottomHole_active(self, sw):
#            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
#            return procgame.game.SwitchStop
