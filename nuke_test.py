# Get The Idol Game Mode

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="left", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Nuke_Test(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Nuke_Test, self).__init__(game, priority)
            self.log = logging.getLogger('ij.nuke_test')
            
            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Nuke Test Timer'])

            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self, "center")
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"

            #sound setup
            self.game.sound.register_music('nuke_test_play', music_path+"nuke_test.aiff")
            self.game.sound.register_sound('target_hit', sound_path+"outlane.aiff")
            self.game.sound.register_sound('nt_shot_hit', sound_path+"out_of_breath.aiff")
            
            self.game.sound.register_sound('nt_boom', sound_path+"crash.aiff")
            self.game.sound.register_sound('gti_speech0', speech_path+"nothing_to_fear_here.aiff")
            self.game.sound.register_sound('gti_speech11', speech_path+"thats_what_scares_me.aiff")
            self.game.sound.register_sound('gti_speech1', speech_path+"throw_me_the_idol.aiff")
            self.game.sound.register_sound('gti_speech12', speech_path+"no_time_to_argue.aiff")
            self.game.sound.register_sound('gti_speech2', speech_path+"give_me_the_whip.aiff")
            self.game.sound.register_sound('gti_speech3', speech_path+"adious_senoir.aiff")

            #lamps setup
            self.left_lamps = ['leftLoopArrow','crusadeArrow','templeArrow']
            self.right_lamps=['raidersArrow','rightRampArrow','rightLoopArrow']
            
            #var setup
            self.score_value_boost = 5000000
            self.score_levels = [5,10,15]
            self.completed_score_value = 20000000
            

        def reset(self):
            self.mode_completed = False
                
            self.count = 0
            self.running_total = 0
            self.level = 1


