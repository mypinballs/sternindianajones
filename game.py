import sys
sys.path.append(sys.path[0]+'/../..') # Set the path so we can find procgame.  We are assuming (stupidly?) that the first member is our directory.
import procgame
import pinproc
import string
import time
import datetime
import locale
import math
import copy
import yaml
import random
import os
import logging
import audits
import diagnostics
import ep

from procgame import *
from threading import Thread

from scoredisplay import *
from player import *
from ark import *
from temple import *
from swordsman import *
#from idol import *
#from mini_playfield import *
from moonlight import *
from trough import *
from effects import *
#from rgb_lamps import *
from volume import *
from extra_ball import *
from screens import *
from ball_search import *
from service import *
from utility import *
from tilt import *
from highscore import EntrySequenceManager

from attract import *
from base import *
from match import *

from random import *
from time import strftime

serial = config.value_for_key_path('game_serial')

game_locale = config.value_for_key_path('std_locale')
locale.setlocale(locale.LC_ALL, game_locale) # en_GB Used to put commas in the score.

base_path = config.value_for_key_path('base_path')
logging.info("Base Path is: "+base_path)

game_path = base_path+"games/indyjones2/"
fonts_path = base_path+"shared/dmd/"
shared_sound_path = base_path+"shared/sound/"

machine_config_path = game_path + "config/machine.yaml"
settings_path = game_path +"config/settings.yaml"
game_data_path = game_path +"config/game_data.yaml"
game_data_template_path = game_path +"config/game_data_template.yaml"
settings_template_path = game_path +"config/settings_template.yaml"
displayed_audits_path = game_path +"config/audits_display.yaml"
dots_path = game_path + "dots/"
images_path = game_path + "images/"

voice_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"
font_tiny7 = dmd.Font(fonts_path+"04B-03-7px.dmd")
font_jazz18 = dmd.Font(fonts_path+"Jazz18-18px.dmd")
font_14x10 = dmd.Font(fonts_path+"Font14x10.dmd")
font_18x12 = dmd.Font(fonts_path+"Font18x12.dmd")
#font_07x4 = dmd.font_named("font_7x4.dmd")
font_07x5 = dmd.font_named("font_7x5.dmd")
font_09Bx7 = dmd.Font(fonts_path+"font_10x7_bold.dmd")
font_6x6_bold = dmd.Font(fonts_path+"font_8x7_bold.dmd")
font_23x12 = dmd.font_named("font_23x12_bold.dmd")
font_8x6_bold = dmd.font_named("font_9x6_bold.dmd")

attract_lampshow_files = [game_path +"lamps/general/searchlight_128.lampshow", \
                game_path +"lamps/general/vertical_wipe_up_down_144.lampshow",\
                game_path +"lamps/general/centre_fill_64.lampshow"]


class Game(game.BasicGame):
        """docstring for Game"""
        def __init__(self, machine_type):
                super(Game, self).__init__(machine_type)

                self.log = logging.getLogger('ij.game')
                self.sound = procgame.sound.SoundController(self)
                self.lampctrl = procgame.lamps.LampController(self)
                self.settings = {}

                self.colour_dmd = None

                #set the dmd colour map - level 1 is mask and set to 0
                #dmd_map = [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                dmd_map = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 5, 11, 12, 13, 14, 15]
                self.proc.set_dmd_color_mapping(dmd_map)

                use_desktop = config.value_for_key_path(keypath='use_desktop', default=True)
                self.colour_desktop = config.value_for_key_path(keypath='colour_desktop', default=False)
                colour_dmd_installed = config.value_for_key_path(keypath='colour_dmd_installed', default=False)
                self.rpi_computer = config.value_for_key_path(keypath='rPi_installed', default=False)
                self.rpi_hardware_video = config.value_for_key_path(keypath='rPi_hardware_video', default=False)
                if use_desktop:
                    #if colour, run colour desktop
                    if self.colour_desktop:
                        if self.rpi_computer:
                            self.log.info("rPi Optimised Colour Desktop")
                            from mpc import rPi_Desktop
                            self.desktop = rPi_Desktop()
                        else:
                            self.log.info("Standard Colour Desktop")
                            from ep import EP_Desktop
                            self.desktop = EP_Desktop()

                    # if not color, run the old style pygame
                    else:
                        self.log.info("Standard Desktop")
                        from procgame.desktop import Desktop
                        self.desktop = Desktop()

                #if colour dmd run colour dmd desktop
                if colour_dmd_installed:
                    self.log.info("Colour DMD Panel Installed")
                    from mpc import rgbLedDMDMatrix
                    self.colour_dmd = rgbLedDMDMatrix(self)


                #debug
