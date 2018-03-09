# Streets Of Cairo Game Mode

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


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



class Adventure(game.Mode):

	def __init__(self, game, priority):
            super(Adventure, self).__init__(game, priority)
            
            self.log = logging.getLogger('ij.adventure')

            #screen setup
           
            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            self.score_layer.composite_op ="blacksrc"
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"

            #sound setup
            self.game.sound.register_sound('adv_fanfare', sound_path+"fanfare_path_modes.aiff")
            self.game.sound.register_sound('adv_shot_unlit', sound_path+'poa_lane_lit.aiff')
            self.game.sound.register_sound('adv_shot_lit', sound_path+'poa_lane_unlit_1.aiff')
            self.game.sound.register_sound('adv_shot_lit', sound_path+'poa_lane_unlit_2.aiff')
            self.game.sound.register_sound('adv_shot_lit', sound_path+'poa_lane_unlit_3.aiff')
            
            self.game.sound.register_sound('adv_well_done', speech_path+"well_done_my_friend-01.aiff")
            #self.game.sound.register_sound('adv_well_done', speech_path+"well_done-03.aiff")
            #self.game.sound.register_sound('adv_well_done', speech_path+"nice_shot_1-01.aiff")
            #self.game.sound.register_sound('adv_well_done', speech_path+"nice_shot_2-01.aiff")
            #self.game.sound.register_sound('adv_well_done', speech_path+"nice_shot_3-01.aiff")


            #lamps setup
            self.arrow_lamps = ['leftLoopArrow','crusadeArrow','templeArrow','raidersArrow','rightRampArrow','rightLoopArrow']
            self.jones_lamps = ['jonesJ','jonesO','jonesN','jonesE','jonesS']
            self.jones_lamps_movement = ['jonesJ','jonesO','jonesN','jonesE','jonesS','jonesE','jonesN','jonesO']

            self.smart_bomb_lamp = 'tournamentStartButton'
            
            
            #setup the switches which pause an active poa 
            self.pausing_switchnames = []
            for switch in self.game.switches.items_tagged('poa_pause'):
                self.pausing_switchnames.append(switch.name)
                self.log.debug("Adventure Pausing Switch is:"+switch.name)
                    
            for switch in self.pausing_switchnames:
		self.add_switch_handler(name=switch, event_type='active', \
			delay=None, handler=self.adventure_paused)  
            


        def reset(self):
            #var setup
            self.count = 0
            self.timer = self.game.user_settings['Gameplay (Feature)']['Adventure Challenge Timer']
            self.pause_length = self.game.user_settings['Gameplay (Feature)']['Mode Timers Pause Length']
            self.adventure_flags = [False,False,False,False,False,False]
           
            self.score_value_boost = 1000000 #1mil
            self.score_value_start = 10000000 #10mil
            self.score_value_bonus = 2000000 #2mil
            self.score_value_extra = 1000000 #1mil
            
            self.jones_count = 0 #count to track the jones lamp active
            self.jones_target_value = 10000
            #self.jones_lamp_lit = False
            
            self.total_score = 0
            
            self.reset_lamps()
            

        def load_progress_anim(self):
            anim = dmd.Animation().load(game_path+"dmd/5_million.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            self.delay(name='reload_bgnd', event_type=None, delay=1, handler=self.load_bgnd_anim)


        def load_bgnd_anim(self):
            bgnd_anim = dmd.Animation().load(game_path+"dmd/poa_continue_bgnd.dmd")
            bgnd_layer = dmd.FrameLayer(frame=bgnd_anim.frames[0])

            self.score_layer.x = 48
            self.score_layer.y=0
            self.score_layer.justify='center'

            info_layer1 = dmd.TextLayer(48, 14, self.game.fonts['5px_az'], "center", opaque=False)
            info_layer2 = dmd.TextLayer(48, 22, self.game.fonts['5px_az'], "center", opaque=False)

            mode_text = "SHOOT "+str(len(self.adventure_flags)-self.count)+" ARROWS TO"
            info_layer1.set_text(mode_text, color=dmd.CYAN)
            info_layer2.set_text("COMPLETE ADVENTURE",  color=dmd.CYAN)

            self.timer_layer = dmd.TimerLayer(115, 4, self.game.fonts['23x12'],self.timer,"right")

            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer1,info_layer2,self.score_layer,self.timer_layer])
            #reset timer for each attempt
            self.cancel_delayed('adventure_timer')
            self.delay(name='adventure_timer', event_type=None, delay=self.timer, handler=self.expired)


        def load_completed_anim(self):
            pass


        def mode_started(self):
            self.reset()
            
            #load player stats
            #self.adventure_flags = self.game.get_player_stats('adventure_flags')
            self.smart_bombs = self.game.get_player_stats('adventure_smart_bombs')

            self.game.set_player_stats('mode_blocking',True)
            self.game.set_player_stats('adventure_started',True)
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(0, -1, self.game.fonts['07x5'],self.timer,"left")
            self.timer_layer.composite_op ="blacksrc"
            self.info_layer = dmd.TextLayer(128/2, 20, self.game.fonts['07x5'], "center", opaque=False)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music, speech & sounds
            #self.game.sound.play_music('soc_background_play', loops=-1)
            #self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=self.count)

            #update effects
            #self.game.effects.drive_flasher('flasherSwordsman','fast',time=2)

            #update_lamps
            self.jones_lamp_sequence()
            self.update_lamps()


        def mode_stopped(self):
            #save player stats

            #self.game.set_player_stats('adventure_flags',self.adventure_flags)
            self.game.set_player_stats('adventure_smart_bombs',self.smart_bombs)
             
            self.game.set_player_stats('poa_score',self.total_score)
            self.game.set_player_stats('last_mode_score',self.total_score)
            
            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')
            
            self.cancel_delayed('adventure_timer')

            #clear display
            self.clear()
            
            self.game.set_player_stats('mode_blocking',False)
            self.game.set_player_stats('adventure_started',False)

            #restore lamps
            self.reset_lamps()
            self.game.update_lamps()


        def mode_tick(self):
            pass


        def voice_call(self,count,delay=None,label="adv_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

        
        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True),color=dmd.YELLOW)
            
            
        def adventure_paused(self,sw):    
            self.timer_layer.pause(True)
            self.cancel_delayed('adventure_timer')
            self.cancel_delayed('adventure_unpause')
            self.delay(name='adventure_unpause', delay=self.pause_length,handler=self.adventure_unpaused)
            
            
        def adventure_unpaused(self):
            self.timer_layer.pause(False) 
            self.delay(name='adventure_timer', event_type=None, delay=self.timer_layer.get_time_remaining(), handler=self.expired)
        
     

        def mode_progression(self,num):

            if self.adventure_flags[num] == False:
                self.count+=1
                if self.count==len(self.adventure_flags):
                    self.completed()
                else:
                    self.load_progress_anim()
                    self.adventure_flags[num] = True
            
                    #lamp effects
                    self.gi_flutter()
                    self.award_score()
            
                    #play sound
                    self.game.sound.play('adv_shot_lit')
                self.update_lamps()
            else:
                  self.game.sound.play('adv_shot_unlit')  
                  self.game.score(self.score_value_extra) 
               
                  
        def spot_shot(self):
            for i in range (len(self.arrow_lamps)):
                if not self.adventure_flags[i]:
                    self.mode_progression(i)
                    break


        def completed(self):
            self.load_completed_anim()
            #speech
            self.game.sound.play('adv_well_done')
            
            self.game.base_game_mode.poa.adventure_continue() #link back to poa mode
            self.game.modes.remove(self)
        
        
        def expired(self):
            self.game.base_game_mode.poa.adventure_expired() #link back to poa mode
            self.game.modes.remove(self)
            
            
        def award_score(self,score_value=0):
            score_value = self.score_value_start + ((self.count-1)*(self.score_value_start/2)) 
            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3,color=dmd.CYAN)
            self.game.score(score_value)
            self.total_score +=score_value


        def mode_bonus(self):
            self.game.score(score_value_bonus)
            
        
        def store_smart_bomb(self,value=1):
             self.smart_bombs+=value
             if self.smart_bombs>0:
                self.game.effects.drive_lamp(self.smart_bomb_lamp_button,'fast')
             else:
                self.game.effects.drive_lamp(self.smart_bomb_lamp_button,'off')
            
            
        def eject_ball(self):
            #create eject delay
            self.delay(name='eject_delay', event_type=None, delay=0.5, handler=self.game.coils.grailEject.pulse)
            
            
        def gi_flutter(self):
            self.log.info("GI FLUTTER")
            self.game.lamps.playfieldGI.schedule(0x000C0F0F,cycle_seconds=1)
                     
        
        def jones_progress(self,num):
            lamp_order = [0,1,2,3,4,3,2,1]
            if lamp_order[self.jones_count]==num: # and self.jones_lamp_lit:
                self.spot_shot()
            else:
                self.game.sound.play('adv_shot_unlit')
                self.game.score(self.jones_target_value)
                
            
        def reset_lamps(self):
            for i in range(len(self.arrow_lamps)):
                self.game.effects.drive_lamp(self.arrow_lamps[i],'off')
            
            for i in range(len(self.jones_lamps)):
                self.game.effects.drive_lamp(self.jones_lamps[i],'off')


        def update_lamps(self):
            for i in range(len(self.arrow_lamps)):
                if self.adventure_flags[i]==True:
                    self.game.effects.drive_lamp(self.arrow_lamps[i],'off')
                else:
                    self.game.effects.drive_lamp(self.arrow_lamps[i],'fast')
                
            #jones_lamp update - this should restore the sequence to where it was. cancel timings should still be in place
            lamp_order = [0,1,2,3,4,3,2,1]
            for i in range(len(self.jones_lamps)):
                if lamp_order[self.jones_count]==i:
                    self.game.lamps[self.jones_lamps[i]].schedule(schedule=0x99999999, cycle_seconds=0, now=True)
                    #self.game.effects.drive_lamp(self.jones_lamps[i],'fast')
                else:
                    self.game.lamps[self.jones_lamps[i]].disable()
                    #self.game.effects.drive_lamp(self.jones_lamps[i],'off')
           
                    
        def showcase_arrow_lamps(self):
            for lamp in self.game.lamps:
                lamp.disable()
                
            for lamp in self.arrow_lamps:
                self.game.effects.drive_lamp(lamp,'fast')
    
                    
        def jones_lamp_sequence(self):
            #create a strip of moving lights, single lamp on for 2 secs with a 3 sec sequence timer
            self.cancel_delayed('jones_lamp')
            self.cancel_delayed('jones_lamp_repeat')
            timer=0
            interval=1.9
            for lamp in self.jones_lamps_movement:
                self.delay(name='jones_lamp',delay=timer,handler=self.set_jones_lamp,param=lamp) #lambda: self.game.zwLamps.timedon(num,'white',interval))
                timer+=interval

            self.delay(name='jones_lamp_repeat',delay=timer,handler=self.jones_lamp_sequence)
            

        def set_jones_lamp(self,lamp):
            interval=2

            self.game.lamps[lamp].schedule(schedule=0x99999999, cycle_seconds=interval, now=True)
            #self.jones_lamp_lit = True
            self.jones_count +=1
            if self.jones_count>=len(self.jones_lamps_movement):
                self.jones_count = 0
            self.log.info("jones_count:%s",self.jones_count)
            self.cancel_delayed('sb_'+lamp+'_off')
            self.delay(name='sb_'+lamp+'_off', delay=interval, handler=self.disable_jones_lamp, param=lamp)
            
            
        def disable_jones_lamp(self,lamp):
            self.game.effects.drive_lamp(lamp,'off')
            self.jones_lamp_lit = False


        def clear(self):
            self.layer = None


        #switch handlers
    
        def sw_leftLoopTop_active(self, sw):
            if self.game.switches.rightLoopTop.time_since_change()>1 and self.game.base_game_mode.poa.adventure_started:
                self.mode_progression(0)

            return procgame.game.SwitchStop
        
        def sw_grailEject_active_for_200ms(self, sw):
            if self.game.base_game_mode.poa.adventure_started:
                self.mode_progression(1)
                self.eject_ball()
                
            return procgame.game.SwitchStop

        def sw_templeStandup_active(self, sw):
            if self.game.base_game_mode.poa.adventure_started:
                self.mode_progression(2)
            
            return procgame.game.SwitchStop

        def sw_arkHit_active(self, sw):
            if self.game.switches.arkHit.time_since_change()>1 and self.game.base_game_mode.poa.adventure_started:
                self.mode_progression(3)

            return procgame.game.SwitchStop
        
        def sw_rightRampMade_active(self, sw):
            if self.game.switches.rightRampMade.time_since_change()>1 and self.game.base_game_mode.poa.adventure_started:
                self.mode_progression(4)
                
            return procgame.game.SwitchStop

        def sw_rightLoopTop_active(self, sw):
            if self.game.switches.leftLoopTop.time_since_change()>1 and self.game.base_game_mode.poa.adventure_started:
                self.mode_progression(5)

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
            
                
        def sw_tournamentStart_active(self, sw):
            if self.smart_bombs>0 and self.game.modes.base_game_mode.poa.adventure_started:
                
                self.completed()
                self.store_smart_bomb(-1)

            return procgame.game.SwitchStop
 
        