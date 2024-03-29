#Moonlight Madness Mode

import procgame
import locale
import random
import logging
import audits
from procgame import *
from mode_select import *

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

class Final_Adventure(game.Mode):

	def __init__(self, game, priority):
            super(Final_Adventure, self).__init__(game, priority)

            self.log = logging.getLogger('ij.final_adventure')

            self.game.sound.register_music('multiball_play', music_path+"multiball.aiff")
            self.game.sound.register_music('multiball_end', music_path+"bonus.aiff")
            self.game.sound.register_sound('multiball_finish', sound_path+"bonus_end_jingle.aiff")

            self.game.sound.register_sound('multiball_start_speech', speech_path+"oh_shit.aiff")
            self.game.sound.register_sound('hit_jackpot', speech_path+"hit_the_jackpot.aiff")
            self.game.sound.register_sound('jackpot1', speech_path+"jackpot.aiff")

            self.game.sound.register_sound('random_sound1', sound_path+"punch_1.aiff")
            self.game.sound.register_sound('random_sound2', sound_path+"punch_2.aiff")
            self.game.sound.register_sound('random_sound3', sound_path+"punch_3.aiff")
            self.game.sound.register_sound('random_sound4', sound_path+"punch_4.aiff")
            self.game.sound.register_sound('random_sound5', sound_path+"adv_target_1.aiff")
            self.game.sound.register_sound('random_sound6', sound_path+"adv_target_2.aiff")
            self.game.sound.register_sound('random_sound7', sound_path+"adv_target_3.aiff")
            self.game.sound.register_sound('random_sound8', sound_path+"adv_target_4.aiff")
            self.game.sound.register_sound('random_sound9', sound_path+"inlane_.aiff")
            self.game.sound.register_sound('random_sound10', sound_path+"sling_1.aiff")
            self.game.sound.register_sound('random_sound11', sound_path+"cow_3.aiff")
            self.game.sound.register_sound('random_sound12', sound_path+"glass_smash.aiff")

            self.game.sound.register_sound('saucer_eject', sound_path+"saucer_eject.aiff")
            
            banner1 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mm_bang.dmd").frames[0])
            banner2 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mm_boom.dmd").frames[0])
            banner3 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mm_crash.dmd").frames[0])
            banner4 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mm_doho.dmd").frames[0])
            banner5 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mm_powie.dmd").frames[0])
            banner6 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mm_zap.dmd").frames[0])
            self.banners = [banner1,banner2,banner3,banner4,banner5,banner6]
            
            self.title_layer = dmd.TextLayer(128/2, 2, self.game.fonts['5px_az'], "center")
            self.score_layer = ModeScoreLayer(128/2, 10, self.game.fonts['num_14x10'], self, "center")
            self.info_layer = dmd.TextLayer(128/2, 23, self.game.fonts['5px_az'], "center")

            self.flashers = ['flasherJets','flasherBackpanel','flasherRamp','flasherArkFront']

            self.enter_value = 10
            self.made_value_base = 50000
            self.made_value_boost = 10000
            self.made_value_max = 100000
            self.super_combo_multiplier = 10
            self.combo_multiplier = 2
            self.base_value = 250000
            self.jackpot_base = 25000000
            self.jackpot_boost = 20000000
            
            
            self.balls_needed = 4 #number of ball for this mode
            self.ball_save_time = 20
            self.next_ball_ready = False
            self.virtual_lock = False
            self.multiball_info_text_flag = 0
            self.end_callback= None
            

            self.moonlight_switchnames = []
            for switch in self.game.switches.items_tagged('moonlight'):
                self.moonlight_switchnames.append(switch.name)

            # Install switch handlers.
            for switch in self.moonlight_switchnames:
		self.add_switch_handler(name=switch, event_type='active',delay=None, handler=self.progress)
                
        
        def reset(self):
            self.count = 0
            self.million_count = 0
            self.total = 0
            self.played_flag = False
            self.ball_ejected = False
            self.start_finish = False
            self.start_cleanup = False
            self.jackpot_value = self.jackpot_base
            self.jackpot_x = 1
            self.jackpot_collected = 0
            self.jackpot_status = 'notlit'
             
            self.reset_display_flag()
            self.reset_combos()
            self.reset_mechs()
            

        def reset_combos(self):
            self.combo = False
            self.super_combo = False

        def reset_display_flag(self):
            self.progress_text_runnning = False
                 
        def reset_mechs(self):
            self.game.temple.close()

