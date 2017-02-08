# Jones Vs Aliens Game Mode
# Copyright (C) 2015 myPinballs, Orange Cloud Software Ltd
#
# Thanks to Eric Priepke for asset assistance


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
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Ringmaster(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Ringmaster, self).__init__(game, priority)
            
            #logging
            self.log = logging.getLogger('ij.ringmaster')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #load settings
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Ringmaster Timer'])
            self.log.info("Ringmaster Timer is:"+str(self.timer))
            self.extras = self.game.user_settings['Gameplay (Feature)']['Ringmaster Extras']
            
            #screen setup
            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            #self.award_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=False)
            #self.award_layer.composite_op ="blacksrc"
            
            #sound setup
            self.game.sound.register_music('ringmaster_play', music_path+"ringmaster.aiff")
            self.game.sound.register_music('ringmaster_gears', sound_path+"cv112_ratchet.wav")
            self.game.sound.register_sound('ringmaster_hit', sound_path+"cv105_ringmaster-hit-1.wav")
            self.game.sound.register_sound('ringmaster_hit', sound_path+"cv106_ringmaster-hit-2.wav")
            self.game.sound.register_sound('ringmaster_gears', sound_path+"cv112_ratchet.wav")
            self.game.sound.register_sound('ringmaster_elephant', sound_path+"cv170-elephant.wav")
            self.game.sound.register_sound('ringmaster_acrobats', sound_path+"cv179_acrobats.wav")
            self.game.sound.register_sound('ringmaster_car_crash', sound_path+"cv218_clown_crash.wav")
            self.game.sound.register_sound('ringmaster_squeaky_wheel', sound_path+"cv523_squeaky-wheel.wav")
            self.game.sound.register_sound('ringmaster_double_boom', sound_path+"cv162_double-boom.wav")
            self.game.sound.register_sound('ringmaster_fireworks', sound_path+"cv575_firework-launch.wav")
            self.game.sound.register_sound('ringmaster_fireworks', sound_path+"cv575_firework-bnag.wav")
            self.game.sound.register_sound('ringmaster_inlane', sound_path+"cv998_monkey.wav")
            self.game.sound.register_sound('ringmaster_outlane', sound_path+"cv218_clown_crash.wav")
            self.game.sound.register_sound('ringmaster_loop', sound_path+"afm246_woosh.wav")     
            self.game.sound.register_sound('ringmaster_explosion', sound_path+"afm208_nice_explosion.aiff")  
            self.game.sound.register_sound('ringmaster_explosion', sound_path+"cv999_large_explosion.wav")
            self.game.sound.register_sound('jva_jones_target', sound_path+"cv305_trumpet_hit0.aiff")
            self.game.sound.register_sound('jva_jones_target', sound_path+"cv306_trumpet_hit1.aiff")
            self.game.sound.register_sound('jva_jones_target', sound_path+"cv307_trumpet_hit2.aiff")
            self.game.sound.register_sound('jva_jones_target', sound_path+"cv308_trumpet_hit3.aiff")
            self.game.sound.register_sound('jva_jones_target', sound_path+"cv163_horn_car.aiff")
            self.game.sound.register_sound('jva_jones_target', sound_path+"cv141_spring.aiff")
            
            self.game.sound.register_sound('ringmaster_defeated_jingle', sound_path+"cv807_jackpot_fanfare.aiff")          
            
            self.game.sound.register_sound('ringmaster_speech0', speech_path+"cv1201_intro.wav")
            self.game.sound.register_sound('ringmaster_speech0', speech_path+"cv1207_your_a_disaster.wav")
            
            self.game.sound.register_sound('ringmaster_speech1', speech_path+"cv1220_intro-you-must-challenge-me.wav")
            self.game.sound.register_sound('ringmaster_speech1', speech_path+"cv1212_intro-cranky.wav")
            self.game.sound.register_sound('ringmaster_speech1', speech_path+"cv1211_do_you_wish_to_challenge_me.aiff")
            self.game.sound.register_sound('ringmaster_speech1', speech_path+"cv1215_do_your_worst.aiff")
            self.game.sound.register_sound('ringmaster_speech1', speech_path+"cv1277_challenge_you_to_a_duel.aiff")
            
            self.game.sound.register_sound('ringmaster_speech11', speech_path+"cv1295_ringmaster_battle.aiff")
            self.game.sound.register_sound('ringmaster_speech11', speech_path+"cv1296_to_the_ringmaster_battle.aiff")
           
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1244_hit-the-best-youve-got.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1247_hit-ow-ooh.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1209_hit-how-dare-you.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1247_hit-ow-ooh.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1253_hit-my-contact.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"ccv1251_hit-watch-it.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1266_hit-stop-that.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1271_hit-ooh-that-hurts.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1223_hahaha.aiff")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1224_muhahaha.aiff")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1210_taunt-mother.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1215_taunt-do-your-worst.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1216_taunt-shoes.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1217_taunt-mangy.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1219_taunt-weep.wav")
            self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv1208_go_go_but_dont_be_slow.aiff")
            if self.extras.startswith("Y"):
                self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv_hare_watchthishocuspocus.aiff")
                self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv_hare_watchthiswizardry.aiff")
                self.game.sound.register_sound('ringmaster_speech2', speech_path+"cv_hare_whooshcough.aiff")
                
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm932_martian_growl.aiff")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm1110_i_hate_humans.aiff")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm896_cant_we_be_friends.aiff")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm_groan1.wav")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm_groan2.wav")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm_groan3.wav")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm_groan4.wav")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm_groan5.wav")
#            self.game.sound.register_sound('ringmaster_speech3', speech_path+"afm_groan6.wav")
            
            self.game.sound.register_sound('ringmaster_speech4', sound_path+"cv1263_oooh-nooo.wav")
            self.game.sound.register_sound('ringmaster_speech4', sound_path+"cv1214_au_revoir.aiff")
            

            #var setup
            self.mode_started_value = int(self.game.user_settings['Gameplay (Feature)']['Mode Start Value (Mil)'])*1000000
            #self.forcefield_hits = 3
            self.ringmaster_hits = 5
            self.score_value_boost = 5000000
            self.score_value_start = 5000000
            self.score_value_extra = 2000000
            self.forcefield_hit_value = 100000
            self.ship_hit_value = 250000
            self.defeated_timer_boost = 10
            
            #lamps setup
            self.lamps = ['raidersArrow']
            
            self.jones_lamps = ['jonesJ','jonesO','jonesN','jonesE','jonesS']
            self.jones_target_score = 10000
            self.jones_completed_score = 500000
            
            self.smart_bomb_lamp_button = 'tournamentStartButton'
            

        def reset(self):
            self.count = 0
            self.ringmaster_defeated_count = 0
            self.running_total = 0
            self.reset_jones()
            
            
        def reset_jones(self):
            self.jones_flags = [False,False,False,False,False]
            self.update_jones_lamps()
            

        def set_jones_lamps(self,id):
            self.game.effects.drive_lamp(self.jones_lamps[id],'smarton')
            for i in range(len(self.jones_lamps)):
                if not self.jones_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'medium')
        
        def update_jones_lamps(self):
            for i in range(len(self.jones_lamps)):
                if self.jones_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'on')
                else:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'medium')

        def reset_jones_lamps(self):
            for i in range(len(self.jones_lamps)):
                self.game.effects.drive_lamp(self.jones_lamps[i],'off')
        
        def completed_jones_lamps(self):
            for i in range(len(self.jones_lamps)):
                self.game.effects.drive_lamp(self.jones_lamps[i],'superfast')
                
                
        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')
            
            self.reset_jones_lamps()


        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'fast')
            
            self.update_jones_lamps()
                
                
