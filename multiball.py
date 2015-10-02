# Multiball Code
#
# This mode handles the ball lock count and the multiball features such as jackpots,how many balls are in play etc.
# All Idol functions are handles by the idol mode. The number of balls locked is not the same as the number of balls in the idol!

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import logging
import audits
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

class JackpotWorthLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="left", opaque=False):
		super(JackpotWorthLayer, self).__init__(x, y, font,justify)
		self.mode = mode

	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_jackpot_worth()

		return super(JackpotWorthLayer, self).next_frame()


class Multiball(game.Mode):

	def __init__(self, game, priority):
            super(Multiball, self).__init__(game, priority)
            self.log = logging.getLogger('ij.multiball')

            self.text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['9x7_bold'], "center", opaque=False)
            self.jackpot_value_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=True)
            self.score_layer = ModeScoreLayer(90, 1, self.game.fonts['9x7_bold'], self)
            self.jackpot_worth_layer = JackpotWorthLayer(62, 25, self.game.fonts['07x5'],self)

            self.lock_animation_1 = "dmd/xxx.dmd"
            self.lock_animation_2 = "dmd/xxx.dmd"
            self.lock_animation_3 = "dmd/xxx.dmd"

            self.game.sound.register_sound('electricity', sound_path+"electricity.aiff")
            
            self.game.sound.register_sound('lock', sound_path+"lock.aiff")
            self.game.sound.register_sound('jackpot_attempt', sound_path+"jackpot_attempt.aiff")

            self.game.sound.register_sound('you_cheat', speech_path+"you_cheat_drjones.aiff")
            self.game.sound.register_sound('hit_jackpot', speech_path+"hit_the_jackpot.aiff")
            self.game.sound.register_sound('prize_doubled', speech_path+"your_prize_is_doubled.aiff")
            self.game.sound.register_sound('prize_tripled', speech_path+"your_prize_is_tripled.aiff")
            self.game.sound.register_sound('jackpot1', speech_path+"jackpot.aiff")
            self.game.sound.register_sound('jackpot2', speech_path+"double_jackpot.aiff")
            self.game.sound.register_sound('jackpot3', speech_path+"triple_jackpot.aiff")
            self.game.sound.register_sound('super_jackpot', speech_path+"super_jackpot.aiff")
            self.game.sound.register_music('multiball_play', music_path+"multiball.aiff")
            
            self.jackpot_lamps = ['arkJackpot','stonesJackpot','grailJackpot','skullJackpot']

            self.balls_needed = 3 #change to setting
            self.balls_in_play = 1

            self.lock_ball_score = 500000
            self.lock_enabled_score = 100000
            self.jackpot_base = 25000000
            self.jackpot_boost = 20000000
            self.super_jackpot_value = 100000000

            self.lock_lit = False
            self.mode_running = False
            self.balls_locked = 0
            self.multiball_started = False
            self.multiball_running = False

            self.cheat_value_start = 5000000
            self.cheat_value_boost = 1000000
            
            self.hits_needed = int(self.game.user_settings['Gameplay (Feature)']['Temple Hits For Lock'])
        


        def reset(self):
            self.update_lamps()


        def mode_started(self):
            #set player stats for mode
            self.jackpot_value = self.jackpot_base
            self.jackpot_x = 1
            self.jackpot_status = 'notlit'
            self.jackpot_collected = self.game.get_player_stats('jackpots_collected')
            self.super_jackpot_enabled = False
            self.next_ball_ready = False
            self.cheat_count = self.game.get_player_stats('cheat_count')
            self.hits = self.game.get_player_stats('lock_progress_hits')
            self.lock_lit = self.game.get_player_stats('lock_lit')
            self.mode_running = self.game.get_player_stats('mode_running')
            self.balls_locked = self.game.get_player_stats('balls_locked')
            self.multiball_running = self.game.get_player_stats('multiball_running')
            self.multiball_started = self.game.get_player_stats('multiball_started')
            
            
            #self.log.info('multiball started flag:%s',self.multiball_started)
            #self.log.info('multiball running flag:%s',self.multiball_running)
            self.log.info('balls locked:%s',self.balls_locked)
            self.log.info('lock lit:%s',self.lock_lit)
            
            #temple logic for main locks
            if self.lock_lit:
                self.game.temple.open()
            else:
                self.game.temple.close()
            
            self.reset()

        def mode_stopped(self):
            self.jackpot('cancelled')
            self.game.set_player_stats('jackpots_collected',self.jackpot_collected)
            self.game.set_player_stats('cheat_count',self.cheat_count)
            self.game.set_player_stats('lock_progress_hits',self.hits)
        
        
        def mode_tick(self):
            if self.multiball_started:
                self.balls_in_play = self.game.trough.num_balls_in_play

                #debug
                #self.balls_in_play=3
                #-------------------------------------------
                #debug_ball_data = str(self.balls_in_play)+":"+str(self.game.trough.num_balls())+":"+str(self.game.trough.num_balls_locked)+":"+str(self.game.trough.num_balls_to_launch)+":"+str(self.multiball_running)
                #self.game.set_status(debug_ball_data)
                #-------------------------------------------

                if self.balls_in_play==self.balls_needed and self.multiball_running==False:
                    #start tracking
                    self.multiball_running = True;
                    self.game.set_player_stats('multiball_running',self.multiball_running)
            
                if self.multiball_running:
                    self.multiball_tracking()


        def lock_ball(self):

            #up the balls locked count
            self.balls_locked +=1
            self.lock_in_progress = True

            #self.game.trough.num_balls_locked = self.balls_locked #update trough mode regarding locked balls
            #self.game.idol.balls_in_idol = self.balls_locked #update idol mode regarding locked balls
            self.game.set_player_stats('balls_locked',self.balls_locked)
            self.game.set_player_stats('lock_in_progress',self.lock_in_progress)

            #debug
            #self.game.set_status("Lock "+str(self.balls_locked))

            #update idol state
            #self.game.idol.lock()
            

            #animations
            anim = dmd.Animation().load(game_path+"dmd/lock_"+str(self.balls_locked)+".dmd")
            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=6)
            self.animation_layer.add_frame_listener(-1,self.clear)
            self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])

            #sound
            self.game.sound.play('lock')

            #lamp show
            self.game.lampctrl.play_show('ball_lock', repeat=False,callback=self.game.update_lamps)

            #score
            self.game.score(self.lock_ball_score)
                
            #reset lock logic after delay
            self.delay(name='reset_lock_delay', event_type=None, delay=2, handler=self.reset_lock)

            if self.balls_locked==self.balls_needed:
                #set flag
                self.multiball_started = True
                self.game.set_player_stats('multiball_started', self.multiball_started)
                #queue start method
                self.animation_layer.add_frame_listener(-15, self.multiball_start)
            #else:
                #self.animation_layer.add_frame_listener(-20,self.launch_next_ball)