#                for coil in self.coils:
#                    self.log.debug("Game Config:"+str(coil.name)+" "+str(coil.number))
#                for lamp in self.lamps:
#                    self.log.debug("Game Config:"+str(lamp.name)+" "+str(lamp.number))


                #setup score display
                self.score_display = ScoreDisplay(self, 0)

                #create displayed audits dict
                self.displayed_audits = yaml.load(open(displayed_audits_path, 'r'))
                #load and update audits database
                audits.load(self)

                #setup diagnostics
                self.health_status = ''
                self.switch_error_log =[]
                self.device_error_log=[]


        #add control for update of last dmd frame onto a colour rgb dmd panel
        def show_last_frame(self):
                #super(Game, self).show_last_frame()

                if self.last_frame:
                    if self.colour_dmd:
                        self.colour_dmd.draw(self.last_frame)
                    if self.desktop:
                        self.desktop.draw(self.last_frame)

                    self.last_frame = None
                    del self.last_frame



        def save_settings(self):
                #self.write_settings(settings_path)
                super(Game, self).save_settings(settings_path)
                #pass

        def save_game_data(self):
                super(Game, self).save_game_data(game_data_path)

        def create_player(self, name):
                return Player(name)


        def setup(self):
                """docstring for setup"""
                self.load_config(self.yamlpath)

                #load the settings data file
                #this can be occasionally corrupted (blank) by hard power offs, so use some try catch here to stop a bomb out
                try:
                    self.load_settings(settings_template_path, settings_path)
                except Exception as err:
                    self.log.error('Settings Data Corrupt. Resetting....')
                    try:
                        os.remove(settings_path)
                        self.load_settings(settings_template_path, settings_path)
                        self.log.info('Settings Data File Recreated')
                    except OSError:
                        self.log.error('Unable to recreate Settings Data File from Template. Damn....')

                #load the game data file
                #this can be corrupted (blank) by hard power offs, so use some try catch here to stop a bomb out
                try:
                    self.load_game_data(game_data_template_path, game_data_path)
                except Exception as err:
                    self.log.error('Game Data Corrupt. Resetting....')
                    try:
                        os.remove(game_data_path)
                        self.load_game_data(game_data_template_path, game_data_path)
                        self.log.info('Game Data File Recreated')
                    except OSError:
                        self.log.error('Unable to recreate Game Data File from Template. Damn....')


                #define system status var
                self.system_status='power_up'
                self.system_version='0.9.1'
                self.system_name='Indiana Jones 2'.upper()

                # Setup fonts
                self.fonts = {}
                #self.fonts['jazz18'] = font_jazz18
                self.fonts['18x12'] = font_18x12
                self.fonts['num_14x10'] = font_14x10
                self.fonts['num_07x4'] = dmd.font_named("font_7x4.dmd")

                self.fonts['tiny7'] = font_tiny7
                self.fonts['7x4'] = dmd.font_named("font_7x4.dmd")
                self.fonts['7x4'].tracking = -1
                self.fonts['7x4'].composite_op ="blacksrc"

                self.fonts['07x5'] = dmd.font_named("font_7x5.dmd")
                self.fonts['07x5'].tracking = -1
                self.fonts['07x5'].composite_op ="blacksrc"

                self.fonts['6x6_bold'] = dmd.font_named("font_8x7_bold.dmd")
                self.fonts['6x6_bold'].tracking = -1
                self.fonts['6x6_bold'].composite_op ="blacksrc"

                self.fonts['8x6'] = dmd.font_named("font_9x6_bold.dmd")
                self.fonts['8x6'].tracking = -1
                self.fonts['8x6'].composite_op ="blacksrc"

                self.fonts['num_09Bx7'] = dmd.font_named("font_10x7_bold.dmd")
                self.fonts['num_09Bx7'].tracking = -1
                self.fonts['num_09Bx7'].composite_op ="blacksrc"

                self.fonts['9x7_bold'] = dmd.font_named("font_10x7_bold.dmd")
                self.fonts['9x7_bold'].tracking = -1
                self.fonts['9x7_bold'].composite_op ="blacksrc"

                self.fonts['10x7_bold'] = dmd.font_named("font_12x8_bold.dmd")
                self.fonts['10x7_bold'].tracking = -1
                self.fonts['10x7_bold'].composite_op ="blacksrc"

                self.fonts['14x9_bold'] = dmd.font_named("font_14x9.dmd")
                self.fonts['14x9_bold'].tracking = -1
                self.fonts['14x9_bold'].composite_op ="blacksrc"

                self.fonts['23x12'] = dmd.font_named("font_23x12_bold.dmd")
                self.fonts['23x12'].tracking = -1
                self.fonts['23x12'].composite_op ="blacksrc"

                self.fonts['30x13'] = dmd.font_named("font_30x13_bold.dmd")
                self.fonts['30x13'].tracking = -1
                self.fonts['30x13'].composite_op ="blacksrc"

                self.fonts['4px_az'] = dmd.font_named("font_7x4.dmd")
                self.fonts['5px_az'] = dmd.font_named("font_7x5.dmd")
                self.fonts['5px_inv_az'] = dmd.font_named("font_7x5_inverted.dmd")
                self.fonts['6px_az'] = dmd.font_named("Font_19_CactusCanyon.dmd")
                self.fonts['7px_narrow_az'] = dmd.font_named("Font_1_CactusCanyon.dmd")
                self.fonts['7px_az'] = dmd.font_named("Font_2_CactusCanyon.dmd")
                self.fonts['7px_bold_az'] = dmd.font_named("Font_14_CactusCanyon.dmd")
                self.fonts['9px_az'] = dmd.font_named("Font_15_CactusCanyon.dmd")
                self.fonts['10px_az'] = dmd.font_named("Font_Custom_10px_AZ.dmd")

                #setup paths
                self.paths = {}
                self.paths['game'] = game_path
                self.paths['sound'] = sound_path
                self.paths['speech'] = voice_path
                self.paths['music'] = music_path
                self.log.info(self.paths)

                #update audit data on boot up time
                audits.record_value(self,'bootUp')

                #set start time game var
                self.start_time = time.time()

