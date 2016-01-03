# Top Rollover Lanes

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

class Utility(game.Mode):

	def __init__(self, game):
            super(Utility, self).__init__(game, 5)

            self.log = logging.getLogger('ij.utility')
            self.game.sound.register_sound('elephant_alert', sound_path+"elephant.aiff")

        def ball_missing(self):
            text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)

            multiple = ''
            balls_missing = self.game.num_balls_total - self.game.num_balls()
            if balls_missing>1:
                multiple='s'
            text_layer.set_text(str(balls_missing)+" BALL"+multiple+" MISSING",1.5,5)#on for 1.5 seconds 5 blinks
            self.layer = text_layer
            self.game.sound.play('elephant_alert')


        def release_stuck_balls(self):
            #Release Stuck Balls code

            total_balls = self.game.trough.num_balls()+self.game.trough.num_balls_locked
            if total_balls<self.game.num_balls_total:

                self.log.info('Trough is full::%s',self.game.trough.is_full())
                self.log.info('Balls in trough::%s',self.game.trough.num_balls())
                self.log.info('Balls in Ark::%s',self.game.ark.num_balls())
                self.log.info('Subway Switch::%s',self.game.switches.subway.is_active())
                self.log.info('Scoop Switch::%s',self.game.switches.grailEject.is_active())
                
                self.log.info('Balls Locked::%s',self.game.trough.num_balls_locked)

                if self.game.switches.grailEject.is_active():
                    self.game.coils.grailEject.pulse()

                #check shooter lane
                if self.game.switches.shooterLane.is_active():
                    self.game.coils.ballLaunch.pulse()


                self.delay(name='release_stuck_balls_loop', event_type=None, delay=5, handler=self.release_stuck_balls)
            else:
                self.cancel_delayed('release_stuck_balls_loop')
            

        def check_map_room(self):
            #check for ball in map eject
            self.log.info('Map Eject Switch::%s',self.game.switches.mapEject.is_active())
            if self.game.switches.mapEject.is_active():
                self.game.coils.mapEject.pulse()
        


        def pause_game(self,active=True):
            self.game.paused = active
            self.game.enable_flippers(True) #update flipper rules
            
            if active:
                self.game.sound.pause()
                #self.game.coils.flipperLwRHold.enable()
                self.game.effects.drive_flasher('flasherPlaneGuns','fast')
                self.game.ball_search.disable()
                
            else:
                self.game.sound.un_pause()
                #self.game.coils.flipperLwRHold.disable()
                self.game.effects.drive_flasher('flasherPlaneGuns','off')
                self.game.ball_search.enable()
        
        
        def resume_mode_music(self):
            self.mode_music_list = ['gti_play','soc_background_play','wos_background_play','rvb_bgnd_play','monkey_brains_play','sts_background_play','minecart_mode_music','rope_bridge_play','castle_grunwald_play','ttc_background_play','tc_background_play','cw_background_play','jones_vs_aliens_play','frankenstein_play']
            mode_running_id = self.game.get_player_stats('mode_running_id')
            mode_running = self.game.get_player_stats('mode_running')
        
            if mode_running:
                self.game.sound.play_music(self.mode_music_list[mode_running_id], loops=-1)
            else:
                self.game.sound.play_music('general_play', loops=-1)
                
                