#        def launch_next_ball(self):
#            self.game.trough.launch_balls(1,callback=self.launch_callback,stealth=False) #stealth false, bip +1
#            self.next_ball_ready = True
#            self.game.ball_save.start(time=5)
#                
#                
        def launch_callback(self):
            pass

        
        def reset_lock(self):
            self.game.temple.close()
            
            self.lock_lit = False
            self.lock_in_progress = False
            self.game.set_player_stats('lock_lit',self.lock_lit)
            self.game.set_player_stats('lock_in_progress',self.lock_in_progress)
            
            self.hits_needed = int(self.game.user_settings['Gameplay (Feature)']['Temple Hits For Lock'])
            self.hits = 0
            
            self.update_lamps()
            
            
        def ark_hit(self):
            self.game.score(50000)
            self.game.sound.play('electricity')
            self.game.effects.drive_flasher('flasherArkFront','chaos',time=0.5)
            self.cancel_delayed('queue_ark_power')
            self.delay(name='queue_ark_power',delay=0.1,handler=self.ark_power)
            
        def ark_power(self):
             self.game.coils.arkMagnet.patter(original_on_time=25, on_time=10, off_time=60)
             self.delay(name='ark_magnet_disable',delay=0.6,handler=self.game.coils.arkMagnet.disable)
        

        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True),color=dmd.YELLOW)

        def update_jackpot_worth(self):
            self.jackpot_worth_layer.set_text(locale.format("%d", self.jackpot_value, True)+" X"+str(self.jackpot_x),color=dmd.ORANGE)

        def multiball_start(self):

