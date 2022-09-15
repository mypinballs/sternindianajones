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
music_path = game_path +"music/"

class Utility(game.Mode):

	def __init__(self, game):
            super(Utility, self).__init__(game, 99)

            self.log = logging.getLogger('ij.utility')
            self.game.sound.register_sound('elephant_alert', sound_path+"elephant.aiff")
            
            #hs entry stuff
            self.game.sound.register_music('hs_entry_music', music_path+"raiders_march.aiff")
            self.game.sound.register_sound('initial_letter_move', sound_path+"swipe_1.aiff")
            self.game.sound.register_sound('initial_letter_enter', sound_path+"match_success.aiff")
            self.game.sound.register_sound('entry_complete_jingle', sound_path+"ij400A8_jones_jingle.aiff")
            self.game.sound.register_sound('well_done', speech_path+"well_done_my_friend.aiff")
            

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
            
            if total_balls<self.game.num_balls_total and self.game.is_game_over():              
                self.log.info('Trough is full::%s',self.game.trough.is_full())
                self.log.info('Balls in trough::%s',self.game.trough.num_balls())
                self.log.info('Balls in Ark::%s',self.game.ark.num_balls())
                self.log.info('Subway Switch::%s',self.game.switches.subway.is_active())
                self.log.info('Scoop Switch::%s',self.game.switches.grailEject.is_active())
                
                self.log.info('Balls Locked::%s',self.game.trough.num_balls_locked)

                if self.game.ark.ark_state=="full":
                    if self.game.switches.grailEject.is_active():
                        self.game.coils.grailEject.pulse()

                    #check shooter lane
                    if self.game.switches.shooterLane.is_active():
                        self.game.coils.ballLaunch.pulse()


                    self.delay(name='release_stuck_balls_loop', event_type=None, delay=5, handler=self.release_stuck_balls)
                else:
                    self.log.info('Waiting for Ark, before looking for stuck balls')
            else:
                self.cancel_delayed('release_stuck_balls_loop')
            

        def check_map_room(self):
            #check for ball in map eject
            self.log.info('Map Eject Switch::%s',self.game.switches.mapEject.is_active())
            if self.game.switches.mapEject.is_active():
                self.game.coils.mapEject.pulse()
        


        def pause_game(self,active=True):
            self.game.paused = active
            
            if active:
                self.game.enable_flippers(False) #update flipper rules
                drivers=[]
                self.game.proc.switch_update_rule(self.game.switches['flipperLwR'].number, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
                        
                info_layer = dmd.TextLayer(128/2, 5, self.game.fonts['7px_narrow_az'], "center", opaque=False)
                info_layer2a = dmd.TextLayer(128/2, 15, self.game.fonts['07x5'], "center", opaque=False)
                info_layer2b = dmd.TextLayer(128/2, 21, self.game.fonts['07x5'], "center", opaque=False)
                bgnd_layer = dmd.FrameLayer(opaque=False)
                bgnd_layer.frame = dmd.Animation().load(game_path+'dmd/scene_ended_bgnd.dmd').frames[0]
            
                info_layer.set_text("GAME PAUSED", color=dmd.CYAN)
                info_layer2a.set_text("HOLD TOURNAMENT BUTTON",color=dmd.GREEN,blink_frames=12)
                info_layer2b.set_text("TO CONTINUE",color=dmd.GREEN,blink_frames=12)
                
                self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer2b,info_layer2a,info_layer])
            
                self.game.sound.pause()
                self.game.coils.flipperLwRMain.pulsed_patter(2,18)
                self.game.effects.drive_flasher('flasherSankara','medium',time=0)
                self.game.effects.drive_lamp('tournamentStartButton','fast')
                self.game.ball_search.disable()
  
            else:
                self.layer=None
                self.game.sound.un_pause()
                self.game.coils.flipperLwRMain.disable()
                self.game.effects.drive_flasher('flasherSankara','off')
                self.game.effects.drive_lamp('tournamentStartButton','off')
                self.game.ball_search.enable()
                
                self.game.enable_flippers(True) #update flipper rules
        
        
        def resume_mode_music(self):
            self.log.info('Utility Mode Music Resumer Called')
            self.mode_music_list = ['gti_play','soc_background_play','wos_background_play','rvb_bgnd_play','monkey_brains_play','sts_background_play','minecart_mode_music','rope_bridge_play','castle_grunwald_play','tc_background_play','ttc_background_play','cw_background_play','warehouse_background_play','nuke_test_play','return_the_skull_play','jones_vs_aliens_play','frankenstein_play']
            mode_running_id = self.game.get_player_stats('mode_running_id')
            mode_running = self.game.get_player_stats('mode_running')
            qm_ready = self.game.get_player_stats('quick_multiball_ready')
            qm_started = self.game.get_player_stats('quick_multiball_started')
            adventure_started = self.game.get_player_stats('adventure_started')
        
            if mode_running:
                self.game.sound.play_music(self.mode_music_list[mode_running_id], loops=-1)
            elif qm_started:
                self.game.sound.play_music('qm_running', loops=-1)
            elif qm_ready:
                self.game.sound.play_music('qm_ready', loops=-1)
            elif adventure_started:
                 self.game.sound.play_music('poa_play', loops=-1)
            else:
                self.game.sound.play_music('general_play', loops=-1)
                
                