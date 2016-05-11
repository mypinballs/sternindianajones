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


class Loopin_Jackpots(game.Mode):

	def __init__(self, game, priority):
            super(Loopin_Jackpots, self).__init__(game, priority)

            #logging
            self.log = logging.getLogger('ij.loopin_jackpots')
            
            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Loopin Jackpots Timer'])
            self.log.info("Loopin Jackpots Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(40, -1, self.game.fonts['07x5'], self)
            #self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            #self.award_layer.composite_op ="blacksrc"
            
            #sound setup
            self.game.sound.register_music('loopin_jackpots_play', music_path+"raiders_march.aiff")
            self.game.sound.register_sound('jackpot_attempt', sound_path+"jackpot_attempt.aiff")
            self.game.sound.register_sound('jackpot_jingle', sound_path+"bonus_ff_2.aiff")
            self.game.sound.register_sound('jackpot1', speech_path+"jackpot.aiff")
            self.game.sound.register_sound('loopinjpot_outlane', sound_path+"frankenstein099_drain.aiff") 
            
            self.game.sound.register_sound('loopinjpot_speech0', speech_path+"well_done_my_friend.aiff")
            self.game.sound.register_sound('loopinjpot_speech0', speech_path+"nothing_to_fear_here.aiff")
            self.game.sound.register_sound('loopinjpot_speech0', speech_path+"excellent.aiff")
            self.game.sound.register_sound('loopinjpot_speech0', speech_path+"hit_the_jackpot.aiff")
            
            
            #self.game.sound.register_sound('loopinjpot_speech1', speech_path+"xxx.aiff")
            #self.game.sound.register_sound('loopinjpot_speech1', speech_path+"xxx.aiff")

            #self.game.sound.register_sound('loopinjpot_speech2', speech_path+"xxx.aiff")
            #self.game.sound.register_sound('loopinjpot_speech2', speech_path+"xxx.aiff")

            #lamps setup
            self.lamps = ['rightRampArrow']
            
            #score setup
            self.base_value = 10000000
            self.score_value_boost = 5000000
            self.score_value_extra = 2000000
            self.bonus_value = 2500000


        def reset(self):
            self.loopin_jackpot_count = 0
            self.running_total = 0
            self.mode_expired = False

        def mode_started(self):
            
            self.reset()
            
            #pause any active modes
            self.game.base_game_mode.mode_select.mode_paused(sw=None)
            #stop any new modes starting
            self.game.set_player_stats('mode_blocking',True)
            #update path mode var
            self.game.set_player_stats("path_mode_started",True) #set as path mode to halt adventure starting if completed
            
            #load player stats
            self.jackpot_count = 0
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer,"right")
            self.title_layer = dmd.TextLayer(0, 8, self.game.fonts['8x6'], "left", opaque=False)
            self.info_layer = dmd.TextLayer(4, 24, self.game.fonts['07x5'], "left", opaque=False)
            
            #setup text
            self.title_layer.set_text("LOOPIN' JACKPOTS", color=dmd.RED)
            self.info_layer.set_text("SHOOT RAMP NOW",blink_frames=10, color=dmd.PURPLE)
            
            #load animation
            self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('loopin_jackpots_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=0)

            #setup timout
            self.delay(name='scene_timeout', event_type=None, delay=self.timer, handler=self.scene_totals)
            
            #update_lamps
            self.game.coils.flasherSkull.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.update_lamps()


        def mode_stopped(self):
            
            #continue any modes previously active
            self.game.set_player_stats('mode_blocking',False)
            #update poa player stats
            self.game.set_player_stats("path_mode_started",False)
            self.game.set_player_stats("poa_queued",False)
            
            #resume music
            self.game.utility.resume_mode_music()
            #resume modes if required
            self.game.base_game_mode.mode_select.mode_unpaused()
            
            #save player stats
            self.game.set_player_stats('loopin_jackpots_collected',self.loopin_jackpot_count)

            self.game.set_player_stats('loopin_jackpots_score',self.running_total)
            self.game.set_player_stats('last_mode_score',self.running_total)

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #clear display
            self.clear()

            #reset lamps
            self.game.coils.flasherSkull.disable()
            self.reset_lamps()


        #def mode_tick(self):
            #if self.game.trough.num_balls_in_play==0:
                #self.game.modes.remove(self)
            


        def scene_totals(self):
            self.mode_expired = True
            self.cancel_delayed('reset_display')
            
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
            self.game.sound.play("loopinjpot_outlane")
           
            #queue the end of scene cleanup
            self.end_scene_delay(4)
            
            
        def end_scene_delay(self,timer):
            self.cancel_delayed('scene_cleanup')
            self.delay(name='scene_cleanup', event_type=None, delay=timer, handler=lambda:self.game.modes.remove(self))
            
            
        def voice_call(self,count,delay=None):
            if delay==None:
                self.game.sound.play_voice("loopinjpot_speech"+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
     
        def score(self,value):
            self.game.score(value)
            self.running_total+=value         

            
        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/loopin_jackpots_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.title_layer,self.info_layer])
            
            
        def load_jackpot_anim(self,timer=3):
            self.bgnd_anim = "dmd/bonus_whip.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            anim_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,hold=True,frame_time=6)
            anim_layer.composite_op ="blacksrc"
            
            award_layer = dmd.TextLayer(106, 4, self.game.fonts['23x12'], "center", opaque=False)
            award_layer.set_text(str(self.jackpot_count),color=dmd.RED)

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [award_layer,anim_layer])

            self.cancel_delayed('reset_display')
            self.delay(name='reset_display', event_type=None, delay=timer, handler=self.load_bgnd_anim)
                
           
        def mode_progression(self):
            #update count
            self.jackpot_count += 1 
            #update screen
            self.load_jackpot_anim()
            #score
            self.score(self.base_value*self.jackpot_count)
            #sound
            self.game.sound.play("jackpot_jingle")
            #lamp effects
            self.game.lampctrl.play_show('jackpot', repeat=False,callback=self.game.update_lamps)

            
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
        def sw_rightRampEnter_active(self, sw):
            if self.game.switches.rightRampEnter.time_since_change()>1 and not self.mode_expired:
                self.game.sound.play('jackpot_attempt')
                
        def sw_rightRampMade_active(self, sw):
            if self.game.switches.rightRampMade.time_since_change()>1 and not self.mode_expired:
                self.mode_progression()
                return procgame.game.SwitchStop
        
        def sw_captiveBallRear_inactive(self, sw):
            return procgame.game.SwitchStop

        def sw_captiveBallFront_inactive_for_200ms(self, sw):
            return procgame.game.SwitchStop
 
        
        def sw_grailEject_active_for_250ms(self,sw): 
            self.bonus()
            return procgame.game.SwitchStop
        