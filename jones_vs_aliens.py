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


class Jones_Vs_Aliens(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Jones_Vs_Aliens, self).__init__(game, priority)

            #logging
            self.log = logging.getLogger('ij.jones_vs_aliens')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Jones Vs Aliens Timer'])
            self.log.info("Jones Vs Aliens Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            #self.award_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=False)
            #self.award_layer.composite_op ="blacksrc"

            #sound setup
            self.game.sound.register_music('jones_vs_aliens_play', music_path+"jones_vs_aliens.aiff")
            self.game.sound.register_sound('jva_forcefield_hit', sound_path+"afm322_explosion2.aiff")
            self.game.sound.register_sound('jva_inlane', sound_path+"afm828_beam_noise.wav")
            self.game.sound.register_sound('jva_outlane', sound_path+"afm340_drain_noise.wav")
            self.game.sound.register_sound('jva_loop', sound_path+"afm246_woosh.wav")
            self.game.sound.register_sound('jva_jones_target', sound_path+"afm158_laser_shot.aiff")
            self.game.sound.register_sound('jva_jones_completed', sound_path+"afm328_celebratory_riff.wav")

            self.game.sound.register_sound('jva_ship_explosion', sound_path+"afm208_nice_explosion.aiff")
            self.game.sound.register_sound('jva_ship_explosion', sound_path+"afm260_nice_big_explosion.aiff")


            self.game.sound.register_sound('jva_speech0', speech_path+"afm_newsanchor_emergency_broadcast.ogg")
            self.game.sound.register_sound('jva_speech0', speech_path+"afm_newsanchor_this just_in.ogg")
            self.game.sound.register_sound('jva_speech1', speech_path+"afm540_you_cannot_defeat_our_forcefield.aiff")
            self.game.sound.register_sound('jva_speech1', speech_path+"afm546_nothing_can_defeat_us.aiff")
            self.game.sound.register_sound('jva_speech1', speech_path+"afm544_ah_ah_ah.aiff")
            self.game.sound.register_sound('jva_speech1', speech_path+"afm547_it_will_nver_work.aiff")
            self.game.sound.register_sound('jva_speech1', speech_path+"afm544_ah_ah_ah.aiff")
            self.game.sound.register_sound('jva_speech1', speech_path+"afm550_shoe_untied.aiff")

            self.game.sound.register_sound('jva_speech2', speech_path+"afm880_run_away.aiff")
            self.game.sound.register_sound('jva_speech2', speech_path+"afm1112_oh_no.aiff.aiff")

            self.game.sound.register_sound('jva_speech3', speech_path+"afm932_martian_growl.aiff")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm1110_i_hate_humans.aiff")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm896_cant_we_be_friends.aiff")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm_groan1.wav")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm_groan2.wav")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm_groan3.wav")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm_groan4.wav")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm_groan5.wav")
            self.game.sound.register_sound('jva_speech3', speech_path+"afm_groan6.wav")

            self.game.sound.register_sound('jva_speech4', sound_path+"afm328_celebratory_riff.wav")

            #var setup
            self.mode_started_value = int(self.game.user_settings['Gameplay (Feature)']['Mode Start Value (Mil)'])*1000000
            self.forcefield_hits = 3
            self.ship_hits = 3
            self.score_value_boost = 5000000
            self.score_value_start = 5000000
            self.score_value_extra = 2000000
            self.forcefield_hit_value = 100000
            self.ship_hit_value = 250000

            #lamps setup
            self.lamps = ['raidersArrow']

            self.jones_lamps = ['jonesJ','jonesO','jonesN','jonesE','jonesS']
            self.jones_target_score = 10000
            self.jones_completed_score = 500000

            self.smart_bomb_lamp_button = 'tournamentStartButton'


        def reset(self):
            self.count = 0
            self.ships_destroyed = 0
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


        def load_forcefield_hit_anim(self):
            self.bgnd_anim = "dmd/jva_ship_forcefield.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)

            self.bgnd_layer.add_frame_listener(-1, self.load_bgnd_anim)

            self.layer = self.bgnd_layer


        def load_ship_anim(self):
            self.bgnd_anim = "dmd/jva_large_ship.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=True,frame_time=6)
            self.layer = self.bgnd_layer


        def load_ship_hit_anim(self):
            self.bgnd_anim = "dmd/jva_large_ship_damage.dmd"
            self.explosion_anim = "dmd/jva_blast_wipe.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=True,frame_time=6)
            anim = dmd.Animation().load(game_path+self.explosion_anim)
            self.explosion_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.explosion_layer.target_x=random.randint(-40,40)
            #self.explosion_layer.target_y=random.randint(5,20)
            self.explosion_layer.composite_op ="blacksrc"
            self.explosion_layer.add_frame_listener(-1, self.load_ship_anim)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.explosion_layer])


        def load_ship_destroyed_anim(self):
            self.bgnd_anim = "dmd/jva_large_ship_explodes.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.bgnd_layer.add_frame_listener(-1, self.load_bgnd_anim)
            self.layer = self.bgnd_layer


        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/jva_aliens_border.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)

            #set destroyed text
            self.destroyed_layer.set_text("SHIPS DESTROYED: "+str(self.ships_destroyed_count), color=dmd.RED)

            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.destroyed_layer])


        def load_loop_anim(self,timer=2):
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/jva_ships_border.dmd").frames[0])
            name_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center")
            info_layer = dmd.TextLayer(128/2, 15, self.game.fonts['9x7_bold'], "center")

            name_layer.set_text('Ship Value'.upper(),color=dmd.BROWN)
            ship_value = self.score_value_start+self.score_value_boost
            info_layer.set_text(locale.format("%d",ship_value,True),color=dmd.GREEN)

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,name_layer,info_layer])

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
            self.timer_layer = dmd.TimerLayer(128, 25, self.game.fonts['07x5'],self.timer,"right", colour=dmd.YELLOW)
            self.destroyed_layer = dmd.TextLayer(128/2, 12, self.game.fonts['8x6'], "center", opaque=False)
            self.info_layer = dmd.TextLayer(128/2, 24, self.game.fonts['07x5'], "center", opaque=False)

            #load player stats
            self.ships_destroyed_count = self.game.get_player_stats('jva_ships_destroyed')
            self.smart_bombs = self.game.get_player_stats('jva_smart_bombs')

            #update path mode var
            self.game.set_player_stats("path_mode_started",True) #set as path mode to halt adventure starting if completed
            self.game.set_player_stats("ark_mode_started",True)

            #setup text
            self.info_layer.set_text("SHOOT ARK TO ATTACK", blink_frames=10, color=dmd.PURPLE)

            #load animation
            self.load_bgnd_anim()

            #start mode music & speech
            self.game.sound.play_music('jones_vs_aliens_play', loops=-1)
            self.voice_call(count=0,delay=2)

            self.running_total=self.mode_started_value

            #update lamps
            self.update_lamps()


        def voice_call(self,count,delay=None):
            if delay==None:
                self.game.sound.play_voice("jva_speech"+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)
