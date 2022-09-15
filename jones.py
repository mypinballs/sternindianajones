# Jones Targets Mode
# Copyright (C) 2016 myPinballs, Orange Cloud Software Ltd

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



class Jones(game.Mode):

	def __init__(self, game, priority):
            super(Jones, self).__init__(game, priority)

            #logging
            self.log = logging.getLogger('ij.jones')


            #screen setup
            #self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            #self.award_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=False)
            #self.award_layer.composite_op ="blacksrc"

            #sound setup
            self.game.sound.register_sound('jones_target_unlit', sound_path+"top_lane_unlit.aiff")
            self.game.sound.register_sound('jones_target_lit', sound_path+"top_lane_lit.aiff")
            #self.game.sound.register_sound('jones_completed', sound_path+"ij400A8_jones_jingle.aiff")
            self.game.sound.register_sound('jones_completed', speech_path+"ij4008E_dr_jones_jingle1.aiff")
            self.game.sound.register_sound('jones_completed', speech_path+"ij4008F_dr_jones_jingle2.aiff")

            self.game.sound.register_sound('jones_speech0', speech_path+"ij402C0_we_do_not_have_much_time.aiff")
            self.game.sound.register_sound('jones_speech0', speech_path+"ij402C4_what_does_this_ark_look_like.aiff")
            self.game.sound.register_sound('jones_speech0', speech_path+"ij4030B_dr_jones.aiff")


            self.game.sound.register_sound('jones_speech1', speech_path+"ij402C1_open_aswell_as_i.aiff")

            #var setup
            self.eight_ball_bank_count = int(self.game.user_settings['Gameplay (Feature)']['Jones Target Banks For 8 Ball'])
            self.score_value_boost = 5000000
            self.score_value_start = 5000000
            self.score_value_extra = 2000000

            #lamps setup
            self.jones_lamps = ['jonesJ','jonesO','jonesN','jonesE','jonesS']
            self.eight_ball_lamp = '8Ball'
            self.target_unlit_score = 10000
            self.target_lit_score = 5000
            self.completed_score = 500000


        def reset(self):
            self.jones_flags = [False,False,False,False,False]
            self.bank_count = 0
            self.running_total = 0

            self.reset_8ball()


        def set_lamps(self,id):
            self.game.effects.drive_lamp(self.jones_lamps[id],'smarton')
            for i in range(len(self.jones_lamps)):
                if not self.jones_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'medium')


        def update_lamps(self):
            for i in range(len(self.jones_lamps)):
                if self.jones_flags[i]:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'on')
                else:
                    self.game.effects.drive_lamp(self.jones_lamps[i],'medium')

            if self.eight_ball_multiball_lit:
                self.game.effects.drive_lamp(self.eight_ball_lamp,'superfast')


        def reset_lamps(self):
            for i in range(len(self.jones_lamps)):
                self.game.effects.drive_lamp(self.jones_lamps[i],'off')

            self.game.effects.drive_lamp(self.eight_ball_lamp,'off')


        def completed_lamps(self):
            for i in range(len(self.jones_lamps)):
                self.game.effects.drive_lamp(self.jones_lamps[i],'superfast')


        def reset_8ball(self):
            self.eight_ball_multiball_lit = False
            self.game.set_player_stats('8ball_multiball_lit',self.eight_ball_multiball_lit)
            self.game.effects.drive_lamp(self.eight_ball_lamp,'off')


        def eightball_progress_display(self):
            value = self.eight_ball_bank_count-self.bank_count
            timer =2
            #create display layer
            anim = dmd.Animation().load(game_path+"dmd/shorty_plain.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            text_layer1 = dmd.TextLayer(88, 0, self.game.fonts['9x7_bold'], "center", opaque=False)
            text_layer2 = dmd.TextLayer(88, 13, self.game.fonts['07x5'], "center", opaque=False)
            text_layer3 = dmd.TextLayer(88, 20, self.game.fonts['07x5'], "center", opaque=False)
            text_layer1.set_text(str(value)+' MORE',blink_frames=10,seconds=timer,color=dmd.CYAN)
            text_layer2.set_text('JONES FOR',seconds=timer,color=dmd.GREEN)
            text_layer3.set_text('8 BALL',seconds=timer,color=dmd.GREEN)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer1,text_layer2,text_layer3])

            self.delayed_clear(timer)


        def eightball_lit_display(self):
            timer=2
            #create display layer
            anim = dmd.Animation().load(game_path+"dmd/shorty_plain.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            text_layer1 = dmd.TextLayer(88, 5, self.game.fonts['9x7_bold'], "center", opaque=False)
            text_layer2 = dmd.TextLayer(88, 18, self.game.fonts['9x7_bold'], "center", opaque=False)
            text_layer1.set_text('8 BALL',seconds=timer,color=dmd.GREEN)
            text_layer2.set_text('IS LIT',blink_frames=10,seconds=timer,color=dmd.GREEN)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer1,text_layer2])

            self.delayed_clear(timer)


        def voice_call(self,count,delay=None):
            if delay==None:
                self.game.sound.play_voice("jones_speech"+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)



        def mode_started(self):
            if self.game.ball==1:
                self.reset()

            #get player stats
            self.jones_flags = self.game.get_player_stats('jones_flags')
            self.eight_ball_multiball_lit = self.game.get_player_stats('8ball_multiball_lit')
            self.bank_count = self.game.get_player_stats('jones_banks_completed')

            self.update_lamps()


        def mode_tick(self):
            pass


        def mode_stopped(self):

            #update player stats
            self.game.set_player_stats('jones_flags',self.jones_flags)
            self.game.set_player_stats('jones_banks_completed',self.bank_count)

            #update lamps
            self.reset_lamps()


        def progress(self,num):
            if not self.jones_flags[num]:
                self.jones_flags[num]=True

                #test for a completed set of targets
                complete=True
                for i in range(len(self.jones_lamps)):
                    if self.jones_flags[i]==False:
                        complete=False

                if complete:
                    self.completed()

                else:
                    self.set_lamps(num)
                    #self.inc_jackpot(self.map_target_score*10)
                    self.game.score(self.target_unlit_score)
                    self.game.sound.play('jones_target_unlit')
                    #self.game.effects.drive_flasher("flasherBackpanel", "fade", time=0.3)
            else:
                self.game.score(self.target_lit_score)
                self.game.sound.play('jones_target_lit')


        def completed(self):
            self.bank_count +=1
            self.completed_lamps()
            #self.game.effects.drive_flasher("flasherBackpanel", "fade", time=1)
            self.game.sound.play('jones_completed')
            self.game.score(self.completed_score)

            if self.bank_count<self.eight_ball_bank_count:
                self.eightball_progress_display()
                self.voice_call(count=0,delay=1.5)
                self.game.effects.drive_flasher('flasherArk','fast',time=0.5)

            elif self.bank_count%self.eight_ball_bank_count==0:
                self.eight_ball_multiball_lit = True
                self.game.set_player_stats('8ball_multiball_lit',self.eight_ball_multiball_lit)
                self.eightball_lit_display()
                self.voice_call(count=1,delay=1.5)
                self.game.effects.drive_flasher('flasherArk','fast',time=2)
                self.gi_flutter()

            self.delay(name='reset_jones', delay=1, handler=self.reset)


        def gi_flutter(self):
            self.log.info("GI FLUTTER")
            self.game.lamps.playfieldGI.schedule(0x000C0F0F,cycle_seconds=1)


        def delayed_clear(self,timer=2):
            self.delay(name='clear_delay', event_type=None, delay=timer, handler=self.clear)


        def clear(self):
            self.layer = None


        #switch handlers
        def sw_jonesJ_active(self,sw):
            self.progress(0)

        def sw_jonesO_active(self,sw):
            self.progress(1)

        def sw_jonesN_active(self,sw):
            self.progress(2)

        def sw_jonesE_active(self,sw):
            self.progress(3)

        def sw_jonesS_active(self,sw):
            self.progress(4)
