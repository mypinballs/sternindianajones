# The Three Challenges Game Mode

__author__="jim"
__date__ ="$31/12/12$"


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


class The_Three_Challenges(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(The_Three_Challenges, self).__init__(game, priority)
            
            #logging
            self.log = logging.getLogger('ij.three_challenges')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['The 3 Challenges Timer'])
            print("3 Challenges Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(86, 9, self.game.fonts['num_09Bx7'],self)
            
            #sound setup
            self.game.sound.register_music('ttc_background_play', music_path+"the_three_challenges.aiff")
            self.game.sound.register_sound('ttc_shot_hit', sound_path+"poa_start.aiff")
            self.game.sound.register_sound('ttc_fanfare', sound_path+"fanfare_path_modes.aiff")
            self.game.sound.register_sound('ttc_target_lit', sound_path+'poa_lane_lit.aiff')
            self.game.sound.register_sound('ttc_target_unlit', sound_path+'poa_lane_unlit_1.aiff')
            self.game.sound.register_sound('ttc_target_unlit', sound_path+'poa_lane_unlit_2.aiff')
            self.game.sound.register_sound('ttc_target_unlit', sound_path+'poa_lane_unlit_3.aiff')
            self.game.sound.register_sound('ttc_s0', speech_path+"meddling_with_powers.aiff")
            self.game.sound.register_sound('ttc_s1', speech_path+"the_breath_of_god.aiff")
            self.game.sound.register_sound('ttc_s2', speech_path+"the_word_of_god.aiff")
            self.game.sound.register_sound('ttc_s3', speech_path+"the_path_of_god.aiff")

            #lamps setup
            self.lamps = ['rightRampArrow']
            self.shot_lamps = ['leftLoopArrow','templeArrow','cairoSwordsman','raidersArrow','rightLoopArrow']
            


        def reset(self):
            #var setup
            self.count = 0
            self.running_total = 0
            self.score_value_start = 5000000
            self.score_value_boost = 1000000
            self.score_value_extra = 2000000
            self.shot_sequence_timer = 10
            self.shot_missed_score = self.score_value_start/100
            
            
        def reset_shots(self):
            self.shot_sequence_running = False
            self.shot_flags = [False,False,False,False,False]
            self.shot_sequence_flags = [False,False,False,False,False]
            

        def load_scene_anim(self,count=0):
            scene_num=1

            bgnd_anim = dmd.Animation().load(game_path+"dmd/ttc_scene_"+str(scene_num)+".dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=bgnd_anim.frames,hold=False,opaque=False,repeat=True,frame_time=2)

            item1 = dmd.Animation().load(game_path+"dmd/ttc_breath.dmd")
            item2 = dmd.Animation().load(game_path+"dmd/ttc_word.dmd")
            item3 = dmd.Animation().load(game_path+"dmd/ttc_path.dmd")

            #set all items to blank initially
            item_layer1 = dmd.FrameLayer(frame=item1.frames[1])
            item_layer1.composite_op ="blacksrc"
            item_layer2 = dmd.FrameLayer(frame=item2.frames[1])
            item_layer2.composite_op ="blacksrc"
            item_layer3 = dmd.FrameLayer(frame=item3.frames[1])
            item_layer3.composite_op ="blacksrc"

            if count>=1:
                 item_layer1 =  dmd.FrameLayer(frame=item1.frames[0])
                 item_layer1.composite_op ="blacksrc"
                 item_layer1.target_x=9
                 item_layer1.target_y=19
            if count>=2:
                 item_layer2 =  dmd.FrameLayer(frame=item2.frames[0])
                 item_layer2.composite_op ="blacksrc"
                 item_layer2.target_x=55
                 item_layer2.target_y=18
            if count>=3:
                 item_layer3 =  dmd.FrameLayer(frame=item3.frames[0])
                 item_layer3.composite_op ="blacksrc"
                 item_layer3.target_x=95
                 item_layer3.target_y=17

            info_layer_1 = dmd.TextLayer(128/2, 8, self.game.fonts['07x5'], "center", opaque=False)
            info_layer_1.set_text("SHOOT LIT SHOTS",blink_frames=4, color=dmd.PURPLE)
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,item_layer1,item_layer2,item_layer3,info_layer_1,self.timer_layer])


        def load_progress_anim(self):
            anim = dmd.Animation().load(game_path+"dmd/5_million.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            self.delay(name='reload_scene_delay', event_type=None, delay=1, handler=lambda:self.load_scene_anim(self.count-1))
            
            
        def load_bgnd_anim(self):
            if self.count<3:
                self.bgnd_anim = "dmd/the_three_challenges_bgnd.dmd"
                anim = dmd.Animation().load(game_path+self.bgnd_anim)
                self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=9)
                self.score_layer.justify='center'
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer])
            else:
                self.mode_select.end_scene()


        def mode_started(self):
            self.reset()
            self.reset_shots()
            
            #load player stats
            self.challenges_collected = self.game.get_player_stats('challenges_collected');
            #set mode player stats
            self.game.set_player_stats("path_mode_started",True)
            self.game.set_player_stats("ark_mode_started",True)
            self.game.set_player_stats('temple_mode_started',True)
            
            self.running_total += int(self.game.user_settings['Gameplay (Feature)']['Mode Start Value (Mil)'])*1000000
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, 25, self.game.fonts['07x5'],self.timer,"right")
            self.info_layer = dmd.TextLayer(86, 18, self.game.fonts['07x5'], "center", opaque=False)
            self.info_layer.set_text("SHOOT RIGHT RAMP",blink_frames=4,color=dmd.PURPLE)

            #turn on coils and flashers
            #self.game.coils.flasherKingdom.schedule(0x30003000, cycle_seconds=0, now=True)
            #self.game.coils.flasherSkull.schedule(schedule=0x30003000 , cycle_seconds=2, now=True)
            
            self.game.effects.drive_flasher('flasherKingdom','medium',time=0)
            self.game.effects.drive_flasher('flasherSkull','fast',time=3)
            #self.game.coils.divertorMain.pulse(50)
            #self.game.coils.divertorHold.pulse(0)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('ttc_background_play', loops=-1)
            #play speech
            self.voice_call(0,0.5)

            #update_lamps
            self.update_lamps()


        def mode_stopped(self):
            #save player stats
            self.challenges_collected+=self.count
            self.game.set_player_stats('challenges_collected',self.challenges_collected)

            self.game.set_player_stats('the_three_challenges_score',self.running_total)
            self.game.set_player_stats('last_mode_score',self.running_total)

            #turn off coils & flashers
            self.game.coils.flasherKingdom.disable()
            #self.game.coils.divertorHold.disable()

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #update mode player stats
            self.game.set_player_stats("path_mode_started",False)
            self.game.set_player_stats("poa_queued",False)
            self.game.set_player_stats("ark_mode_started",False)
            self.game.set_player_stats("temple_mode_started",False)

            #reset music
            #self.game.sound.stop_music()
            #self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass


        def voice_call(self,count,delay=None,label="ttc_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
            
        
        def setup_shot_sequence(self,count):
            self.reset_shots()
            numbers = range(len(self.shot_sequence_flags))
            random.shuffle(numbers)
            self.log.debug('Number list is:%s',numbers)
            
            for i in range(count):
                self.log.debug('Count loop :%s',i)
                posn = numbers[0]
                self.shot_sequence_flags[posn] = True
                numbers.pop(0)
            
            for i in range(len(self.shot_lamps)):
                if self.shot_sequence_flags[i]:
                    self.game.effects.drive_lamp(self.shot_lamps[i],'fast')
                else:
                    self.game.effects.drive_lamp(self.shot_lamps[i],'off')
            
            self.shot_sequence_running = True
            self.log.info('Shot Sequence Created:%s',self.shot_sequence_flags)
            
            #setup a changing shot sequence at the current count
            self.cancel_delayed('shot_sequence_expired')
            self.delay(name='shot_sequence_expired',delay=self.shot_sequence_timer,handler=self.setup_shot_sequence,param=count)
     
            
        def mode_progression(self):
            if not self.shot_sequence_running:
                self.count+=1
                self.timer+=10
                self.mode_select.mode_paused(sw=None)

                #stop the ball
                self.stop_ball()
            
                #clear mode lamps
                self.reset_lamps()
                #turn off flasher
                self.game.coils.flasherKingdom.disable()
                self.game.coils.flasherSkull.disable()
                
                #setup the jones targets
                self.setup_shot_sequence(self.count)

                #load progression animations
                self.load_scene_anim(self.count-1)
                #self.load_mp_instructions()
                #self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)

                #release ball
                self.delay(name='release_ball', event_type=None, delay=3, handler=self.release_ball)

                #play sound
                self.game.sound.play('sts_shot_hit')
                self.running_total+=self.score_value_extra
                self.game.score(self.score_value_extra)
            else:
                self.game.sound.play('ttc_target_unlit')
                self.game.score(self.shot_missed_score) 
                
            
            
        def shot_progress(self,num):
            if self.shot_sequence_flags[num] and self.shot_sequence_running:
                self.shot_flags[num]=True

                self.load_progress_anim()
                self.set_shot_lamps(num)
                self.running_total+=self.score_value_start
                self.game.score(self.score_value_start)
                self.game.sound.play('ttc_shot_lit')
                    
                #test for a completed set of targets
                complete=True
                for i in range(len(self.shot_lamps)):
                    if self.shot_sequence_flags[i] and not self.shot_flags[i]:
                        complete=False

                if complete:
                    self.delay(name='next_level', delay=1, handler=self.shots_completed) 
                    
            elif self.shot_sequence_running:
                self.game.sound.play('ttc_target_unlit')
                self.game.score(self.shot_missed_score) 
            
                    
        def shots_completed(self):
            self.cancel_delayed('shot_sequence_expired')
            self.completed_shot_lamps()
            #self.game.effects.drive_flasher("xxx", "fade", time=1)
            
            #update scene anim
            self.load_scene_anim(self.count)
            
            #play sound & speech
            self.game.sound.play('ttc_fanfare')
            self.voice_call(self.count,1)
            
            #award score
            self.game.score(self.score_value_start)
            
            if self.count<3:
                self.delay(name='next_level', delay=2, handler=self.mode_continue) 
            else:
                self.mode_select.end_scene()
            
            
        def mode_continue(self):
            self.reset_shots()
            #self.game.coils.flasherKingdom.schedule(0x30003000, cycle_seconds=0, now=True)
            self.game.effects.drive_flasher('flasherKingdom','medium',time=0)
            #load animation
            self.load_bgnd_anim()
            #update_lamps
            self.update_lamps()


        def stop_ball(self):
            self.game.coils.rampBallStop.patter(2,20,self.game.coils.rampBallStop.default_pulse_time,True)
            
    
        def release_ball(self):
            self.game.coils.rampBallStop.disable()
            self.mode_select.mode_unpaused()


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')
            
            self.reset_shot_lamps()

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'fast')
                
            self.update_shot_lamps()
                

        def set_shot_lamps(self,id):
            self.game.effects.drive_lamp(self.shot_lamps[id],'smarton')
                     
        def update_shot_lamps(self):
            for i in range(len(self.shot_lamps)):
                if self.shot_flags[i]:
                    self.game.effects.drive_lamp(self.shot_lamps[i],'on')
                elif self.shot_sequence_flags[i]:
                    self.game.effects.drive_lamp(self.shot_lamps[i],'fast')
                else:
                    self.game.effects.drive_lamp(self.shot_lamps[i],'off')
        
        def completed_shot_lamps(self):
            for i in range(len(self.shot_lamps)):
                if self.shot_flags[i]:
                    self.game.effects.drive_lamp(self.shot_lamps[i],'superfast')
        
        def reset_shot_lamps(self):
            for i in range(len(self.shot_lamps)):
                self.game.effects.drive_lamp(self.shot_lamps[i],'off')
                
                
        def clear(self):
            self.layer = None


        #switch handlers
        #-------------------
        
        def sw_rightRampMade_active(self,sw):
            if self.game.switches.rightRampMade.time_since_change()>1:

                self.mode_progression()
                return procgame.game.SwitchStop

        def sw_leftLoopTop_active(self, sw):
            if self.game.switches.rightLoopTop.time_since_change()>1:
                self.shot_progress(0)
            return procgame.game.SwitchStop

        def sw_templeStandup_active(self, sw):
            self.shot_progress(1)
            return procgame.game.SwitchStop
        
        def sw_captiveBallRear_inactive(self, sw):
            self.shot_progress(2)
            return procgame.game.SwitchStop

        def sw_captiveBallFront_inactive_for_200ms(self, sw):
            return procgame.game.SwitchStop
        
        def sw_arkHit_active(self, sw):
            self.shot_progress(3)
            return procgame.game.SwitchStop

        def sw_rightLoopTop_active(self, sw):
            if self.game.switches.leftLoopTop.time_since_change()>1:
                self.shot_progress(4)
            return procgame.game.SwitchStop


        