#                print "Stats:"
#                print self.game_data
#                print "Settings:"
#                print self.settings

                #configure of switch types and coil types (solenoid or flasher) for mypinballs controller class
                io_controller = config.value_for_key_path(keypath='pinproc_class', default='')
                if 'mypinballs' in io_controller:
                    self.proc.config(self.switches,self.coils)

                #config debug info
                self.log.info("Initial switch states:")
                for sw in self.switches:
                        self.log.info("  %s:\t%s:\t%s" % (sw.number, sw.name, sw.state_str()))
#
                self.log.info("Lamp Info:")
                for lamp in self.lamps:
                        self.log.info("  %s:\t%s:\t%s" % (lamp.number, lamp.name, lamp.yaml_number))
#
                #balls per game setup
                self.balls_per_game = self.user_settings['Machine (Standard)']['Balls Per Game']

                #moonlight setup
                self.moonlight_minutes = self.user_settings['Gameplay (Feature)']['Moonlight Mins to Midnight']
                self.moonlight_flag = False

                self.setup_ball_search()
                self.score_display.set_left_players_justify(self.user_settings['Display']['Left side score justify'])

                #speech setup
                self.extended_speech = self.boolean_format(self.user_settings['Sound']['Extended Speech'])
                self.log.info('Extended Speech Enabled:%s',self.extended_speech)

                # Note - Game specific item:
                # The last parameter should be the name of the game's ball save lamp
                self.ball_save = procgame.modes.BallSave(self, self.lamps.shootAgain, 'shooterLane')

                trough_switchnames = []
                # Note - Game specific item:
                # This range should include the number of trough switches for
                # the specific game being run.  In range(1,x), x = last number + 1.
                for i in range(1,7):
                        trough_switchnames.append('trough' + str(i))
                early_save_switchnames = ['rightOutlaneBottom', 'leftOutlane']

                # Note - Game specific item:
                # Here, trough6 is used for the 'eject_switchname'.  This must
                # be the switch of the next ball to be ejected.  Some games
                # number the trough switches in the opposite order; so trough1
                # might be the proper switchname to user here.

                #setup trough
                self.trough = Trough(game=self,drain_callback=self.drain_callback)
                # Link ball_save to trough
                self.trough.ball_save_callback = self.ball_save.launch_callback
                self.trough.num_balls_to_save = self.ball_save.get_num_balls_to_save
                self.ball_save.trough_enable_ball_save = self.trough.enable_ball_save

                #setup & init service modes
                self.service_mode = ServiceMode(self,100,font_07x5,font_8x6_bold,[])
                self.coin_door = CoinDoor(self)

                # Register lampshow files for attact
                self.lampshow_keys = []
                key_ctr = 0
                for file in attract_lampshow_files:
                    if file.find('flasher',0)>0:
                        key = 'attract_flashers_' + str(key_ctr)
                    else:
                        key = 'attract_lamps_' + str(key_ctr)
                    self.lampshow_keys.append(key)
                    self.lampctrl.register_show(key, file)
                    key_ctr += 1

                #register game play lamp show
                self.lampctrl.register_show('success', game_path +"lamps/game/success.lampshow")
                self.lampctrl.register_show('ball_lock', game_path +"lamps/game/success.lampshow")
                self.lampctrl.register_show('hit', game_path +"lamps/game/success.lampshow")
                self.lampctrl.register_show('jackpot', game_path +"lamps/game/success.lampshow")
                self.lampctrl.register_show('start_ball', game_path +"lamps/game/start_ball_32.lampshow")
                self.lampctrl.register_show('end_ball', game_path +"lamps/game/end_ball_32.lampshow")
                self.lampctrl.register_show('mode_start_shot', game_path +"lamps/game/mode_start_shot_32.lampshow")
                self.lampctrl.register_show('mode_start_eject', game_path +"lamps/game/mode_start_eject_32.lampshow")

                # Setup High Scores
                self.setup_highscores()
                #allow access of hs initials from other modes
                self.last_entered_inits = None


                #Setup Date & Time Display
                self.show_date_time = self.user_settings['Machine (Standard)']['Show Date and Time']

                #Maximum Players
                self.max_players = 4;

                #setup paused flag
                self.paused = False

                #add basic modes
                #------------------
                #attract mode
                self.attract_mode = Attract(self)
                #moonlight mode - special
                self.moonlight = Moonlight(self,2)
                #effects mode
                self.effects = Effects(self,4)
                #basic game control mode
                self.base_game_mode = BaseGameMode(self)
                #rgb lamps mode
                #self.rgb_lamps = RGBLamps(self,4)
                #utility mode
                self.utility = Utility(self)
                #tilt mode
                self.tilt = Tilt(self,5)
                #extra ball mode
                self.extra_ball = Extra_Ball(self)
                #screens mode
                self.screens = Screens(self)
                #volume mode
                self.volume = Volume(self)
                #match mode
                self.match = Match(self,10)
                #add ark mode for ark logic and control
                self.ark = Ark(self,15)
                #add temple mode for temple logic and control
                self.temple = Temple(self,15)
                #add temple mode for temple logic and control
                self.swordsman = Swordsman(self,15)
                #add idol mode for idol logic and control
                #self.idol = Idol(self,15)
                #setup mini_playfield
                #self.mini_playfield = Mini_Playfield(self,16)
                #------------------


                # set up the color desktop if we're using that
                if self.colour_desktop:
                    self.desktop.draw_window(self.user_settings['Display']['Color Display Pixel Size'],self.user_settings['Display']['Color Display X Offset'],self.user_settings['Display']['Color Display Y Offset'])
                    # load the images for the colorized display
                    self.desktop.load_images(dots_path)


                # Instead of resetting everything here as well as when a user
                # initiated reset occurs, do everything in self.reset() and call it
                # now and during a user initiated reset.
                self.reset()

        def setup_highscores(self):
                self.highscore_categories = []

                #regular high scores
                cat = highscore.HighScoreCategory()
                cat.game_data_key = 'ClassicHighScoreData'
                self.highscore_categories.append(cat)

                #POA Champion
                cat = highscore.HighScoreCategory()
                cat.game_data_key = 'POAChampionData'
                cat.titles = ['Adventure Champ']
                cat.score_suffix_singular = ' Adventure'
                cat.score_suffix_plural = ' Adventures'
                cat.score_for_player = lambda player: player.player_stats['adventures_started']
                self.highscore_categories.append(cat)