#        def load_forcefield_hit_anim(self):
#            self.bgnd_anim = "dmd/jva_ship_forcefield.dmd"
#            anim = dmd.Animation().load(game_path+self.bgnd_anim)
#            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
#            
#            self.bgnd_layer.add_frame_listener(-1, self.load_bgnd_anim)
#            
#            self.layer = self.bgnd_layer 
            
            
#        def load_ship_anim(self):
#            self.bgnd_anim = "dmd/jva_large_ship.dmd"
#            anim = dmd.Animation().load(game_path+self.bgnd_anim)
#            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=True,frame_time=6)
#            self.layer = self.bgnd_layer
            
            
        def load_ringmaster_hit_anim(self):
            self.cancel_delayed('change_bgnd_anim')
            
            self.bgnd_anim = "dmd/cv-intro-part2.dmd"
            explosions = ["dmd/cv-burst1.dmd","dmd/cv-burst2.dmd","dmd/cv-burst3.dmd"]
            self.explosion_anim = explosions[random.randint(0,len(explosions)-1)]
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=True,frame_time=6)
            anim = dmd.Animation().load(game_path+self.explosion_anim)
            self.explosion_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.explosion_layer.target_x=random.randint(-80,40)
            #self.explosion_layer.target_y=random.randint(5,20)
            self.explosion_layer.composite_op ="blacksrc"
            self.explosion_layer.add_frame_listener(-1, self.load_bgnd_anim)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.explosion_layer])
        
        
        def load_ringmaster_defeated_anim(self):
            self.cancel_delayed('change_bgnd_anim')
            
            self.bgnd_anim = "dmd/cv-finale-color.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.bgnd_layer.add_frame_listener(-3, self.load_explosion_anim)
            
            #add sounds choriography
            self.bgnd_layer.add_frame_listener(1,lambda:self.game.sound.play('ringmaster_defeated_jingle'))
            self.bgnd_layer.add_frame_listener(8,lambda:self.game.sound.play('ringmaster_double_boom'))
            self.bgnd_layer.add_frame_listener(13,lambda:self.game.sound.play('ringmaster_elephant'))
            self.bgnd_layer.add_frame_listener(15,lambda:self.game.sound.play('self.game.assets.quote_cvEnd'))
            self.bgnd_layer.add_frame_listener(29,lambda:self.game.sound.play('ringmaster_acrobats'))
            self.bgnd_layer.add_frame_listener(52,lambda:self.game.sound.play('ringmaster_squeaky_wheel'))
            self.bgnd_layer.add_frame_listener(59,lambda:self.game.sound.play('ringmaster_car_crash'))
            self.bgnd_layer.add_frame_listener(63,lambda:self.game.sound.play('ringmaster_gears'))
            
            self.layer = self.bgnd_layer 
            
        
        def load_explosion_anim(self):
            self.game.sound.play("ringmaster_explosion")
            
            self.bgnd_anim = "dmd/cv-explosion.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.bgnd_layer.add_frame_listener(-1, self.load_completed_anim)
            self.layer = self.bgnd_layer 
    
            
        def load_completed_anim(self):     
            self.bgnd_anim = "dmd/cv-completed.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            award_layer = dmd.TextLayer(128/2, 19, self.game.fonts['10x7_bold'], "center", opaque=False)
            award_layer.composite_op ="blacksrc"
            award_layer.set_text(locale.format("%d",self.score_value_start+self.score_value_boost,True),blink_frames=10,seconds=3,color=dmd.MAGENTA)
            self.bgnd_layer.add_frame_listener(6,lambda:self.game.sound.play('ringmaster_fireworks'))
            self.bgnd_layer.add_frame_listener(10,lambda:self.game.sound.play('ringmaster_fireworks'))
            self.bgnd_layer.add_frame_listener(16,lambda:self.game.sound.play('ringmaster_fireworks'))
            self.bgnd_layer.add_frame_listener(24,lambda:self.game.sound.play('ringmaster_fireworks'))
            self.bgnd_layer.add_frame_listener(-2, self.game.base_game_mode.mode_select.mode_unpaused)
            self.bgnd_layer.add_frame_listener(-1, self.load_bgnd_anim)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,award_layer])
          
            
        def load_intro1_anim(self):
            self.bgnd_anim = "dmd/cv-intro-part1.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.bgnd_layer.add_frame_listener(-1, self.load_intro2_anim)
            self.layer = self.bgnd_layer 
            
            
        def load_intro2_anim(self):
            self.game.sound.play_music('ringmaster_play', loops=-1)
             
            self.bgnd_anim = "dmd/cv-intro-part2.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.bgnd_layer.add_frame_listener(-1, self.load_bgnd_anim)
            self.layer = self.bgnd_layer 
        

        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/cv-hypno.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            
            #set destroyed text
            self.destroyed_layer.set_text("RINGMASTERS DEFEATED: "+str(self.ringmaster_defeated_count), color=dmd.RED)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.destroyed_layer])
            
            timer=random.randint(5,15)
            self.cancel_delayed('change_bgnd_anim')
            self.delay(name='change_bgnd_anim', event_type=None, delay=timer, handler=self.load_battle_anim)
                     
            
        def load_battle_anim(self):
            self.voice_call(count=11)
            
            if self.extras.startswith("Y"):
                alt_text =["MAKING PINBALL IS HARD","NO-ONE WOULD HELP ME","YOU'RE CAUSING GREAT HARM","3 TYPES OF PROGRAMMERS","MAKE IT OUT OF FOAM CORE","WHERE'S MY F$%KING MONEY?","DRINK THE KOOL-AID"]
                chosen_text = alt_text[random.randint(0,len(alt_text)-1)]
                self.info_layer.set_text(chosen_text, blink_frames=10, color=dmd.CYAN)
            
            self.bgnd_anim = "dmd/cv-hypno.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
             
            self.logo_anim = "dmd/cv_battle_logo.dmd"
            logo_anim = dmd.Animation().load(game_path+self.logo_anim)
            self.logo_layer = dmd.AnimatedLayer(frames=logo_anim.frames,opaque=False,repeat=True,frame_time=6)
            self.logo_layer.composite_op ="blacksrc"
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.logo_layer])
            
            timer=3
            self.cancel_delayed('change_bgnd_anim')
            self.delay(name='change_bgnd_anim', event_type=None, delay=timer, handler=self.load_bgnd_anim)
            
            
        def load_loop_anim(self,timer=2):
            self.cancel_delayed('change_bgnd_anim')
            anim = dmd.Animation().load(game_path+"dmd/cv_tesla_electricity.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,hold=True,frame_time=6)
            name_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center")
            info_layer = dmd.TextLayer(128/2, 15, self.game.fonts['9x7_bold'], "center")
            
            def set_text(self):
                name_layer.set_text('Ringmaster Value'.upper(),color=dmd.BROWN)
                ship_value = self.score_value_start+self.score_value_boost
                info_layer.set_text(locale.format("%d",ship_value,True),color=dmd.GREEN)
            
            bgnd_layer.add_frame_listener(-1,lambda:set_text(self)) #set the text for the end of the animation

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,name_layer,info_layer,])
            
            #queue display reset to main bgnd
            self.delay(name='reset_display', event_type=None, delay=timer, handler=self.load_bgnd_anim)
            
            
            
        
        def load_forcefield_down_anim(self,timer=2):
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/jva_ships_border.dmd").frames[0])
            name_layer = dmd.TextLayer(128/2, 12, self.game.fonts['9x7_bold'], "center")
            name_layer.set_text('Forcefield Down'.upper(),color=dmd.CYAN)
            
            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,name_layer])

            self.delay(name='load_ship_anim', event_type=None, delay=timer, handler=self.load_ship_anim)


        def mode_started(self):
            self.reset()
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, 25, self.game.fonts['07x5'],self.timer,"right")
            self.destroyed_layer = dmd.TextLayer(128/2, 12, self.game.fonts['8x6'], "center", opaque=False)
            self.info_layer = dmd.TextLayer(128/2, 24, self.game.fonts['07x5'], "center", opaque=False)
           
            #load player stats
            self.ringmaster_defeated_count = self.game.get_player_stats('ringmasters_defeated')
            self.smart_bombs = self.game.get_player_stats('ringmaster_smart_bombs')
            
            #update path mode var
            self.game.set_player_stats("path_mode_started",True) #set as path mode to halt adventure starting if completed
            self.game.set_player_stats("ark_mode_started",True)

            #setup text
            self.info_layer.set_text("SHOOT ARK TO BATTLE", blink_frames=10, color=dmd.PURPLE)
            
            #load animation
            self.load_intro1_anim()
            
            #start mode music sounds & speech
            self.game.sound.play_music('ringmaster_gears',loops=-1)
            self.voice_call(count=0,delay=3)
            
            self.running_total=self.mode_started_value
            
            #update lamps
            self.update_lamps()
            
                 
        def voice_call(self,count,delay=None):
            if delay==None:
                wait = self.game.sound.play_voice("ringmaster_speech"+str(count))
                
                #additional speech calls
                if count==0:
                    self.voice_call(count=1,delay=wait+2)
                    #self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=1)