#            #check is any additional ball launches are needed - multi-player game etc
#            if self.game.idol.balls_in_idol<self.balls_needed:
#                additional_balls = self.balls_needed-self.game.idol.balls_in_idol
#                self.log.info("Additional Ball to Launch:%s",additional_balls)
#                #self.game.set_status("ADDITIONAL BALLS LAUNCH:"+str(additional_balls))
#                self.game.trough.launch_balls(additional_balls,callback=self.launch_callback,stealth=False)

            #animations
            #self.game.set_status("MULTIBALL!") #debug
            anim = dmd.Animation().load(game_path+"dmd/multiball_start.dmd")
            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=6)
            #self.animation_layer.add_frame_listener(-1,self.game.idol.empty)
            self.animation_layer.add_frame_listener(-1,self.multiball_launch)
            #queue the jackpot tracking
            self.animation_layer.add_frame_listener(-1,lambda:self.jackpot('unlit'))
            self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])

            self.game.lampctrl.play_show('ball_lock', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
            self.game.score(self.lock_ball_score)

            #start multiball music
            self.game.sound.play_music('multiball_play', loops=-1)

            self.balls_locked=0  
            self.game.set_player_stats('balls_locked',self.balls_locked)
            
            #turn on ball save
            self.game.ball_save.start(num_balls_to_save=3,allow_multiple_saves=True,time=10)
            
            #restart the totem mode if quick multiball is not running and stacking therefore isnt happening
            if not self.game.get_player_stats('quick_multiball_running'):
                self.game.base_game_mode.totem.restart()
            
            
        def multiball_launch(self):
             #launch balls - locks are virtual on stern indy
            additional_balls = self.balls_needed-1
            self.game.trough.launch_balls(additional_balls,callback=self.launch_callback,stealth=False)
            
            
        def multiball_tracking(self):
            #end check
            if self.balls_in_play==1:
                #end tracking
                self.multiball_running=False
                self.multiball_started = False
                self.game.set_player_stats('multiball_running',self.multiball_running) 
                self.game.set_player_stats('multiball_started',self.multiball_started)

                #update poa player stats - moved to jackpot cancelled
                #self.game.set_player_stats("poa_queued",False)
                
                self.game.sound.stop_music()
                self.game.sound.play_music('general_play', loops=-1)

                #light jackpot if not collected during multiball otherwise cancel
                if self.jackpot_collected==0:
                    self.jackpot('lit')
                    self.log.info('Jackpot lit after multiball end, not collected')
                    self.delay(name='jackpot_timeout', event_type=None, delay=10, handler=self.jackpot, param='cancelled')
                else:
                    self.jackpot('cancelled')
                    #clear the display
                    self.clear()
                
                #restart the totem mode
                self.game.base_game_mode.totem.restart()
                    
            elif self.balls_in_play==0: #what to do if last 2 or more balls drain together
                #end tracking
                self.multiball_running=False
                self.multiball_started = False
                self.game.set_player_stats('multiball_running',self.multiball_running) 
                self.game.set_player_stats('multiball_started',self.multiball_started) 
                #update poa player stats
                #self.game.set_player_stats("poa_queued",False)
                #cancel jackpot
                self.jackpot('cancelled')
                #clear the display
                self.clear()
                

        def multiball_display(self,num):
            
            anim1 = dmd.Animation().load(game_path+"dmd/ark.dmd")
            anim2 = dmd.Animation().load(game_path+"dmd/sankara_stone.dmd")
            anim3 = dmd.Animation().load(game_path+"dmd/grail.dmd")
            anim4 = dmd.Animation().load(game_path+"dmd/skull.dmd")
            animation_layer1 = None
            animation_layer2 = None
            animation_layer3 = None
            animation_layer4 = None
            if num==0:
                animation_layer1 = dmd.AnimatedLayer(frames=anim1.frames,repeat=True,frame_time=6)
                animation_layer2 = dmd.FrameLayer(frame=anim2.frames[0])
                animation_layer3 = dmd.FrameLayer(frame=anim3.frames[0])
                animation_layer4 = dmd.FrameLayer(frame=anim4.frames[0])
            elif num==1:
                animation_layer1 = dmd.FrameLayer(frame=anim1.frames[0])
                animation_layer2 = dmd.AnimatedLayer(frames=anim2.frames,repeat=True,frame_time=6)
                animation_layer3 = dmd.FrameLayer(frame=anim3.frames[0])
                animation_layer4 = dmd.FrameLayer(frame=anim4.frames[0])
            elif num==2:
                animation_layer1 = dmd.FrameLayer(frame=anim1.frames[0])
                animation_layer2 = dmd.FrameLayer(frame=anim2.frames[0])
                animation_layer3 = dmd.AnimatedLayer(frames=anim3.frames,repeat=True,frame_time=6)
                animation_layer4 = dmd.FrameLayer(frame=anim4.frames[0])
            elif num==3:
                animation_layer1 = dmd.FrameLayer(frame=anim1.frames[0])
                animation_layer2 = dmd.FrameLayer(frame=anim2.frames[0])
                animation_layer3 = dmd.FrameLayer(frame=anim3.frames[0])
                animation_layer4 = dmd.AnimatedLayer(frames=anim4.frames,repeat=True,frame_time=6)

            animation_layer1.target_x=15
            animation_layer1.target_y=21
            animation_layer2.target_x=45
            animation_layer2.target_y=21
            animation_layer3.target_x=70
            animation_layer3.target_y=21
            animation_layer4.target_x=95
            animation_layer4.target_y=20
            
            self.score_layer.x = 128/2
            self.score_layer.y=-1
            self.score_layer.justify='center'
            
            info_layer1 = dmd.TextLayer(128/2, 8, self.game.fonts['07x5'], "center", opaque=False)
            info_layer2 = dmd.TextLayer(128/2, 14, self.game.fonts['07x5'], "center", opaque=False)

            info_layer1.set_text("SHOOT LEFT RAMP OR CENTER",color=dmd.CYAN)
            info_layer2.set_text("HOLE TO LIGHT JACKPOT",color=dmd.CYAN)

            self.layer = dmd.GroupedLayer(128, 32, [self.score_layer,info_layer1,info_layer2,animation_layer1,animation_layer2,animation_layer3,animation_layer4])

        def jackpot_lit_display(self,num):
            file=None
            title_layer = dmd.TextLayer(78, 1, self.game.fonts['num_09Bx7'], "center", opaque=False)
            if num==0:
                file = "dmd/ark_jackpot_lit.dmd"
                title_layer.set_text("rescue the ark".upper(),color=dmd.BROWN)
            elif num==1:
                file = "dmd/sankara_jackpot_lit.dmd"
                title_layer.set_text("return stones".upper(),color=dmd.BROWN)
            elif num==2:
                file = "dmd/grail_jackpot_lit.dmd"
                title_layer.set_text("find the grail".upper(),color=dmd.BROWN)
            elif num==3:
                file = "dmd/skull_jackpot_lit.dmd"
                title_layer.set_text("awaken hive".upper(),color=dmd.BROWN)
            anim = dmd.Animation().load(game_path+file)
            animation_layer = dmd.AnimatedLayer(frames=anim.frames,repeat=True,frame_time=6)

            self.score_layer.x = 80
            self.score_layer.y = 13

            self.layer = dmd.GroupedLayer(128, 32, [animation_layer,self.jackpot_worth_layer,self.score_layer,title_layer])

        
        def jackpot_collected_display(self,num):
            anim = dmd.Animation().load(game_path+"dmd/jackpot.dmd")
            animation_layer = dmd.AnimatedLayer(frames=anim.frames,repeat=True,frame_time=6)
            self.layer = animation_layer
            self.delay(name='jackpot_explode_delay',delay=4,handler=self.jackpot_explode_display)

        def jackpot_explode_display(self):
            anim = dmd.Animation().load(game_path+"dmd/jackpot_explode.dmd")
            animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=6)
            animation_layer.add_frame_listener(-1,self.jackpot_value_display)
            self.layer = animation_layer

        def jackpot_value_display(self):
            time=3
            self.jackpot_value_layer.set_text(locale.format("%d",self.jackpot_value,True),blink_frames=2)
            self.layer = self.jackpot_value_layer
            self.delay(name='reset_jackpot',delay=time,handler=lambda:self.jackpot('unlit'))

        def jackpot(self,status=None):

                self.jackpot_status = status
            #if self.multiball_running:
                if status=='lit':
                    self.game.coils.flasherArkFront.disable()
                    self.game.coils.flasherSkull.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