#
                #Treasure Champion
                cat = highscore.HighScoreCategory()
                cat.game_data_key = 'TreasureChampionData'
                cat.titles = ['Treasure Champ']
                cat.score_suffix_singular = ' Artifact'
                cat.score_suffix_plural = ' Artifacts'
                cat.score_for_player = lambda player: player.player_stats['treasures_collected']
                self.highscore_categories.append(cat)

                #Loopin' Ramp Champion
                cat = highscore.HighScoreCategory()
                cat.game_data_key = 'LoopChampionData'
                cat.titles = ['Loopin\' Ramp Champ']
                cat.score_suffix_singular = ' Ramp'
                cat.score_suffix_plural = ' Ramps'
                cat.score_for_player = lambda player: player.player_stats['loops_completed']
                self.highscore_categories.append(cat)

                for category in self.highscore_categories:
                        category.load_from_game(self)


        def start_highscore_sequence(self):
                seq_manager = EntrySequenceManager(game=self, priority=150)
                seq_manager.ready_handler = self.highscore_entry_ready_to_prompt
                seq_manager.finished_handler = self.highscore_entry_finished

                seq_manager.logic = procgame.highscore.CategoryLogic(game=self, categories=self.highscore_categories)
                self.modes.add(seq_manager)

        def highscore_entry_ready_to_prompt(self, mode, prompt):
                #banner_mode = Billboard(game=self, priority=8)
                #banner_mode.show_text(text=('Great Score'.upper(), prompt.left.upper()), seconds=None)
                #self.modes.add(banner_mode)
                self.sound.stop_music()
                self.sound.play_music('hs_entry_music', loops=-1)
                self.sound.play_voice('well_done')

                bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/hs_entry_bgnd.dmd").frames[0])
                title_layer = dmd.TextLayer(128/2, 10, self.fonts['8x6'], "center", opaque=False).set_text("Great Score".upper(),color=dmd.CYAN)
                player_layer = dmd.TextLayer(128/2, 18, self.fonts['8x6'], "center", opaque=False).set_text(prompt.left.upper(),color=dmd.CYAN)
                # combine the parts together
                self.utility.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,title_layer,player_layer])

                self.utility.delay(delay=3, handler=lambda: self.highscore_banner_complete(mode=mode))


        def highscore_banner_complete(self, mode):
                self.utility.layer=None
                mode.prompt()


        def highscore_entry_finished(self, mode):
                self.modes.remove(mode)
                self.modes.add(self.match)

                #store high score on hs server