#        def update_lamps(self):
#            for i in range(self.lamps):
#                self.game.effects.drive_lamp(self.lamps[i],'on')
#

        def multiball_lamps(self, enable=True):
            # Start the lamps doing a crazy rotating sequence:
            schedules = [0xffff000f, 0xfff000ff, 0xff000fff, 0xf000ffff, 0x000fffff, 0x00fffff0, 0x0fffff00, 0xfffff000]
            for index, lamp in enumerate(sorted(self.game.lamps, key=lambda lamp: lamp.number)):
                if enable:
                    sched = schedules[index%len(schedules)]
                    lamp.schedule(schedule=sched, cycle_seconds=0, now=False)
                else:
                    lamp.disable()


        def gi_flutter(self):
            self.log.info("GI FLUTTER")
            self.game.lamps.playfieldGI.schedule(0x000C0F0F,cycle_seconds=1)
            
        def gi(self,enable=True):
            if enable:
                self.game.lamps.playfieldGI.disable()
            else:
                #self.game.lamps.playfieldGI.enable()
                self.game.lamps.playfieldGI.patter(on_time=10,off_time=0)
            
            self.game.base_game_mode.pops.lighting(enable)
            
            
            
        def mode_started(self):
            self.reset()
            
            #setup player stats
            self.multiball_ready = self.game.get_player_stats('multiball_ready')
            self.multiball_started = self.game.get_player_stats('multiball_started')
            self.multiball_running = self.game.get_player_stats('multiball_running')         

            #cleanup lamps & flashers
            self.game.effects.drive_lamp('grail','off')
            self.game.effects.drive_flasher('flasherCrusade','off')
            
                
            #set gi
            self.gi_flutter()

            #start
            self.multiball_start()

            #reset tracking
            self.reset()
           
            
        def mode_stopped(self):
            #tidy up
            self.multiball_ready = False
            self.game.set_player_stats('multiball_ready',self.multiball_ready)

            #set the played flag to true so only happens once per player if enabled
            self.played_flag = True
            self.game.set_player_stats('final_adventure_status',self.played_flag)
            #store the total value for the round
            self.game.set_player_stats('final_adventure_total',self.total)
            
            #reset mode select scenes
            self.game.base_game_mode.mode_select.reset_scenes()
            
            #continue game
            self.game.trough.launch_balls(1)
            self.game.enable_flippers(enable=True)
            self.game.utility.resume_mode_music()
            
            self.game.set_player_stats('final_adventure_started',False)


        def mode_tick(self):
            if self.multiball_started:
                self.balls_in_play = self.game.trough.num_balls_in_play

                #debug
                #self.balls_in_play=3
                #-------------------------------------------
                #debug_ball_data = str(self.balls_in_play)+":"+str(self.game.trough.num_balls())+":"+str(self.game.trough.num_balls_locked)+":"+str(self.game.trough.num_balls_to_launch)+":"+str(self.multiball_running)
                #self.game.set_status(debug_ball_data)
                #self.game.score_display.set_text(debug_ball_data.upper(),1,'left')
                #self.log.debug(debug_ball_data)
                #-------------------------------------------

                if self.balls_in_play==self.balls_needed and self.multiball_running==False:
                    #start tracking
                    self.multiball_running = True;
                    self.game.set_player_stats('multiball_running',self.multiball_running)


                if self.multiball_running:
                    self.multiball_tracking()

                
        def display_start(self,time=0):             
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
            info_top_layer = dmd.TextLayer(128/2, 1, self.game.fonts['14x9_bold'], "center")
            info_bottom_layer = dmd.TextLayer(128/2, 15, self.game.fonts['14x9_bold'], "center")
            info_top_layer.composite_op='blacksrc'
            info_bottom_layer.composite_op='blacksrc'
            info_top_layer.set_text("Final".upper(), color=dmd.PURPLE)
            info_bottom_layer.set_text("Adventure".upper(), color=dmd.PURPLE)
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_top_layer,info_bottom_layer])
            
            self.delay(name='display_mode_info_delay',delay=time,handler=self.display_info)

        
        def display_info(self):
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
            self.title_layer.set_text("Final Adventure".upper(), color=dmd.PURPLE)
            self.info_layer.set_text("All Switches = ".upper()+str(locale.format("%d", self.base_value, True)), color=dmd.CYAN)
            #self.title_layer.composite_op='blacksrc'
            #self.info_layer.composite_op='blacksrc'
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.title_layer,self.score_layer,self.info_layer])
            
            self.reset_display_flag()

            
        def display_progress(self,time=3):
            num = random.randint(0,len(self.banners)-1)
            self.progress_text_runnning = True
            self.layer = self.banners[num]
            self.delay(name='animation_end_delay', event_type=None, delay=time, handler=self.display_info)


        def display_total(self,time=0):   
            self.cancel_delayed('animation_end_delay')
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
            title_layer = dmd.TextLayer(128/2, 4, self.game.fonts['8x6'], "center")
            value_layer = ModeScoreLayer(128/2, 15, self.game.fonts['num_14x10'], self)
            title_layer.set_text("Adventure Total".upper(), color=dmd.PURPLE)
            value_layer.set_text(locale.format("%d", self.total, True), color=dmd.GREEN)
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,value_layer,title_layer])
            
            self.delay(name='minimum_total_score_display_timer',delay=time,handler=self.start_cleanup_allowed)


        def display_finish(self,time=0):             
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
            info_top_layer = dmd.TextLayer(128/2, 6, self.game.fonts['9x7_bold'], "center")
            info_bottom_layer = dmd.TextLayer(128/2, 18, self.game.fonts['9x7_bold'], "center")
            info_top_layer.set_text("And Now Back".upper(), color=dmd.CYAN)
            info_bottom_layer.set_text("To The Game".upper(), color=dmd.CYAN)
            
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_top_layer,info_bottom_layer])
            
        def jackpot_collected_display(self,num):
            self.cancel_delayed('animation_end_delay')
            anim = dmd.Animation().load(game_path+"dmd/jackpot.dmd")
            animation_layer = dmd.AnimatedLayer(frames=anim.frames,repeat=True,frame_time=6)
            self.layer = animation_layer
            self.delay(name='jackpot_explode_delay',delay=4,handler=self.jackpot_explode_display)

        def jackpot_explode_display(self):
            anim = dmd.Animation().load(game_path+"dmd/jackpot_explode.dmd")
            animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=6)
            animation_layer.add_frame_listener(-1,self.jackpot_reset)
            self.layer = animation_layer

        def jackpot_reset(self):
            self.jackpot('unlit')
            self.display_info()


        def strobe_flashers(self,time=0.1,repeats=4):
            self.game.effects.strobe_flasher_set(self.flashers,time=time,overlap=0.2,repeats=repeats)
            

        def progress_flashers(self,time=0.1,repeats=2):
            sequence = []

            #playfield flashers
            flashers = self.flashers
            sequence+=flashers
            flashers.reverse()
            sequence+flashers

            self.game.effects.strobe_flasher_set(self.flashers,time=time,overlap=0.2,repeats=repeats)


        def play_sound(self):

            list =["random_sound1","random_sound2","random_sound3","random_sound4","random_sound5","random_sound6","random_sound7","random_sound8","random_sound9","random_sound10","random_sound11","random_sound12"]
            i= random.randint(0, len(list)-1)
            self.game.sound.play(list[i])


        def multiball_start(self):
            self.log.debug('multiball start reached')

            #update the flag
            self.multiball_started = True
            self.game.set_player_stats('multiball_started',self.multiball_started)
            
            self.game.set_player_stats('final_adventure_started',True)

            #display mode info
            self.display_start(3)

            #play speech
            start_speech_length = self.game.sound.play_voice('multiball_start_speech')

            #change music
            self.game.sound.stop_music()
            self.game.sound.play_music('multiball_play',loops=-1)
            self.log.info('multiball music started')

            self.delay(name='multiball_eject_delay',delay=start_speech_length+1, handler=self.multiball_eject)

            audits.record_value(self.game,'finalAdventureStarted')


        def multiball_eject(self):
            self.log.debug('multiball eject reached')
             
            #launch balls
            #self.game.trough.launch_balls(self.balls_needed-self.game.idol.balls_in_idol-1, self.ball_launch_callback, False)
            self.game.trough.launch_balls(self.balls_needed,stealth=False) #launch balls

            #queue multiball effects
            self.delay(name='multiball_effects_delay',delay=0.5, handler=self.multiball_effects)


        def multiball_effects(self):
            #jackpot lit
            self.jackpot(self.jackpot_status)

            #run flasher effects
            self.strobe_flashers()

            #start lamp effects
            self.multiball_lamps()

            #turn on ball save
            self.game.ball_save.start(num_balls_to_save=self.balls_needed,allow_multiple_saves=True,time=self.ball_save_time)


        def multiball_tracking(self):
            #end check
            if self.balls_in_play<=1 and not self.start_finish:
                
                #update flag
                self.start_finish = True
            
                #cancel award
                self.jackpot('cancelled')
                
                #update base mode so game can continue uninterupted by drain when ready
                self.game.base_game_mode.ball_served = False
                self.game.base_game_mode.ball_starting = True

                #disable all lamps
                for lamp in self.game.lamps:
                    lamp.disable()

                #stop music
                self.game.sound.stop_music()
                self.game.sound.play_music('multiball_end',loops=0)

                #multiball ended callback
                if self.end_callback:
                    self.log.debug('Final Adventure End Callback Called')
                    self.end_callback()

                #disable flippers
                self.game.enable_flippers(enable=False)
                #reset GI
                self.gi(enable=True)

                #calc total & display
                self.total = (self.count*self.base_value)+(self.jackpot_collected*self.jackpot_value)
                self.display_total(time=4) #sets start_cleanup flag after delay
                

            elif self.balls_in_play==0 and self.start_cleanup: #all balls now drained and cleanup flag set

                #end tracking & update player stats
                self.multiball_running=False
                self.multiball_started = False
                self.multiball_ready = False

                self.game.set_player_stats('multiball_running',self.multiball_running)
                self.game.set_player_stats('multiball_started',self.multiball_started)
                self.game.set_player_stats('multiball_ready',self.multiball_ready)
                
                #play end jingle
                self.game.sound.fadeout_music()
                self.game.sound.play('multiball_finish')

                wait =2
                self.display_finish(wait)
                self.delay(delay=wait,handler=self.finish)    
                
        
        def ball_launch_callback(self):
            if self.game.trough.num_balls_to_launch==0:
                self.game.ball_save.start(num_balls_to_save=self.balls_needed, time=self.ball_save_time, now=True, allow_multiple_saves=True)
    
    
        def start_cleanup_allowed(self):
            #update flag
            self.start_cleanup = True

        def finish(self):
            self.game.modes.remove(self)


        def jackpot(self,status=None):
                self.jackpot_status = status
                
                if status=='lit':
                    self.game.coils.flasherArkFront.disable()
                    self.game.coils.flasherSkull.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)

                    #speech
                    self.game.sound.play('hit_jackpot')

                elif status=='unlit':
                    self.game.coils.flasherArkFront.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)            
                   
                elif status=='made':
                    self.game.coils.flasherSkull.disable()
                    self.game.effects.drive_shaker('medium')
                   
                    self.game.score(self.jackpot_value*self.jackpot_x)
                    self.jackpot_collected+=1
                    
                    #update display
                    self.jackpot_collected_display(self.jackpot_collected)

                    #speech
                    self.game.sound.play('jackpot'+str(self.jackpot_x))    

                elif status=='cancelled':
                    self.game.coils.flasherArkFront.disable()
                    self.game.coils.flasherSkull.disable()
            
            
        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)


        def progress(self,sw):
            if self.multiball_running and not self.start_finish:
                if not self.progress_text_runnning:
                    self.display_progress()
                self.game.score(self.base_value)
                self.progress_flashers()
                self.play_sound()

                self.count+=1
            

        #switch handlers
        #-------------------------
                
        def sw_captiveBallRear_active(self, sw):
            if self.multiball_running:
                value = 2000000
                self.jackpot_value+=value
                self.game.screens.raise_jackpot(2,value)
                return procgame.game.SwitchStop
            
            
        def sw_captiveBallFront_active(self, sw):
            if self.multiball_running:
                value = 5000000
                self.jackpot_value+=value
                self.game.screens.raise_jackpot(2,value)
                return procgame.game.SwitchStop
            
            
        def sw_mapEject_active(self, sw):
            if self.multiball_running:
                value = 10000000
                self.jackpot_value+=value
                self.game.screens.raise_jackpot(2,value)
        
        
        def sw_arkHit_active(self, sw):  
            if self.multiball_running and self.jackpot_status!='lit':
                self.jackpot('lit')
                self.game.score(500000)
                return procgame.game.SwitchStop


        def sw_rightRampMade_active(self, sw):
            if self.multiball_running and self.jackpot_status=='lit' and self.game.switches.rightRampMade.time_since_change()>1:
                self.jackpot('made')
                return procgame.game.SwitchStop
       

        def sw_shooterLane_active_for_500ms(self,sw):
            if self.multiball_started: #and not self.multiball_running:
                self.game.coils.ballLaunch.pulse()

