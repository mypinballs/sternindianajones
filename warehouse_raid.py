# Warehouse Raid Game Mode - 2 ball Multiball
# Jim
# September 2016


import procgame
import locale
import logging
import random
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font, mode, justify, opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font, justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()
            
            

class Warehouse_Raid(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Warehouse_Raid, self).__init__(game, priority)

            self.log = logging.getLogger('ij.wellOfSouls')
            #setup link back to mode_select mode
            self.mode_select = mode_select

            #user defined game settings config
            self.bip_start = int(self.game.user_settings['Gameplay (Feature)']['Warehouse Raid BIP Start'])
            self.ball_save_time = int(self.game.user_settings['Gameplay (Feature)']['Warehouse Raid Ball Save Timer'])
            self.hold_timeout = int(self.game.user_settings['Gameplay (Feature)']['Warehouse Hold Timer'])
            self.log.info("Warehouse Raid BIP Start is: "+str(self.bip_start))
            self.log.info("Warehouse Raid Ball Save Time is: "+str(self.ball_save_time))

            #screen setup
            #self.score_layer = ModeScoreLayer(128/2, 0, self.game.fonts['num_09Bx7'], self,"center")
            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['9x7_bold'], self,"center")
            self.score_layer.composite_op ="blacksrc"
            self.info_layer = dmd.TextLayer(128/2, 26, self.game.fonts['07x5'], "center", opaque=False)
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op='blacksrc'
            self.box_layer = dmd.TextLayer(22, 11, self.game.fonts['8x6'], "left", opaque=False)
            
            #sound setup
            self.game.sound.register_music('warehouse_background_play', music_path+"warehouse_raid.aiff")
            self.game.sound.register_sound('warehouse_shot_hit', sound_path+"whoosh.aiff")
            self.game.sound.register_sound('warehouse_item_collected', sound_path+"fanfare_path_modes.aiff")
            self.game.sound.register_sound('warehouse_item_timed_out', sound_path+"flames.aiff")
            self.game.sound.register_sound('warehouse_electricity', sound_path+"electricity_short.aiff")
            self.game.sound.register_sound('warehouse_s0', speech_path+"ij4030E_you_look_lost.aiff")
            self.game.sound.register_sound('warehouse_s1', speech_path+"ij4031F_maybe_but_not_today.aiff")
            #self.game.sound.register_sound('warehouse_s2', speech_path+"xxx.aiff")
            #self.game.sound.register_sound('warehouse_s3', speech_path+"xxx.aiff")

            #lamps setup
            self.lamps = ['rightRampArrow']


        def reset(self):
            #var setup
            self.count = 0
            self.score_value_boost = 1000000
            self.score_value_start = 1000000
            self.score_value_bonus = 2000000
            self.award = 0
            self.running_total = 0
            self.mode_running=False
            self.reset_drop_count = 6


        def load_scene_anim(self,count):

            #set the scene number to load depending on shots made
            #only 1 scene for this mode
            scene_num=1
            self.create_award()
            
            self.scene_anim = "dmd/match_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.scene_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=6)
            self.scene_layer.composite_op ="blacksrc"
            self.scene_layer.add_frame_listener(-2,self.award_score)
            #self.scene_layer.add_frame_listener(-1, self.load_bgnd_anim)
            self.cancel_delayed('reload_bgnd_anim')
            self.delay(name='reload_bgnd_anim',delay=2,handler=self.load_bgnd_anim)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.box_layer,self.scene_layer,self.score_layer,self.info_layer,self.award_layer])


        def load_bgnd_anim(self):   
            self.bgnd_anim = dmd.Animation().load(game_path+"dmd/match_bgnd.dmd")
            self.bgnd_layer = dmd.FrameLayer(frame=self.bgnd_anim.frames[0])
            #create random electricity!
            electricity_x = random.randint(25,29)
            electricity_y = random.randint(8,17)
            electricity_anim = dmd.Animation().load(game_path+"dmd/box_electricity.dmd")
            self.electricity_layer = dmd.AnimatedLayer(frames=electricity_anim.frames,hold=False,opaque=False,repeat=True,frame_time=6)
            self.electricity_layer.composite_op ="blacksrc"
            self.electricity_layer.target_x=electricity_x
            self.electricity_layer.target_y=electricity_y
            self.electricity_layer.add_frame_listener(1,self.electricity_sound)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.electricity_layer,self.score_layer,self.info_layer])
            
            self.delay(name='reload_bgnd_anim',delay=5,handler=self.load_bgnd_anim)


        def electricity_sound(self):
            self.game.sound.play('warehouse_electricity')
            

        def mode_started(self):
            self.reset()
            
            #load player stats
            self.items_collected = self.game.get_player_stats('warehouse_items_collected');

            #set mode player stats
            self.game.set_player_stats('multiball_mode_started',True)
            
            self.running_total += int(self.game.user_settings['Gameplay (Feature)']['Mode Start Value (Mil)'])*1000000
        
            #setup additonal layers
            self.info_layer.set_text("SHOOT RAMP TO LOCATE ITEMS",color=dmd.MAGENTA,blink_frames=10)
            
            #turn on coils and flashers
            self.game.effects.drive_flasher('flasherKingdom','medium',time=0)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music, speech & sounds
            self.game.sound.play_music('warehouse_background_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=self.count)
            

            self.game.trough.launch_balls(self.bip_start-self.game.trough.num_balls_in_play, self.ball_launch_callback, False)
            #debug trough
            #self.game.trough.debug()

            #start ball save
            self.game.ball_save.start(time=self.ball_save_time)


            #update_lamps
            self.update_lamps()



        def mode_stopped(self):
            #save player stats
            self.items_collected+=self.running_total
            self.game.set_player_stats('warehouse_items_collected',self.running_total)

            score_value = self.running_total
            self.game.set_player_stats('warehouse_raid_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)

            #update poa & mode player stats
            self.game.set_player_stats("multiball_mode_started",False)
            self.game.set_player_stats("poa_queued",False)

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #cancel flasher
            self.game.coils.flasherKingdom.disable()
            self.game.coils.flasherSkull.disable()
            
            #cancel any locks
            self.release_ball()
            
            #reset music
            #self.game.sound.stop_music()
            #self.game.sound.play_music('general_play', loops=-1)

            #update idol state
            #self.game.idol.home()

            #clear display
            self.clear()

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            if self.game.trough.num_balls_in_play==1 and self.mode_running:
                self.mode_select.end_scene()


        def ball_launch_callback(self):

            if self.game.trough.num_balls_to_launch==0:
                self.mode_running=True
                self.log.info("Warehouse Raid: Mode Running")
                self.game.effects.drive_flasher('flasherSkull','fast',time=3)

            self.game.ball_save.start(num_balls_to_save=self.bip_start, time=self.ball_save_time, now=True, allow_multiple_saves=True)


        def voice_call(self,count,delay=None,label="warehouse_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
            if count==0:
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=self.game.sound.play(label+str(count))+1, handler=self.voice_call, param=1)


        def sound_call(self,count,delay=None,label="warehouse_s"):
            if delay==None:
                self.game.sound.play(label+str(count))
            else:
                self.delay(name='mode_sound_delay', event_type=None, delay=delay, handler=self.sound_call, param=count)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
       

        def mode_progression(self):

            self.cancel_delayed('warehouse_hold_timeout')
            
            if self.count==1:
                 #load progression animation
                self.load_scene_anim(self.count)
                 #play sound
                self.game.sound.play('warehouse_item_collected')
                self.release_ball()
                self.count= 0
                self.running_total+=1
                
            else:
                self.count=1
                self.stop_ball()
                self.game.sound.play('warehouse_shot_hit')
                self.delay(name='warehouse_hold_timeout',delay=self.hold_timeout,handler=self.cancel_warehouse_hold)
                
                
        def cancel_warehouse_hold(self):
            #cancel counter and release ball from hold after timeout
            self.release_ball()
            self.count= 0


        def create_award(self):
            rand_num = random.randint(1,5)
            self.award = rand_num*5
            #self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3,color=dmd.GREEN)
            self.box_layer.set_text(str(self.award)+'M',color=dmd.GREEN)
           
            
        def award_score(self):
            self.game.score(self.award*self.score_value_start)
            #update runing total - needed for this mode as can't be calculated at end
            self.running_total +=self.award*self.score_value_start
            
            
        def stop_ball(self):
            self.game.coils.rampBallStop.patter(2,20,self.game.coils.rampBallStop.default_pulse_time,True)
    
    
        def release_ball(self):
            self.game.coils.rampBallStop.disable()


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'fast')

        def clear(self):
            self.layer = None


        #switch handlers
        
        def sw_rightRampMade_active(self,sw):
            if self.game.switches.rightRampMade.time_since_change()>1:
                self.mode_progression()
                return procgame.game.SwitchStop

        def sw_shooterLane_active_for_500ms(self,sw):
            self.game.coils.ballLaunch.pulse(50)
            #debug
            self.log.info("Warehouse Raid Debug: Balls in Trough is:,%s",self.game.trough.num_balls())
            self.log.info("Warehouse Raid Debug: Balls in Play %s",self.game.trough.num_balls_in_play)
            return procgame.game.SwitchStop