#                if self.user_settings['Network']['Store High Scores on Server']=='Yes':
#                    p = self.current_player()
#                    self.hs_server.store_score(self.last_entered_inits,p.score)


        def set_player_stats(self,id,value):
            p = self.current_player()
            p.player_stats[id]=value

        def get_player_stats(self,id):
            p = self.current_player()
            return p.player_stats[id]

        def reset(self):
                # Reset the entire game framework
                super(Game, self).reset()

                # Add the basic modes to the mode queue
                self.modes.add(self.ball_search)
                self.modes.add(self.utility)
                self.modes.add(self.effects)
                #self.modes.add(self.rgb_lamps)
                self.modes.add(self.ball_save)
                self.modes.add(self.ark)
                self.modes.add(self.temple)
                self.modes.add(self.swordsman)
                #self.modes.add(self.idol)
                #self.modes.add(self.mini_playfield)
                self.modes.add(self.trough)
                self.modes.add(self.tilt)
                self.modes.add(self.extra_ball)
                self.modes.add(self.screens)
                self.modes.add(self.volume)
                self.modes.add(self.attract_mode)

                # Make sure flippers are off, especially for user initiated resets.
                #TODO - TEMP Change to True for MPU testing, normally false
                #self.enable_flippers(enable=True)
                self.enable_flippers(enable=False)

                #temp addition -testing for Gerry
                #self.coils.swCol9Coil.pulse(0)
                #self.log.info('%s On',self.coils.swCol9Coil.label)


        # Empty callback just incase a ball drains into the trough before another
        # drain_callback can be installed by a gameplay mode.
        def drain_callback(self):
                pass


        def start_game(self,force_moonlight=False):
                super(Game, self).start_game()

                #update game start audits
                self.start_time = time.time()
                #audits.record_value(self,'gameStarted')
                if self.user_settings['Machine (Standard)']['Free Play'].startswith('N'):
                    credits =  audits.display(self,'general','creditsCounter')
                    audits.update_counter(self,'credits',credits-1)

                #moonlight check - from Eric P of CCC fame
                #-----------------------------------------
                # Check the time
                now = datetime.datetime.now()
                self.log.info("Hour:%s Minutes:%s",now.hour,now.minute)
                # subtract the window minutes from 60
                window = 60 - self.moonlight_minutes
                self.log.info("Moonlight window time:%s",window)
                # check for moonlight - always works at straight up midnight
                if now.hour == 0 and now.minute == 0:
                    self.moonlight_flag = True
                # If not exactly midnight - check to see if we're within the time window
                elif now.hour == 23 and now.minute >= window:
                    self.moonlight_flag = True
                # if force was passed - start it no matter what
                elif force_moonlight:
                    self.moonlight_flag = True
                else:
                    self.moonlight_flag = False

                self.log.info("Moonlight Flag:%s",self.moonlight_flag)
                #-----------------------------------------