#                    self.game.coils.divertorMain.pulse(50)
#                    self.game.coils.divertorHold.pulse(0)
#                    self.game.coils.topLockupMain.pulse(50)
#                    self.game.coils.topLockupHold.pulse(0)

                    #update display
                    self.jackpot_lit_display(self.jackpot_collected)

                    #speech
                    self.game.sound.play('hit_jackpot')

                elif status=='unlit':
                    self.game.coils.flasherArkFront.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
#                    self.game.coils.divertorHold.disable()
#                    self.game.coils.topLockupHold.disable()

                    #update display
                    if self.jackpot_collected<4:
                        self.multiball_display(self.jackpot_collected)
                    else:
                        self.super_jackpot_lit()

                elif status=='made':
                    self.game.coils.flasherSkull.disable()
                    self.game.lampctrl.play_show('jackpot', repeat=False,callback=self.game.update_lamps)#self.restore_lamps

       #            anim = dmd.Animation().load(game_path+"dmd/lock_animation_"+self.balls_locked+".dmd")
       #            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=2)
#                   self.animation_layer.add_frame_listener(-1,self.clear)
#                   self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])

                    #self.jackpot_x = self.game.idol.balls_in_idol+1

                    self.game.score(self.jackpot_value*self.jackpot_x)
                    self.jackpot_collected+=1
                    self.game.effects.drive_lamp(self.jackpot_lamps[self.jackpot_collected-1],'smarton')
                    if self.jackpot_collected>4:
                        self.super_jackpot_collected()
                    else:
                        #self.delay(name='reset_jackpot', event_type=None, delay=1, handler=self.jackpot, param='unlit')
                        #update display
                        self.jackpot_collected_display(self.jackpot_collected)

                        #speech
                        self.game.sound.play('jackpot'+str(self.jackpot_x))

                    
                elif status=='cancelled':
                    self.game.coils.flasherArkFront.disable()
                    self.game.coils.flasherSkull.disable()