#        def load_anim(self,count):
#            self.bgnd_anim = "dmd/get_the_idol_bgnd_"+str(count)+".dmd"
#            anim = dmd.Animation().load(game_path+self.bgnd_anim)
#            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
        
        
        def load_bgnd_anim(self):
            self.clock_layer = dmd.TextLayer(24, 5, self.game.fonts['23x12'], "left", opaque=False)
            self.clock_layer.set_text("00:00:",color=dmd.RED)

            self.bgnd_anim = dmd.Animation().load(game_path+"dmd/nuke_clock_bgnd.dmd")
            self.bgnd_layer = dmd.FrameLayer(frame=self.bgnd_anim.frames[0])
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.clock_layer,self.timer_layer,self.score_layer,self.award_layer])


        def load_progress_anim(self,value,timer=3):
            self.bgnd_anim = "dmd/bonus_whip.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            anim_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,hold=True,frame_time=6)
            anim_layer.composite_op ="blacksrc"
            
            award_layer = dmd.TextLayer(103, 4, self.game.fonts['23x12'], "center", opaque=False)
            award_layer.set_text(str(value),color=dmd.RED)
            info_layer = dmd.TextLayer(120, 14, self.game.fonts['9x7_bold'], "center", opaque=False)
            info_layer.set_text('M',color=dmd.RED)
            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [award_layer,info_layer,anim_layer])

            self.cancel_delayed('reset_display')
            self.delay(name='reset_display', event_type=None, delay=timer, handler=self.load_bgnd_anim)
            
                    
        def mode_started(self): 
            self.reset()
            
            #set mode player stats
            self.game.set_player_stats('temple_mode_started',True)
            
            #setup timer layer
            self.timer_layer = dmd.TimerLayer(103, 5, self.game.fonts['23x12'],self.timer)
            self.timer_layer.composite_op ="blacksrc"
            
            #create animation
            self.load_bgnd_anim()
            
            self.game.sound.play_music('nuke_test_play', loops=-1)

            #self.reset_drops()
            #close temple
            self.game.temple.close()
            
            self.delay(name='mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=self.count)
            
            #lamps
            self.update_lamps()
            
            #nuke timeout - boom!
            self.delay(name='nuke_timeout', event_type=None, delay=self.timer, handler=self.failed1)

        
        def mode_tick(self):
            pass


        def mode_stopped(self):
            #cancel queued delays
            self.cancel_delayed('nuke_timeout')
            
            #set mode player stats
            self.game.set_player_stats('temple_mode_started',False)
            
            self.game.set_player_stats('nuke_test_score',self.running_total)
            self.game.set_player_stats('last_mode_score',self.running_total)

            #restore temple if required and award any locks if setup
            if self.game.get_player_stats('lock_lit'):
                if self.award_locks and self.mode_completed:
                    self.game.base_game_mode.multiball.lock_ball()
                else:
                    self.game.temple.open()
            else:
                self.game.temple.close()
                
            if self.mode_completed:
                self.eject()

            #reset music
            #self.game.sound.stop_music()
            #self.game.sound.play_music('general_play', loops=-1)
            
            #cancel flashers
            self.game.effects.drive_flasher('flasherSankara','off',)
            
            #clear display
            self.clear()
            
            #lamps
            self.reset_lamps()

        
        def mode_progression1(self,value):
            if self.count==0:
                score = self.score_levels[value]*1000000
                self.load_progress_anim(value=self.score_levels[value])
                
                self.running_total+=score
                self.game.score(score)
                
                #sound
                self.game.sound.play('nt_shot_hit')
            
                self.count+=1
                self.reset_lamps()
                self.update_lamps()
            else:
                score=self.score_levels[value]*10000
                self.game.score(score)
            
            
        def mode_progression2(self,value):
            if self.count==1:
                score = self.score_levels[value]*1000000
                self.load_progress_anim(value=self.score_levels[value])
            
                self.running_total+=score
                self.game.score(score)
                
                #sound
                self.game.sound.play('nt_shot_hit')
            
                self.count+=1
                self.reset_lamps()
                self.update_lamps()
            
                self.game.temple.open()
                self.game.effects.drive_flasher('flasherSankara','fast',time=0)
                
            else:
                score=self.score_levels[value]*10000
                self.game.score(score)


        def voice_call(self,count):
            self.game.sound.play_voice("gti_speech"+str(count))

            self.delay(name='mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=11+count)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True),color=dmd.YELLOW)


        def failed1(self):
            timer=1
            self.bgnd_anim = "dmd/mm_boom.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,hold=True,frame_time=6)
           
            #play sound
            self.game.sound.play('nt_boom')
            
            self.delay(name='failed2_queued', event_type=None, delay=timer, handler=self.failed2)


        def failed2(self):
            self.bgnd_anim = "dmd/blinded.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,hold=True,frame_time=6)
            self.end_scene_delay(2)
            
        
        def completed(self):
            self.cancel_delayed('nuke_timeout')
            
            award_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=True)
            award_layer.set_text(locale.format("%d",self.completed_score_value,True),blink_frames=2,color=dmd.GREEN)
            self.layer = award_layer
            
            self.running_total+=self.completed_score_value
            self.game.score(self.completed_score_value)
            #up the level for succesfull completion
            self.level+=1
            
            self.game.effects.drive_flasher('flasherSankara','off',)

            self.end_scene_delay(2)
             

        def end_scene_delay(self,timer):
            self.delay(name='scene_cleanup', event_type=None, delay=timer, handler=self.mode_select.end_scene)


        def reset_lamps(self):
            for i in range(len(self.left_lamps)):
                self.game.effects.drive_lamp(self.left_lamps[i],'off')
            for i in range(len(self.right_lamps)):
                self.game.effects.drive_lamp(self.right_lamps[i],'off')


        def update_lamps(self):
            if self.count==0:
                for i in range(len(self.right_lamps)):
                    self.game.effects.drive_lamp(self.right_lamps[i],'fast')
            elif self.count==1:
                for i in range(len(self.left_lamps)):
                    self.game.effects.drive_lamp(self.left_lamps[i],'fast')
            elif self.count==2:
                self.game.effects.drive_lamp('templeArrow','fast')
                

        def clear(self):
            self.layer = None
            
        
        def eject(self):
            #self.game.coils.grailEject.pulse()
            self.game.base_game_mode.mode_select.eject_ball()
            
        def eject_ball(self):
            #create eject delay
            self.delay(name='eject_delay', event_type=None, delay=0.5, handler=self.game.coils.grailEject.pulse)



        #switch handlers
        #-------------------
        
        def sw_subway_active(self, sw):
            if self.count==2:
                self.completed()
            return procgame.game.SwitchStop
        
        
        def sw_grailEject_active_for_200ms(self, sw):
            self.mode_progression2(2)
            self.eject_ball()
                
            return procgame.game.SwitchStop
        
        
        def sw_leftLoopTop_active(self, sw):
            if self.game.switches.rightLoopTop.time_since_change()>1:
                self.mode_progression2(1)

            return procgame.game.SwitchStop


        def sw_templeStandup_active(self, sw):
            self.mode_progression2(0)
            
            return procgame.game.SwitchStop


        def sw_arkHit_active(self, sw):
            if self.game.switches.arkHit.time_since_change()>1:
                self.mode_progression1(0)

            return procgame.game.SwitchStop
        
        
        def sw_rightRampMade_active(self, sw):
            if self.game.switches.rightRampMade.time_since_change()>1:
                self.mode_progression1(1)
                
            return procgame.game.SwitchStop


        def sw_rightLoopTop_active(self, sw):
            if self.game.switches.leftLoopTop.time_since_change()>1:
                self.mode_progression1(2)

            return procgame.game.SwitchStop