#        def add_player(self):
#                super(Game, self).add_player()
#                audits.record_value(self,'gameStarted')


        def shoot_again(self):
            super(Game, self).shoot_again() #calls ball_starting

            self.base_game_mode.shoot_again()


        def ball_starting(self):
                super(Game, self).ball_starting()

                #check for moonlight
                if self.moonlight_flag and not self.get_player_stats('moonlight_status'):
                    self.modes.add(self.moonlight)
                #else add normal base mode
                else:
                    self.modes.add(self.base_game_mode)

        def ball_ended(self):
                self.modes.remove(self.base_game_mode)
                super(Game, self).ball_ended()

        def game_ended(self):
                super(Game, self).game_ended()

                #remove the base game mode
                self.modes.remove(self.base_game_mode)
                #disable the active ball search from now the game has ended
                self.ball_search.disable()

                #self.modes.add(self.match)
                #run the high score sequencer. Will run match automatically if no high scores to enter
                self.start_highscore_sequence()

                #record audits
                #-------------
                self.game_time = time.time()-self.start_time
                audits.record_value(self,'gameTime',self.game_time)

                #p = self.current_player()
                for p in self.players:
                    audits.record_value(self,'gamePlayed')
                    audits.record_value(self,'gameScore',p.score)
                #-------------

                #update diagnostics
                #--------------------
                self.update_diagnostics()
                #--------------------


        def update_diagnostics(self):
            if self.game_time:
                diagnostics.update_switches(self,self.game_time)
                self.switch_error_log = diagnostics.broken_switches(self)
            else:
                self.switch_error_log = diagnostics.broken_switches(self)

            self.log.debug('Switch Errors:%s',self.switch_error_log)


        def set_status(self, text):
                self.dmd.set_message(text, 3)
                print(text)

        def extra_ball_count(self):
                p = self.current_player()
                p.extra_balls += 1


        def setup_ball_search(self):
                # No special handlers in starter game.
                special_handler_modes = []
                self.ball_search = Ball_Search(self, priority=100, \
                                     countdown_time=12, coils=self.ballsearch_coils, \
                                     reset_switches=self.ballsearch_resetSwitches, \
                                     stop_switches=self.ballsearch_stopSwitches, \
                                     special_handler_modes=special_handler_modes) #procgame.modes.BallSearch



        def enable_flippers(self, enable):
                """Enables or disables the flippers AND bumpers."""
                self.party_mode = self.user_settings['Machine (Standard)']['Party Mode']
                #stern flippers
                for flipper in self.config['PRFlippers']:
                        self.logger.info("Programming Flipper %s", flipper)
                        #setup flipper coil naming
                        main_coil = self.coils[flipper+'Main']

                        #setup opposite flipper coil naming for party modes
                        oppflipper = ''
                        if flipper.endswith('R'):
                            oppflipper = flipper[:-1]+'L'
                        elif flipper.endswith('L'):
                            oppflipper = flipper[:-1]+'R'
                        opposite_coil = self.coils[oppflipper+'Main']

                        switch_num = self.switches[flipper].number

                        #activating flipper rules # patter timing 2 on, 18 off, now 2 on 24 off
                        drivers = []
                        if enable:
                                if self.party_mode=='No Hold':
                                    drivers += [pinproc.driver_state_pulse(main_coil.state(), main_coil.default_pulse_time)]
                                elif self.party_mode =='Double Flip':
                                    drivers += [pinproc.driver_state_patter(main_coil.state(), 2, 24, main_coil.default_pulse_time, True)]
                                    drivers += [pinproc.driver_state_patter(opposite_coil.state(), 2, 24, opposite_coil.default_pulse_time, True)]
                                elif self.party_mode=='Reversed':
                                    drivers += [pinproc.driver_state_patter(opposite_coil.state(), 2, 24, main_coil.default_pulse_time, True)]
                                else:
                                    drivers += [pinproc.driver_state_patter(main_coil.state(), 2, 24, main_coil.default_pulse_time, True)]
                                    #drivers += [pinproc.driver_state_patter(main_coil.state(), 2, 24, 35, True)]
                        else:
                             main_coil.disable()

                        self.proc.switch_update_rule(switch_num, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)

                        #deactivating flipper rules
                        drivers = []
                        #if enable:
                        if self.party_mode =='Double Flip':
                            drivers += [pinproc.driver_state_disable(main_coil.state())]
                            drivers += [pinproc.driver_state_disable(opposite_coil.state())]
                        elif self.party_mode=='Reversed':
                            drivers += [pinproc.driver_state_disable(opposite_coil.state())]
                        else:
                            drivers += [pinproc.driver_state_disable(main_coil.state())]

                        self.proc.switch_update_rule(switch_num, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)


                #bumpers
                self.enable_bumpers(enable)

        def drive_lamp(self, lamp_name, style='on'):
                if style == 'slow':
                        self.lamps[lamp_name].schedule(schedule=0x00ff00ff, cycle_seconds=0, now=True)
                elif style == 'medium':
                        self.lamps[lamp_name].schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
                elif style == 'fast':
                        self.lamps[lamp_name].schedule(schedule=0x55555555, cycle_seconds=0, now=True)
                elif style == 'superfast':
                        self.lamps[lamp_name].schedule(schedule=0x99999999, cycle_seconds=0, now=True)
                elif style == 'on':
                        self.lamps[lamp_name].enable()
                elif style == 'off':
                        self.lamps[lamp_name].disable()
                elif style == 'smarton':
                        self.lamps[lamp_name].schedule(schedule=0x88888888, cycle_seconds=0, now=True)
                        self.lamps[lamp_name].enable()
                        #self.mode.delay(name='lamp_on', event_type=None, delay=0.5, handler=self.lamps[lamp_name].enable)


        def boolean_format(self,value):
            if value.upper()=='YES':
                return True
            elif value.upper()=='NO':
                return False