#                    self.game.coils.divertorHold.disable()
#                    self.game.coils.topLockupHold.disable()
                    
                    #update poa player stats
                    self.game.set_player_stats("poa_queued",False)
                    
                    self.clear()

        def super_jackpot_lit(self):
            self.super_jackpot_lit = True
            self.game.coils.flasherSankara.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.game.coils.flasherTemple.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.super_jackpot_enabled = True
            self.game.temple.open()


        def super_jackpot_collected(self):
            #run animation
            anim = dmd.Animation().load(game_path+"dmd/super_jackpot.dmd")
            animation_layer = dmd.AnimatedLayer(frames=anim.frames,repeat=True,frame_time=6)
            self.layer = animation_layer
            #lamp effects
            self.game.lampctrl.play_show('jackpot', repeat=False,callback=self.game.update_lamps)
            #speech
            self.game.sound.play('super_jackpot')
            
            #award score
            self.game.score(self.jackpot_value*10)
            
            self.delay(name='display_clear_delay',delay=4,handler=self.jackpot_reset)
           

        def jackpot_reset(self):
            #reset jackpot count to start again
            self.jackpot_collected=0
            self.jackpot('unlit')
            self.super_jackpot_lit = False

        def cheat_display(self):
            #calc value
            cheat_value = (self.cheat_value_boost*self.cheat_count)+self.cheat_value_start

            #create display layers
            anim = dmd.Animation().load(game_path+"dmd/cheat_drjones.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            text_layer = dmd.TextLayer(88, 21, self.game.fonts['num_09Bx7'], "center", opaque=False)
            text_layer.set_text(locale.format("%d",cheat_value,True),blink_frames=10,color=dmd.GREEN)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer])

            #play speech
            length = self.game.sound.play('you_cheat')
            
            #update counter
            self.cheat_count+=1
            
            #continue ball lock after cheat anim and speech
            self.lock_enabled() #update the lock flags anyway
            self.delay(delay=length+0.25,handler=self.lock_ball)
            
            
        def lock_progress_display(self):
            value = self.hits_needed-self.hits
            timer =2
            #create display layer
            anim = dmd.Animation().load(game_path+"dmd/shorty_plain.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            text_layer1 = dmd.TextLayer(88, 0, self.game.fonts['9x7_bold'], "center", opaque=False)
            text_layer2 = dmd.TextLayer(88, 13, self.game.fonts['07x5'], "center", opaque=False)
            text_layer3 = dmd.TextLayer(88, 20, self.game.fonts['07x5'], "center", opaque=False)
            text_layer1.set_text(str(value)+' MORE',blink_frames=10,seconds=timer,color=dmd.CYAN)
            text_layer2.set_text('HITS TO',seconds=timer,color=dmd.GREEN)
            text_layer3.set_text('LITE LOCK',seconds=timer,color=dmd.GREEN)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer1,text_layer2,text_layer3])
            
            self.delayed_clear(timer)


        def lock_lit_display(self):
            timer=2
            #create display layer
            anim = dmd.Animation().load(game_path+"dmd/shorty_plain.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            text_layer1 = dmd.TextLayer(88, 5, self.game.fonts['9x7_bold'], "center", opaque=False)
            text_layer2 = dmd.TextLayer(88, 18, self.game.fonts['9x7_bold'], "center", opaque=False)
            text_layer1.set_text('LOCK',seconds=timer,color=dmd.GREEN)
            text_layer2.set_text('IS LIT',blink_frames=10,seconds=timer,color=dmd.GREEN)
            
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer1,text_layer2])
            
            self.delayed_clear(timer)


        def lock_enabled(self):
            self.lock_lit = True;
            #self.game.idol.lock_lit=  self.lock_lit
            self.game.set_player_stats('lock_lit',self.lock_lit)
            
            #update display
            self.lock_lit_display()
            
            #open temple
            self.game.temple.open()

            self.game.score(self.lock_enabled_score)
            self.update_lamps()
          
          
        def lock_progress(self):
            if not self.lock_lit:
                self.hits +=1

                if self.hits==self.hits_needed:
                    self.lock_lit = True     
                    audits.record_value(self.game,'lockLit')
                    self.lock_enabled()
                else:
                    self.lock_progress_display()

            else:
                pass
        