#
#            #additional speech calls
#            if count==0:
#                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=11)
#                self.delay(name='aux_mode_speech_delay', event_type=None, delay=6, handler=self.voice_call, param=12)
#            if count==2:
#                self.delay(name='aux_mode_speech_delay', event_type=None, delay=1.2, handler=self.voice_call, param=13)
#                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2.5, handler=self.voice_call, param=14)
#            if count==3:
#                self.delay(name='aux_mode_speech_delay', event_type=None, delay=1, handler=self.voice_call, param=15)



        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)


        def mode_tick(self):
            pass

        def mode_stopped(self):
            #save player stats
            self.game.set_player_stats('jva_ships_destroyed',self.ships_destroyed)
            self.game.set_player_stats('jva_ships_destroyed',self.smart_bombs)

            self.game.set_player_stats('jones_vs_aliens_score',self.running_total)
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
            if self.count<=self.forcefield_hits:
                self.forcefield_progress()
            elif self.count<=self.forcefield_hits+self.ship_hits:
                self.ship_progress()
            else:
                self.ship_destroyed()


        def forcefield_progress(self):
            #setup anim
            if self.count<self.forcefield_hits:
                self.load_forcefield_hit_anim()
                self.voice_call(count=1,delay=1.5)
            else:
                self.load_forcefield_down_anim()
                self.voice_call(count=2,delay=0.5)

            #play speech/sound
            self.game.sound.play("jva_forcefield_hit")

            #effects
            self.ark_hit()

            self.game.score(self.forcefield_hit_value)


        def ship_progress(self):
            #setup anim
            self.load_ship_hit_anim()

            #play speech/sound
            self.game.sound.play("jva_ship_explosion")
            self.voice_call(count=3,delay=1.5)

            #effects
            self.ark_hit()
            self.gi_flutter()

            self.game.score(self.ship_hit_value)


        def ship_destroyed(self):
            #setup anim
            self.load_ship_destroyed_anim()

            #play speech/sound
            self.game.sound.play("jva_ship_explosion")
            self.voice_call(count=4,delay=1)

            #effects
            self.ark_hit()
            self.game.lampctrl.play_show('success', repeat=False,callback=self.game.update_lamps)
            self.gi_flutter()

            self.ships_destroyed_count+=1

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
            self.game.sound.play("jva_inlane")


        def outlane(self):
            self.game.score(200000)
            self.game.sound.play("jva_outlane")


        def clear(self):
            self.layer = None



        #switch handlers

        def sw_captiveBallRear_inactive(self, sw):
            return procgame.game.SwitchStop

        def sw_captiveBallFront_inactive_for_200ms(self, sw):
            return procgame.game.SwitchStop


        def sw_arkHit_active(self, sw):
            if self.game.switches.arkHit.time_since_change()>1:
                self.mode_progression()

            return procgame.game.SwitchStop

        def sw_adventureV_active(self, sw):
            if self.game.switches.adventureV.time_since_change()>1:
                self.mode_progression()

            return procgame.game.SwitchStop

        def sw_adventureE1N_active(self, sw):
            if self.game.switches.adventureE1N.time_since_change()>1:
                self.mode_progression()

            return procgame.game.SwitchStop


        def sw_leftLoopTop_active(self,sw):

            if self.game.switches.rightLoopTop.time_since_change()>1 and self.game.switches.leftLoopBottom.time_since_change()<0.25:
                self.score_value_boost+=self.score_value_extra

                self.load_loop_anim()
                self.game.sound.play('jva_loop')

            return procgame.game.SwitchStop


        def sw_rightLoopTop_active(self,sw):

            if self.game.switches.leftLoopTop.time_since_change()>1 and self.game.switches.rightLoopBottom.time_since_change()<0.25:
                self.score_value_boost+=self.score_value_extra

                self.load_loop_anim()
                self.game.sound.play('jva_loop')

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