def main():
        VAR_PATH='./var'
        if not os.path.exists(VAR_PATH):
            os.mkdir(VAR_PATH)

        LOG_PATH='./var/logs'
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

#        #setup console logging
#        from colorlogging import ColorizingStreamHandler
#        handler = ColorizingStreamHandler()
#        handler.setLevel(logging.INFO)
#        handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        #setup logging to file
        datetime = str(time.strftime("%Y-%m-%d %H-%M-%S"))
        file_handler = logging.FileHandler(game_path +'var/logs/'+serial+' Game Log '+datetime+'.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

 #       root_logger.addHandler(handler)
        root_logger.addHandler(file_handler)

        #set invidivual log levels here
        logging.getLogger('ij.ark').setLevel(logging.DEBUG)
        logging.getLogger('ij.swordsman').setLevel(logging.ERROR)
        logging.getLogger('ij.temple').setLevel(logging.ERROR)
        logging.getLogger('ij.ball_search').setLevel(logging.ERROR)
        logging.getLogger('ij.trough').setLevel(logging.DEBUG)
#        logging.getLogger('ij.base').setLevel(logging.DEBUG)
        logging.getLogger('ij.poa').setLevel(logging.DEBUG)
        logging.getLogger('ij.adventure').setLevel(logging.DEBUG)
        logging.getLogger('ij.mode_select').setLevel(logging.DEBUG)
#        logging.getLogger('ij.raven_bar').setLevel(logging.DEBUG)
#        logging.getLogger('ij.match').setLevel(logging.DEBUG)
#        logging.getLogger('ij.service').setLevel(logging.DEBUG)
#        logging.getLogger('ij.three_challenges').setLevel(logging.DEBUG)
        logging.getLogger('game.vdriver').setLevel(logging.ERROR)
        logging.getLogger('game.driver').setLevel(logging.ERROR)
        logging.getLogger('game.sound').setLevel(logging.ERROR)
        logging.getLogger('game').setLevel(logging.ERROR)
        logging.getLogger('mpu').setLevel(logging.INFO) #ERROR


        config = yaml.load(open(machine_config_path, 'r'))
        print("Using config at: %s "%(machine_config_path))
        machine_type = config['PRGame']['machineType']
        config = 0
        game = None
        try:
                game = Game(machine_type)
                game.yamlpath = machine_config_path
                game.setup()
                game.run_loop()

        except Exception as err:
                log = logging.getLogger()
                log.exception('We are stopping here!:')

        finally:
                del game



if __name__ == '__main__': main()