#        def reset_drops(self):
#            if self.game.switches.dropTargetLeft.is_active() or self.game.switches.dropTargetMiddle.is_active() or  self.game.switches.dropTargetRight.is_active():
#                self.game.coils.centerDropBank.pulse(100)


        def update_lamps(self):
            if self.lock_lit:
                self.game.effects.drive_lamp('templeArrow','medium')
            else:
                self.game.effects.drive_lamp('templeArrow','off')
                
            for i in range(self.jackpot_collected):
                self.game.effects.drive_lamp(self.jackpot_lamps[i],'on')


        def delayed_clear(self,timer=2):
            self.delay(name='clear_delay', event_type=None, delay=timer, handler=self.clear)
            
        def clear(self):
            self.layer = None



        #switch handlers
        #--------------------
#        def sw_dropTargetLeft_active(self, sw):
#            self.lock_enabled()
#
#        def sw_dropTargetMiddle_active(self, sw):
#            self.lock_enabled()
#
#        def sw_dropTargetRight_active(self, sw):
#            self.lock_enabled()

        def sw_templeStandup_active(self, sw):
            self.lock_progress()

        def sw_subway_active(self, sw):
            if not self.multiball_running and not self.game.get_player_stats('multiball_mode_started'):
                if self.lock_lit:
                    self.lock_ball()
                else:
                    self.cheat_display() #play the cheat anim :)
            elif self.multiball_running:
                #self.game.idol.hold()
                if not self.super_jackpot_lit:
                    self.jackpot_x+=1
                    if self.jackpot_x==2:
                        self.game.sound.play('prize_doubled')
                    elif self.jackpot_x==3:
                        self.game.sound.play('prize_tripled')
                else:
                    self.super_jackpot_collected()
            #else:
                #self.game.idol.lock_release()