#                   self.delay(name='aux_mode_speech_delay', event_type=None, delay=6, handler=self.voice_call, param=12)
#               if count==2:
#                   self.delay(name='aux_mode_speech_delay', event_type=None, delay=1.2, handler=self.voice_call, param=13)
#                   self.delay(name='aux_mode_speech_delay', event_type=None, delay=2.5, handler=self.voice_call, param=14)
#               if count==3:
#                   self.delay(name='aux_mode_speech_delay', event_type=None, delay=1, handler=self.voice_call, param=15)
  
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)


        def mode_tick(self):
            pass

        def mode_stopped(self):
            #save player stats
            self.game.set_player_stats('ringmasters_defeated',self.ringmaster_defeated_count)
            self.game.set_player_stats('ringmaster_smart_bombs',self.smart_bombs)

            self.game.set_player_stats('ringmaster_score',self.running_total)
            self.game.set_player_stats('last_mode_score',self.running_total)
            
            #update poa player stats
            self.game.set_player_stats("path_mode_started",False)
            self.game.set_player_stats("poa_queued",False)
            self.game.set_player_stats("ark_mode_started",False)
            
            #safety magnet disable
            self.cancel_delayed('queue_ark_power')
            self.game.coils.arkMagnet.disable()

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            #self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            #self.game.sound.stop_music()
            #self.game.sound.play_music('general_play', loops=-1)
            
            #clear display
            self.clear()
            
            #update lamps
            self.reset_lamps()


        def mode_progression(self):
            self.count+=1
