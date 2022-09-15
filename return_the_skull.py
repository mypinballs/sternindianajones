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


class Return_The_Skull(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Return_The_Skull, self).__init__(game, priority)
            
            #logging
            self.log = logging.getLogger('ij.return_the_skull')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Return The Skull Timer'])
            self.log.info("Return The Skull Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self, "center")
            
            #sound setup
            self.game.sound.register_music('return_the_skull_play', music_path+"return_the_skull.aiff")
            self.game.sound.register_sound('rts_shot_hit', sound_path+"poa_start.aiff")
            self.game.sound.register_sound('rts_fanfare', sound_path+"fanfare_path_modes.aiff")
            self.game.sound.register_sound('rts_temple_closed', sound_path+'poa_lane_lit.aiff')
            #self.game.sound.register_sound('rts_target_unlit', sound_path+'poa_lane_unlit_1.aiff')
            #self.game.sound.register_sound('rts_target_unlit', sound_path+'poa_lane_unlit_2.aiff')
            #self.game.sound.register_sound('rts_target_unlit', sound_path+'poa_lane_unlit_3.aiff')
            self.game.sound.register_sound('rts_s0', speech_path+"xxx.aiff")


            #lamps setup
            self.lamps = ['rightRampArrow','templeArrow']


        def reset(self):
            #var setup
            self.count = 0
            self.running_total = 0
            self.score_value_start = 3000000
            self.score_value_boost = 1000000
            self.score_value_extra = 2000000
            self.award_value = 10000000 #10million
            self.completed_value = 20000000
            self.level = 1
            self.in_progress = False
            self.stones = 5
            #self.shot_sequence_timer = 10
            #self.shot_missed_score = self.score_value_start/100
            
            

#        def load_scene_anim(self,count=0):
#            scene_num=1
#
#            bgnd_anim = dmd.Animation().load(game_path+"dmd/ttc_scene_"+str(scene_num)+".dmd")
#            bgnd_layer = dmd.AnimatedLayer(frames=bgnd_anim.frames,hold=False,opaque=False,repeat=True,frame_time=2)
#
#            item1 = dmd.Animation().load(game_path+"dmd/ttc_breath.dmd")
#            item2 = dmd.Animation().load(game_path+"dmd/ttc_word.dmd")
#            item3 = dmd.Animation().load(game_path+"dmd/ttc_path.dmd")
#
#            #set all items to blank initially
#            item_layer1 = dmd.FrameLayer(frame=item1.frames[1])
#            item_layer1.composite_op ="blacksrc"
#            item_layer2 = dmd.FrameLayer(frame=item2.frames[1])
#            item_layer2.composite_op ="blacksrc"
#            item_layer3 = dmd.FrameLayer(frame=item3.frames[1])
#            item_layer3.composite_op ="blacksrc"
#
#            if count>=1:
#                 item_layer1 =  dmd.FrameLayer(frame=item1.frames[0])
#                 item_layer1.composite_op ="blacksrc"
#                 item_layer1.target_x=9
#                 item_layer1.target_y=19
#            if count>=2:
#                 item_layer2 =  dmd.FrameLayer(frame=item2.frames[0])
#                 item_layer2.composite_op ="blacksrc"
#                 item_layer2.target_x=55
#                 item_layer2.target_y=18
#            if count>=3:
#                 item_layer3 =  dmd.FrameLayer(frame=item3.frames[0])
#                 item_layer3.composite_op ="blacksrc"
#                 item_layer3.target_x=95
#                 item_layer3.target_y=17
#
#            info_layer_1 = dmd.TextLayer(128/2, 8, self.game.fonts['07x5'], "center", opaque=False)
#            info_layer_1.set_text("SHOOT LIT SHOTS",blink_frames=4, color=dmd.PURPLE)
#            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,item_layer1,item_layer2,item_layer3,info_layer_1,self.timer_layer])


        def load_award_anim(self):
            anim = dmd.Animation().load(game_path+"dmd/5_million.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
           
                        
            
        def load_scene_anim(self, count=0):
            self.bgnd_anim = "dmd/skull_temple_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=9)
            
            
            stone_posns = [[17,1],[39,9],[62,1],[84,9],[107,1]]
            stone_graphic = dmd.Animation().load(game_path+"dmd/face_stone.dmd")
            sand_graphic = dmd.Animation().load(game_path+"dmd/rts_sand.dmd")
                
                
            self.scene_layer = []
            self.scene_layer.append(self.bgnd_layer)
                
            for id,posn in enumerate(stone_posns):
                
                if count>id:
                    stone_layer = dmd.FrameLayer(frame=stone_graphic.frames[1])
                    sand_layer = dmd.FrameLayer(frame=sand_graphic.frames[0])
                else:
                    stone_layer = dmd.FrameLayer(frame=stone_graphic.frames[0])
                    sand_layer = dmd.FrameLayer(frame=stone_graphic.frames[1])
                stone_layer.target_x = posn[0]
                stone_layer.target_y = posn[1]
                sand_layer.target_x = posn[0]+1
                sand_layer.target_y = posn[1]+21
                    
                stone_layer.composite_op ="blacksrc"
                sand_layer.composite_op ="blacksrc"
                self.scene_layer.append(stone_layer)
                self.scene_layer.append(sand_layer)
                
            self.scene_layer.append(self.score_layer)
            self.scene_layer.append(self.timer_layer)
            self.scene_layer.append(self.info_layer)
            self.info_layer.set_text("SHOOT RAMP",blink_frames=4,color=dmd.PURPLE)
            
            self.layer = dmd.GroupedLayer(128, 32, self.scene_layer)
            
            #close temple
            self.game.temple.close()
            
            #turn on coils and flashe       
            self.game.effects.drive_flasher('flasherKingdom','medium',time=0)
            self.game.effects.drive_flasher('flasherSkull','fast',time=3)


        def mode_started(self):
            self.reset()
 
            #load player stats
            self.stones_removed = self.game.get_player_stats('skull_face_stones_removed');
            #set mode player stats
            self.game.set_player_stats("path_mode_started",True)
            self.game.set_player_stats('temple_mode_started',True)
            
            self.running_total += int(self.game.user_settings['Gameplay (Feature)']['Mode Start Value (Mil)'])*1000000
            
            #setup additional layers
            self.timer_layer = dmd.TimerLayer(0, 0, self.game.fonts['07x5'],self.timer,"left")
            self.info_layer = dmd.TextLayer(0, 24, self.game.fonts['07x5'], "left", opaque=False)
            self.info_layer.composite_op='blacksrc'
            self.score_layer.justify='center'

            #load main animation
            self.load_scene_anim()
            
            #start mode music & speech
            self.game.sound.play_music('return_the_skull_play', loops=-1)
            #play speech
            self.voice_call(0,0.5)
            
            #close temple
            self.game.temple.close()

            #update_lamps
            self.update_lamps()


        def mode_stopped(self):
            #save player stats
            self.stones_removed+=self.count
            self.game.set_player_stats('skull_face_stones_removed',self.stones_removed)

            self.game.set_player_stats('return_the_skull_score',self.running_total)
            self.game.set_player_stats('last_mode_score',self.running_total)

            #turn off coils & flashers
            self.game.coils.flasherKingdom.disable()
            self.game.coils.flasherSankara.disable()
            #self.game.coils.divertorHold.disable()

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #update mode player stats
            self.game.set_player_stats("path_mode_started",False)
            self.game.set_player_stats("poa_queued",False)
            self.game.set_player_stats("temple_mode_started",False)

            #reset music
            #self.game.sound.stop_music()
            #self.game.sound.play_music('general_play', loops=-1)
            
            #restore temple if required 
            if self.game.get_player_stats('lock_lit'):
                self.game.temple.open()

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
            
            
#        def mode_progression(self):
#            if not self.shot_sequence_running:
#                self.count+=1
#                self.timer+=10
#                self.mode_select.mode_paused(sw=None)
#
#                #stop the ball
#                self.stop_ball()
#            
#                #clear mode lamps
#                self.reset_lamps()
#                #turn off flasher
#                self.game.coils.flasherKingdom.disable()
#                self.game.coils.flasherSkull.disable()
#                
#                #setup the jones targets
#                self.setup_shot_sequence(self.count)
#
#                #load progression animations
#                self.load_scene_anim(self.count-1)
#                #self.load_mp_instructions()
#                #self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)
#
#                #release ball
#                self.delay(name='release_ball', event_type=None, delay=3, handler=self.release_ball)
#
#                #play sound
#                self.game.sound.play('sts_shot_hit')
#                self.running_total+=self.score_value_extra
#                self.game.score(self.score_value_extra)
#            else:
#                self.game.sound.play('ttc_target_unlit')
#                self.game.score(self.shot_missed_score) 
#                
        
        def award_score(self,score_value=0):
            score_value = self.award_value

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3, color=dmd.MAGENTA)
            self.game.score(self.award_value)    
            
            
        def shot_progress(self):
            if not self.in_progress:
                self.info_layer.set_text("SHOOT TEMPLE",blink_frames=4,color=dmd.PURPLE)
                
                self.game.sound.play('rts_shot_hit')
                
                #self.game.coils.flasherSankara.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
                self.game.effects.drive_flasher('flasherSankara','fast',time=0)
            
                self.game.temple.open()
                
                self.game.score(self.score_value_extra)
                self.running_total+=self.score_value_extra
                
                self.in_progress = True
            else:
                self.game.sound.play('rts_shot_unlit')
                self.game.score(self.score_value_extra/10)
            
            
                    
        def shot_completed(self): 
            self.count+=1
            self.in_progress = False
            
            if self.count<self.stones:
                #award
                self.load_award_anim()
            
                #play sound & speech
                self.game.sound.play('rts_fanfare')
                #self.voice_call(self.count,1)
                
                self.game.effects.drive_flasher('flasherSankara','off')
            
                #award score
                self.game.score(self.award_value)
                self.running_total+=self.award_value

                self.delay(name='reload_scene_delay', event_type=None, delay=1, handler=lambda:self.load_scene_anim(self.count))
            else:
                self.completed()
            
            self.update_lamps()
            
            
        
        def completed(self):
            value = (self.completed_value*self.level)

            award_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=True)
            award_layer.set_text(locale.format("%d",value,True),blink_frames=2,color=dmd.GREEN)
            self.layer = award_layer

            self.game.score(self.score_value)
            #up the level for succesfull completion, not currently stored
            self.level+=1

            self.end_scene_delay(2)
             

        def end_scene_delay(self,timer):
            self.delay(name='scene_cleanup', event_type=None, delay=timer, handler=self.mode_select.end_scene)


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')
            

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'fast')
                 
                
        def clear(self):
            self.layer = None


        #switch handlers
        #-------------------
        
        def sw_rightRampMade_active(self,sw):
            if self.game.switches.rightRampMade.time_since_change()>1:

                self.shot_progress()
                return procgame.game.SwitchStop


        def sw_subway_active(self, sw):
            self.shot_completed()
            return procgame.game.SwitchStop
        
        
        def sw_templeStandup_active(self, sw):
            self.game.sound.play('rts_shot_unlit')
            self.game.score(self.score_value_extra/10)
            
            return procgame.game.SwitchStop
        
       


        