#        def sw_exitIdol_active(self,sw):
#            if self.multiball_running and self.jackpot_x>1:
#                 self.jackpot_x-=1
        
        def sw_captiveBallRear_active(self, sw): #instead of left ramp
            if self.multiball_running:
                value = 2000000
                self.jackpot_value+=value
                self.game.screens.raise_jackpot(2,value)
                return procgame.game.SwitchStop

        def sw_rightRampMade_active(self, sw):
            if self.multiball_running and self.game.switches.rightRampMade.time_since_change()>1:
                self.jackpot('made')
                return procgame.game.SwitchStop

#        def sw_leftRampEnter_active(self, sw):
#            pass

        def sw_rightRampEnter_active(self, sw):
            if self.jackpot_status=='lit' and self.game.switches.rightRampEnter.time_since_change()>1:
                self.game.sound.play('jackpot_attempt')


        def sw_grailEject_active(self, sw):
            if self.multiball_running:
                value = 2000000
                self.jackpot_value+=value
                self.game.screens.raise_jackpot(2,value)


        def sw_captiveBallFront_active(self, sw):
            if self.multiball_running:
                value = 5000000
                self.jackpot_value+=value
                self.game.screens.raise_jackpot(2,value)

            #return procgame.game.SwitchStop
            
        def sw_mapEject_active(self, sw):
            if self.multiball_running:
                value = 10000000
                self.jackpot_value+=value
                self.game.screens.raise_jackpot(2,value)

            #return procgame.game.SwitchStop

        def sw_arkHit_active(self, sw):  
            if self.multiball_running and self.jackpot_status!='lit':
                self.jackpot('lit')
                self.game.score(500000)
                return procgame.game.SwitchStop
            else:    
                self.ark_hit()
            

        #start ball save for next ball after lock
        def sw_shooterLane_open_for_1s(self,sw):
            if self.next_ball_ready:

            	ball_save_time = 5
                self.game.ball_save.start(num_balls_to_save=1, time=ball_save_time, now=True, allow_multiple_saves=False)

        #check for shooter lane launches in multiball
        def sw_shooterLane_active_for_500ms(self,sw):
            if self.multiball_started:
                self.game.coils.ballLaunch.pulse()