#            if self.count<=self.forcefield_hits:
#                self.forcefield_progress()
#            elif self.count<=self.forcefield_hits+self.ship_hits:
#                self.ship_progress()
#            else:
#                self.ship_destroyed()

            if self.count<=self.ringmaster_hits:
                self.ringmaster_progress()
            else:
                self.ringmaster_defeated()

            
#        def forcefield_progress(self):
#            #setup anim
#            if self.count<self.forcefield_hits:
#                self.load_forcefield_hit_anim()
#                self.voice_call(count=1,delay=1.5)
#            else:
#                self.load_forcefield_down_anim()
#                self.voice_call(count=2,delay=0.5)
#            
#            #play speech/sound
#            self.game.sound.play("jva_forcefield_hit")
#           
#            #effects
#            self.ark_hit()
#            
#            self.game.score(self.forcefield_hit_value)
            
        
        def ringmaster_progress(self):
            #setup anim
            self.load_ringmaster_hit_anim()
            
            #play speech/sound
            self.game.sound.play("ringmaster_hit")
            self.voice_call(count=2,delay=1.5)
            
            #effects
            self.ark_hit()
            self.gi_flutter()
            
            self.game.score(self.ship_hit_value)
        
       
        def ringmaster_defeated(self):
            #pause mode timer
            self.game.base_game_mode.mode_select.mode_paused(sw=None)
            #increase mode timer for completion
            #self.timer_layer.add_time(self.defeated_timer_boost) 
            
            #setup anim
            self.load_ringmaster_defeated_anim()
            
            #play speech/sound
            #self.game.sound.play("ringmaster_defeated_jingle")
            self.voice_call(count=4,delay=1)
            
            #effects
            self.ark_hit()
            self.game.lampctrl.play_show('success', repeat=False,callback=self.game.update_lamps)
            self.gi_flutter()
            
            self.ringmaster_defeated_count+=1
            
            self.running_total += self.score_value_start+self.score_value_boost
            self.game.score(self.score_value_start+self.score_value_boost)
            
            self.count=0 #reset count
            
            
        def ark_hit(self):
            self.game.effects.drive_flasher('flasherArkFront','chaos',time=0.5)
            self.cancel_delayed('queue_ark_power')
            self.delay(name='queue_ark_power',delay=0.1,handler=self.ark_power)
            
        def ark_power(self):
             self.game.coils.arkMagnet.patter(original_on_time=25, on_time=10, off_time=60)
             self.delay(name='ark_magnet_disable',delay=0.6,handler=self.game.coils.arkMagnet.disable)
             self.game.ball_save.start(num_balls_to_save=1,allow_multiple_saves=True,time=3)
             
             
        def jones_progress(self,num):
            if not self.jones_flags[num]:
                self.jones_flags[num]=True

                #test for a completed set of targets
                complete=True
                for i in range(len(self.jones_lamps)):
                    if self.jones_flags[i]==False:
                        complete=False

                if complete:
                    self.jones_completed()
                    
                else:
                    self.set_jones_lamps(num)
                    #self.inc_jackpot(self.map_target_score*10)
                    self.game.score(self.jones_target_score)
                    self.game.sound.play('jva_jones_target')
                    #self.game.effects.drive_flasher("flasherBackpanel", "fade", time=0.3)

                    
                    
        def jones_completed(self):
            self.completed_jones_lamps()
            #self.game.effects.drive_flasher("flasherBackpanel", "fade", time=1)
            self.game.sound.play('jva_jones_completed')
            
            self.smart_bomb(+1)
            
            self.game.score(self.jones_completed_score)
            
            self.delay(name='reset_jones', delay=1, handler=self.reset_jones)  
            
        
        def smart_bomb(self,value=1):
            
             self.smart_bombs+=value
             if self.smart_bombs>0:
                self.game.effects.drive_lamp(self.smart_bomb_lamp_button,'fast')
             else:
                self.game.effects.drive_lamp(self.smart_bomb_lamp_button,'off')
            
        
        def gi_flutter(self):
            self.log.info("GI FLUTTER")
            self.game.lamps.playfieldGI.schedule(0x000C0F0F,cycle_seconds=1)
            
        def inlane(self):
            self.game.score(100000)
            self.game.sound.play("ringmaster_inlane")


        def outlane(self):
            self.game.score(200000)
            self.game.sound.play("ringmaster_outlane")


        def clear(self):
            self.layer = None
            


        #switch handlers
        
        def sw_captiveBallRear_inactive(self, sw):
            return procgame.game.SwitchStop
        
        def sw_captiveBallFront_inactive_for_200ms(self, sw):
            return procgame.game.SwitchStop


        def sw_arkHit_active(self, sw):
            if self.game.switches.arkHit.time_since_change()>1 and self.game.switches.adventureV.time_since_change()>1 and self.game.switches.adventureE1N.time_since_change()>1:
                self.mode_progression()

            return procgame.game.SwitchStop
        
        def sw_adventureV_active(self, sw):
            if self.game.switches.arkHit.time_since_change()>1 and self.game.switches.adventureV.time_since_change()>1 and self.game.switches.adventureE1N.time_since_change()>1:
                self.mode_progression()

            return procgame.game.SwitchStop
        
        def sw_adventureE1N_active(self, sw):
            if self.game.switches.arkHit.time_since_change()>1 and self.game.switches.adventureV.time_since_change()>1 and self.game.switches.adventureE1N.time_since_change()>1:
                self.mode_progression()

            return procgame.game.SwitchStop
        
         


        def sw_leftLoopTop_active(self,sw):
       
            if self.game.switches.rightLoopTop.time_since_change()>1 and self.game.switches.leftLoopBottom.time_since_change()<0.25:
                self.score_value_boost+=self.score_value_extra
                
                self.load_loop_anim()
                self.game.sound.play('ringmaster_loop')
            
            return procgame.game.SwitchStop
  
             
        def sw_rightLoopTop_active(self,sw):
       
            if self.game.switches.leftLoopTop.time_since_change()>1 and self.game.switches.rightLoopBottom.time_since_change()<0.25:
                self.score_value_boost+=self.score_value_extra
            
                self.load_loop_anim()
                self.game.sound.play('ringmaster_loop')

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
        
        def sw_tournamentStart_active(self, sw):
            if self.smart_bombs>0:
                self.ship_destroyed()
                self.smart_bomb(-1)
                
            return procgame.game.SwitchStop