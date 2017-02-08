# Frankenstein Game Mode
# Homage to the great Sega game of 1995. This modes parodies the 'frankenstein millions' mode
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


class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Frankenstein(game.Mode):

	def __init__(self, game, priority):
            super(Frankenstein, self).__init__(game, priority)

            #logging
            self.log = logging.getLogger('ij.frankenstein')

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Frankenstein Timer'])
            self.log.info("Frankenstein Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            #self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            #self.award_layer.composite_op ="blacksrc"
            
            #sound setup
            self.game.sound.register_music('frankenstein_play', music_path+"frankenstein_millions.aiff")
            self.game.sound.register_sound('franky_target_unlit', sound_path+"frankenstein071_electric.aiff")
            self.game.sound.register_sound('franky_target_unlit', sound_path+"frankenstein072_electric.aiff")
            self.game.sound.register_sound('franky_target_lit', speech_path+"frankenstein144_million.aiff")
            self.game.sound.register_sound('franky_target_lit', speech_path+"frankenstein199_million.aiff")
            self.game.sound.register_sound('franky_inlane', sound_path+"xxx.aiff")
            self.game.sound.register_sound('franky_outlane', sound_path+"frankenstein099_drain.aiff")          
            
            self.game.sound.register_sound('franky_speech0', speech_path+"frankenstein147_you_must_help_me.aiff")
            self.game.sound.register_sound('franky_speech0', speech_path+"frankenstein206_who_am_i.aiff")
            self.game.sound.register_sound('franky_speech0', speech_path+"frankenstein181_say_my_name.aiff")
            
            self.game.sound.register_sound('franky_speech1', speech_path+"frankenstein092_live_live_live.aiff")
            self.game.sound.register_sound('franky_speech1', speech_path+"frankenstein140_thats_the_combination.aiff")

            self.game.sound.register_sound('franky_speech2', speech_path+"frankenstein145_i_keep_my_promises.aiff")
            self.game.sound.register_sound('franky_speech2', speech_path+"frankenstein129_electricity_is_the_key.aiff")

            #lamps setup
            self.lamps = ['indyI','indyN','indyD','indyY','jonesJ','jonesO','jonesN','jonesE','jonesS']
            
            #score setup
            self.target_lit_score_value = 1000000
            self.target_unlit_score_value = 100000
            self.score_value_boost = 1000000
            self.score_value_extra = 2000000
            self.bonus_value = 2500000
            self.set_completed_score =  self.target_lit_score_value *10


        def reset(self):
            self.letters_spotted = 0
            self.flags = [False,False,False,False,False,False,False,False,False,False,False,False]
            self.set1 = False
            self.set2 = False
            self.set3 = False
            

        def mode_started(self): 
            self.reset()
            
            self.running_total = 0
            self.game.set_player_stats('mode_blocking',True)
            
            #load player stats
            self.sets_completed = self.game.get_player_stats('frankenstein_sets_completed')
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, 22, self.game.fonts['07x5'],self.timer,"right")
            self.info_layer = dmd.TextLayer(128/2, 22, self.game.fonts['07x5'], "center", opaque=False)
            
            #set text
            self.info_layer.set_text("SHOOT STANDUP TARGETS",blink_frames=10, color=dmd.PURPLE)
            
            #load animation
            self.load_anim()
            
            #start mode music & speech
            self.game.sound.play_music('frankenstein_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=0)
            self.delay(name='eject_delay', event_type=None, delay=0.5, handler=self.eject)
            
            #setup timout
            self.delay(name='scene_timeout', event_type=None, delay=self.timer, handler=self.scene_totals)
            
            #update_lamps
            self.update_lamps()


        def mode_stopped(self):
            self.game.set_player_stats('mode_blocking',False)
            
            #save player stats
            self.game.set_player_stats('frankenstein_sets_completed',self.sets_completed)

            self.game.set_player_stats('frankenstein_millions_score',self.running_total)
            self.game.set_player_stats('last_mode_score',self.running_total)

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            #continue any previously active mode music if ball still in play
            if self.game.trough.num_balls_in_play>0:
                #self.game.sound.stop_music()
                #self.game.sound.play_music('general_play', loops=-1)
                self.game.utility.resume_mode_music() 

            #clear display
            self.clear()

            #reset lamps
            self.reset_lamps()


        def mode_tick(self):
            if self.game.trough.num_balls_in_play==0:
                self.game.modes.remove(self)
            


        def scene_totals(self):
            bgnd_layer = dmd.FrameLayer(opaque=False,frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])

            #set text layers
            title_layer = dmd.TextLayer(64, 8, self.game.fonts['8x6'], "center", opaque=False)
            award_layer = dmd.TextLayer(64, 16, self.game.fonts['num_09Bx7'], "center", opaque=False)

            title_layer.composite_op ="blacksrc"
            award_layer.composite_op ="blacksrc"
           
            title_layer.set_text("Total Score",color=dmd.BROWN)
            award_layer.set_text(locale.format("%d", self.running_total, True), color=dmd.PURPLE)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,title_layer,award_layer])
            
            #sound
            self.game.sound.play("franky_outlane")
           
            #queue the end of scene cleanup
            self.end_scene_delay(4)
            
            
        def end_scene_delay(self,timer):
            self.cancel_delayed('scene_cleanup')
            self.delay(name='scene_cleanup', event_type=None, delay=timer, handler=lambda:self.game.modes.remove(self))
            
            
        def voice_call(self,count,delay=None):
            if delay==None:
                self.game.sound.play_voice("franky_speech"+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
     
        def score(self,value):
            self.game.score(value)
            self.running_total+=value
            
        def completed(self):
            self.sets_completed+=1
            self.voice_call(1)
            self.score(self.set_completed_score)
            self.info_layer.set_text("")
            self.delay(name='next_set_delay', event_type=None, delay=3, handler=self.next_letter_set)
            
        def next_letter_set(self):
            self.reset()
            self.load_anim()
            
            
        def load_anim(self):

            bgnd = dmd.FrameLayer(opaque=False,frame=dmd.Animation().load(game_path+'dmd/frankenstein_bgnd.dmd').frames[0])     

            F = dmd.FrameLayer(opaque=False)
            R = dmd.FrameLayer(opaque=False)
            A = dmd.FrameLayer(opaque=False)
            N1 = dmd.FrameLayer(opaque=False)
            K = dmd.FrameLayer(opaque=False)
            E1 = dmd.FrameLayer(opaque=False)
            N2 = dmd.FrameLayer(opaque=False)
            S = dmd.FrameLayer(opaque=False)
            T = dmd.FrameLayer(opaque=False)
            E2 = dmd.FrameLayer(opaque=False)
            I = dmd.FrameLayer(opaque=False)
            N3 = dmd.FrameLayer(opaque=False)
            
            completed = dmd.AnimatedLayer(opaque=False)
            
            layers=[bgnd,F,R,A,N1,K,E1,N2,S,T,E2,I,N3,completed,self.score_layer,self.timer_layer,self.info_layer]
            frame_path = ['dmd/frankenstein_f.dmd','dmd/frankenstein_r.dmd','dmd/frankenstein_a.dmd','dmd/frankenstein_n.dmd','dmd/frankenstein_k.dmd','dmd/frankenstein_e.dmd','dmd/frankenstein_n.dmd','dmd/frankenstein_s.dmd','dmd/frankenstein_t.dmd','dmd/frankenstein_e.dmd','dmd/frankenstein_i.dmd','dmd/frankenstein_n.dmd']
            x_posn = [7,16,27,37,48,59,68,79,88,98,107,111]
            
            for i in range(len(frame_path)):
                if self.flags[i]:
                    layers[i+1].frame = dmd.Animation().load(game_path+frame_path[i]).frames[0]
                    layers[i+1].composite_op = "blacksrc"
                    layers[i+1].target_x=x_posn[i]
                    layers[i+1].target_y=7
                    
            if self.letters_spotted==len(self.flags):
                anim = dmd.Animation().load(game_path+'dmd/frankenstein_completed.dmd')
                completed.frames=anim.frames
                completed.repeat=True
                completed.frame_time=2
                completed.composite_op = "blacksrc"
                self.completed()
            
            
            self.layer = dmd.GroupedLayer(128, 32, layers)
                
           
        def mode_progression(self,value):
            if not self.flags[value]:
                #self.game.drive_lamp(self.lamps[0],'on')
                self.letters_spotted +=1
                self.flags[value]=True;
                
                #update screen
                self.load_anim()
                #score
                self.score(self.target_lit_score_value)
                #sound
                self.game.sound.play("franky_target_lit")
               
            else:
                self.score(self.target_unlit_score_value)
                #sound
                self.game.sound.play("franky_target_unlit")
                

        def next_letter_id(self):
            j=0
            for i in range(len(self.flags)):
                if self.flags[i] and j<i:
                    j+=1
                else:
                    break
            return j
                
            
        def award_score(self,score_value=0):
            score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3, color=dmd.MAGENTA)
            self.game.score(score_value)


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'fast')
                
        def inlane(self):
            self.game.score(100000)
            self.game.sound.play("franky_inlane")

        def outlane(self):
            self.game.score(200000)
            self.game.sound.play("franky_outlane")

        def clear(self):
            self.layer = None
            
        def bonus(self):
            timer=2
            self.game.screens.monster_bonus(timer,self.bonus_value)
            self.running_total+=self.bonus_value
            self.voice_call(2)
            
            self.delay(name='eject_delay', event_type=None, delay=timer-1, handler=self.eject)
            
        def eject(self):
            self.game.base_game_mode.mode_select.eject_ball()


        #switch handlers
        def sw_indyI_active(self,sw):
            self.mode_progression(0)
            return procgame.game.SwitchStop
        
        def sw_indyN_active(self,sw):
            self.mode_progression(1)
            return procgame.game.SwitchStop
        
        def sw_indyD_active(self,sw):
            self.mode_progression(1)
            return procgame.game.SwitchStop
        
        def sw_indyY_active(self,sw):
            self.mode_progression(2)
            return procgame.game.SwitchStop
        
        def sw_adventureA_active(self,sw):
            self.mode_progression(3)
            return procgame.game.SwitchStop
        
        def sw_adventureD_active(self,sw):
            self.mode_progression(4)
            return procgame.game.SwitchStop
        
        def sw_adventureV_active(self,sw):
            self.mode_progression(5)
            return procgame.game.SwitchStop
        
        def sw_adventureE1N_active(self,sw):
            self.mode_progression(6)
            return procgame.game.SwitchStop
        
        def sw_adventureT_active(self,sw):
            self.mode_progression(7)
            return procgame.game.SwitchStop
        
        def sw_adventureUR_active(self,sw):
            self.mode_progression(8)
            return procgame.game.SwitchStop
        
        def sw_adventureE2_active(self,sw):
            self.mode_progression(9)
            return procgame.game.SwitchStop
        
        def sw_jonesJ_active(self,sw):
            self.mode_progression(9)
            return procgame.game.SwitchStop
        
        def sw_jonesO_active(self,sw):         
            self.mode_progression(10)
            return procgame.game.SwitchStop
            
        def sw_jonesN_active(self,sw):
            self.mode_progression(10)
            return procgame.game.SwitchStop
        
        def sw_jonesE_active(self,sw):         
            self.mode_progression(11)
            return procgame.game.SwitchStop
            
        def sw_jonesS_active(self,sw):
            self.mode_progression(11)
            return procgame.game.SwitchStop
        
        def sw_captiveBallRear_inactive(self, sw):
            self.mode_progression(self.next_letter_id())
            return procgame.game.SwitchStop

        def sw_captiveBallFront_inactive_for_200ms(self, sw):
            return procgame.game.SwitchStop
            
        def sw_leftInlane_active(self,sw):
            self.inlane()
            return procgame.game.SwitchStop
        
        def sw_rightInlane_active(self,sw):
            self.inlane()
            return procgame.game.SwitchStop
        
        def sw_rightOutlane_active(self,sw):
            self.outlane()
            return procgame.game.SwitchStop
        
        def sw_leftOutlane_active(self,sw):
            self.outlane()
            return procgame.game.SwitchStop
 
        
        def sw_grailEject_active_for_250ms(self,sw): 
            self.bonus()
            return procgame.game.SwitchStop
