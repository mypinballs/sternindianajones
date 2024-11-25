# Attract Mode

import procgame
import locale
import logging
import audits
import time
import ep
from procgame import *
from random import *
from service import *
from time import strftime


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Attract(game.Mode):
        """docstring for AttractMode"""
        def __init__(self, game):
                super(Attract, self).__init__(game, 1)
                self.log = logging.getLogger('ij.attract')
                self.display_order = [0,1,2,3,4,5,6,7,8,9]
                self.display_index = 0

                #setup attract sounds for flipper presses
                self.game.sound.register_sound('flipperAttract', sound_path+'burp.aiff')
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402CC_bellak.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402CD_bellaks_staff_is_too_long.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402D2_he_was_good.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402CF_dont_look_marrion.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402D4_blow_up_the_ark.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402D5_kill_you_right_now.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402D6_only_say_sorry_so_many_times.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402D7_making_this_up_as_i_go.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402DE_start_the_engines_chuck.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402F2_trust_me.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij402FF_show_alittle_backbone.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij40314_fortune_and_glory_kid.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij4030D_you_know_perfectly_well.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij4030E_you_look_lost.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij4030F_welcome_to_pamcot_palace.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij4033B_ha_ha_very_funny.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij40318_not_leaving_here_without_stones.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij40320_my_name_is_indiana_jones.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij40327_call_it_the_jungle.aiff")
                self.game.sound.register_sound('flipperAttract', speech_path+"ij40330_never_happen_again.aiff")


                self.sound_timestamp = time.time()

                #setup coin switches
                self.coin_switchnames=[]
                for switch in self.game.switches.items_tagged('coin'):
                    self.coin_switchnames.append(switch.name)
                    self.log.info("Coin Switch is:"+switch.name)

                for switch in self.coin_switchnames:
                        self.add_switch_handler(name=switch, event_type='active', \
                                delay=None, handler=self.coin_switch_handler)

                #setup lamp sets
                self.film_mode_lamps = ['getTheIdol','streetsOfCairo','wellOfSouls','ravenBar','monkeyBrains','stealTheStones','mineCart','ropeBridge','castleBrunwald','tankChase','theThreeChallenges','chooseWisely','warehouseRaid','nukeTest','returnTheSkull','jonesVsAliens']
                self.jackpot_lamps = ['arkJackpot','stonesJackpot','grailJackpot','skullJackpot']
                self.skillshot_lamps = ['skillIndy','skillSwordsman','skillMystery','skillJets']
                self.indy_lamps = ['indyI','indyN','indyD','indyY']
                self.jones_lamps = ['jonesJ','jonesO','jonesN','jonesE','jonesS']
                self.arrow_lamps = ['crusadeArrow','leftLoopArrow','templeArrow','raidersArrow','rightRampArrow','rightLoopArrow']
                self.film_lamps = ['lastCrusade','templeOfDoom','raiders','kingdom']
                self.map_lamps = ['mapM','mapA','mapP']
                self.misc_lamps = ['leftSpecial','leftSpinner','cairoSwordsman','xMarksTheSpot','8Ball','rightSpinner','liteMystery','rightSpecial']

        def mode_topmost(self):
                pass


        def mode_started(self):

                # Blink the start button to notify player about starting a game.
                self.update_start_lamp()

                # Turn on GI lamps
                #self.delay(name='gi_on_delay', event_type=None, delay=0, handler=self.gi)
                #self.log.info("attract mode after gi turn on")

                # run feature lamp patterns
                self.lamp_show_set=True
                self.change_lampshow()
                #self.standard_lampshow()

                #clear any leftover tilts
                if self.game.tilt.get_status()==1:
                    self.game.tilt.reset()

                #debug subway release issues
                #self.game.coils.subwayRelease.pulse(100)

                #check for stuck balls
                #self.delay(name='idol_empty_delay', event_type=None, delay=2, handler=self.init_idol)
                self.delay(name='stuck_balls_release_delay', event_type=None, delay=2, handler=self.game.utility.release_stuck_balls)
                self.delay(name='map_room_check_delay', event_type=None, delay=2, handler=self.game.utility.check_map_room)


                #reset mini playfield code

                #create dmd attract screens
                self.mypinballs_logo = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/mypinballs_logo.dmd').frames[0])
                self.mypinballs_logo.transition = dmd.ExpandTransition(direction='horizontal')

                #self.williams_logo = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/williams_animated.dmd').frames[0])
                self.williams_logo = dmd.AnimatedLayer(frames=dmd.Animation().load(game_path+'dmd/williams_animated.dmd').frames,frame_time=1,hold=True)
                #self.williams_logo.transition = dmd.ExpandTransition(direction='vertical')

                self.indy_logo = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/indy_logo.dmd').frames[0])
                self.indy_logo.transition = dmd.ExpandTransition(direction='vertical')

                #self.game_over_layer = dmd.TextLayer(128/2, 10, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text("GAME OVER")
                self.game_over_layer = dmd.TextLayer(128/2, 10, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text("GAME OVER",color=dmd.ORANGE)
                self.game_over_layer.transition = dmd.ExpandTransition(direction='horizontal')#dmd.CrossFadeTransition(width=128,height=32)

                self.scores_layer = dmd.TextLayer(128/2, 11, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text("HIGH SCORES",color=dmd.BROWN)
                self.scores_layer.transition = dmd.PushTransition(direction='west')

                #setup date & time info
                self.day_layer = dmd.DateLayer(128/2, 5, self.game.fonts['tiny7'],"day", "center", opaque=False, colour=dmd.ORANGE)
                self.date_layer = dmd.DateLayer(128/2, 13, self.game.fonts['tiny7'],"date", "center", opaque=False, colour=dmd.YELLOW)
                self.time_layer = dmd.DateLayer(128/2, 21, self.game.fonts['tiny7'],"time", "center", opaque=False, colour=dmd.BROWN)
                self.date_time_layer = dmd.GroupedLayer(128, 32, [self.day_layer,self.date_layer,self.time_layer])
                self.date_time_layer.transition = dmd.PushTransition(direction='west')

                #update the pricing
                self.update_pricing()

                #still cant believe i'm adding this :(
                self.lyman_tribute()

                #run attract dmd screens
                self.attract_display()

                #fadeout music (if any running)
                self.delay(name='music_fadeout_delay', event_type=None, delay=10, handler=lambda:self.game.sound.fadeout_music(3000))

                #temp gi test
                self.gi_flutter()

                #open the swordsman for attract
                self.game.swordsman.open_when_init()

                #TODO:TEMP - remove
                #self.game.coils.grailEject.pulse()


#        def gi(self):
#            self.game.lamps.gi01.pulse(0)
#            self.game.lamps.gi02.pulse(0)
#            self.game.lamps.gi03.pulse(0)
#            self.game.lamps.gi04.pulse(0)

        def gi_flutter(self):
            self.log.info("GI FLUTTER")
            self.game.lamps.playfieldGI.schedule(0x000C0F0F,cycle_seconds=1)
#
#        def gi_off(self):
#            self.game.lamps.gi01.disable()
#            self.game.lamps.gi02.disable()
#            self.game.lamps.gi03.disable()
#            self.game.lamps.gi04.disable()

        def init_idol(self):
            if not self.game.trough.is_full():
                self.game.idol.empty()
            else:
                self.game.idol.home()


        def change_lampshow(self):
                delay=25
                shuffle(self.game.lampshow_keys)

                self.game.lampctrl.stop_show()
                self.game.lampctrl.play_show(self.game.lampshow_keys[0], repeat=False, callback=self.standard_lampshow)

                #turn gi on or off depending on lampshow chosen from shuffle
#                if self.game.lampshow_keys[0].find('flasher',0)>0:
#                    self.gi_off()
#                else:  
#                    self.gi()

                self.delay(name='lampshow', event_type=None, delay=delay, handler=self.change_lampshow)


        # def standard_lampshow(self, enable=True):
                #flash all lamps in groups of 8 ordered by columns
                #schedules = [0xffff0000, 0xfff0000f, 0xff0000ff, 0xf0000fff, 0x0000ffff, 0x000ffff0, 0x00ffff00, 0x0ffff000]
                # schedules = [0xcccccccc, 0x66666666, 0x33333333, 0x99999999]
                # for index, lamp in enumerate(sorted(self.game.lamps, key=lambda lamp: lamp.number)):
                    # if lamp.yaml_number.startswith('L') and lamp.name.find('Button')<0:
                        # if enable:
                                # sched = schedules[index%len(schedules)]
                                # lamp.schedule(schedule=sched, cycle_seconds=0, now=False)
                        # else:
                                # lamp.disable()

        def standard_lampshow(self,enable=True):
            lamp_sets =  [self.film_mode_lamps,self.jackpot_lamps,self.skillshot_lamps,self.indy_lamps,self.jones_lamps,self.arrow_lamps,self.film_lamps,self.map_lamps,self.misc_lamps]

            schedules = [0xffff0000, 0xfff0000f, 0xff0000ff, 0xf0000fff, 0x0000ffff, 0x000ffff0, 0x00ffff00, 0x0ffff000]
            for set in lamp_sets:    
                for index, lamp in enumerate(set):
                    if enable:
                        sched = schedules[index%len(schedules)]
                        self.game.lamps[lamp].schedule(schedule=sched, cycle_seconds=0, now=False)
                    else:
                        self.game.lamps[lamp].disable()


        def update_start_lamp(self):
            if audits.display(self.game,'general','creditsCounter') >0 or self.game.user_settings['Machine (Standard)']['Free Play'].startswith('Y'):
                # Blink the start button to notify player about starting a game.
                self.game.lamps.startButton.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=False)
            else:
                self.game.lamps.startButton.disable()


        def update_pricing(self):
            self.pricing_top = ''
            self.pricing_bottom = ''

            if self.game.user_settings['Machine (Standard)']['Free Play'].startswith('Y'):
                self.pricing_top='FREE PLAY'
            else:
                self.pricing_top=str(audits.display(self.game,'general','creditsCounter')+" CREDITS")

            if audits.display(self.game,'general','creditsCounter') >0 or self.game.user_settings['Machine (Standard)']['Free Play'].startswith('Y'):
                self.pricing_bottom = 'PRESS START'
            else:
                self.pricing_bottom = 'INSERT COINS'

            self.coins_top_layer = dmd.TextLayer(128/2, 6, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text(self.pricing_top,color=dmd.BROWN)
            #self.coins_top_layer.transition = dmd.PushTransition(direction='north')
            self.coins_bottom_layer = dmd.TextLayer(128/2, 18, self.game.fonts['num_09Bx7'], "center", opaque=False).set_text(self.pricing_bottom,color=dmd.GREEN)
            #self.coins_bottom_layer.transition = dmd.PushTransition(direction='south')

            self.coins_layer = dmd.GroupedLayer(128, 32, [self.coins_top_layer, self.coins_bottom_layer])


        def show_pricing(self):
            self.update_pricing()
            self.layer = self.coins_layer

        def lyman_tribute(self):
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
            title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text("CODE CHAMPION",color=dmd.CYAN)
            initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text("LYMAN",color=dmd.WHITE)
            infoLine1 = dmd.TextLayer(64, 17, self.game.fonts['4px_az'], "center", opaque=False).set_text("Inspiration. Genius. Legend.",color=dmd.ORANGE)
            infoLine2 = dmd.TextLayer(64, 23, self.game.fonts['4px_az'], "center", opaque=False).set_text("Thanks for the games x".upper(),color=dmd.ORANGE)
            self.lyman_tribute_layer = dmd.GroupedLayer(128,32,[bgnd_layer,initsLine,infoLine1,infoLine2,title])
            self.lyman_tribute_layer.transition = dmd.PushTransition(direction='south')



        def create_high_scores(self,script):
            # Read the categories
            for category in self.game.highscore_categories:
                title = None # just pre-sets to make the IDE happy
                initLine1 = None
                scoreLine1 = None


                for index, score in enumerate(category.scores):
                    score_str = locale.format("%d", score.score, True) # Add commas to the score.

                    ## For the standard high scores
                    if category.game_data_key == 'ClassicHighScoreData':
                        ## score 1 is the grand champion, gets its own frame
                        if index == 0:
                            # this is the new style for the 12 init max

                            title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text("Grand Champion".upper(),color=dmd.YELLOW)
                            initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(score.inits,color=dmd.GREEN)
                            scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10x7_bold'], "center", opaque=False).set_text(score_str)
                            # combine the parts together
                            combined = dmd.GroupedLayer(128, 32, [title, initsLine, scoreLine])
                            combined.transition = dmd.PushTransition(direction='west')
                            # add it to the stack
                            script.append({'seconds':6.0, 'layer':combined})

                             # this section handles scores 2 through 5 (high scores 1 through 4)
                        else:

                            title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text("Highest Scores".upper(),color=dmd.ORANGE)
                            initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(str(index) + ") " + score.inits,color=dmd.YELLOW)
                            scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10x7_bold'], "center", opaque=False).set_text(score_str,color=dmd.BROWN)
                            combined = dmd.GroupedLayer(128, 32, [title, initsLine, scoreLine])
                            combined.transition = dmd.PushTransition(direction='west')
                            # add it to the stack
                            script.append({'seconds':4.0, 'layer':combined})

                    # generate screens for Treasure Champion
                    if category.game_data_key == 'TreasureChampionData':
                        bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
                        title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text(category.titles[0].upper(),color=dmd.DARK_BROWN)
                        initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(score.inits,color=dmd.YELLOW)
                        scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10px_az'], "center", opaque=False).set_text(score_str+" "+category.score_suffix_plural.upper() ,color=dmd.GREY)
                        combined = dmd.GroupedLayer(128,32,[bgnd_layer,initsLine,scoreLine,title])
                        combined.transition = dmd.PushTransition(direction='west')
                        # add it to the stack
                        script.append({'seconds':5.0, 'layer':combined})

                    # generate screens for POA Champion
                    if category.game_data_key == 'POAChampionData':
                        bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
                        title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text(category.titles[0].upper(),color=dmd.DARK_BROWN)
                        initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(score.inits,color=dmd.YELLOW)
                        scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10px_az'], "center", opaque=False).set_text(score_str+" "+category.score_suffix_plural.upper(),color=dmd.GREY)
                        combined = dmd.GroupedLayer(128,32,[bgnd_layer,initsLine,scoreLine,title])
                        combined.transition = dmd.PushTransition(direction='west')
                        # add it to the stack
                        script.append({'seconds':5.0, 'layer':combined})

                    # generate screens for Loop Champion
                    if category.game_data_key == 'LoopChampionData':
                        bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
                        title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text(category.titles[0].upper(),color=dmd.DARK_BROWN)
                        initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(score.inits,color=dmd.YELLOW)
                        scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10px_az'], "center", opaque=False).set_text(score_str+" "+category.score_suffix_plural.upper(),color=dmd.GREY)
                        combined = dmd.GroupedLayer(128,32,[bgnd_layer,initsLine,scoreLine,title])
                        combined.transition = dmd.PushTransition(direction='west')
                        # add it to the stack
                        script.append({'seconds':5.0, 'layer':combined})


        def attract_display(self):
                script = list()

                script.append({'seconds':5.0, 'layer':self.mypinballs_logo})
                script.append({'seconds':7.0, 'layer':self.williams_logo})
                script.append({'seconds':3.0, 'layer':self.indy_logo})
                script.append({'seconds':3.0, 'layer':self.coins_layer})
                #script.append({'seconds':20.0, 'layer':self.credits_layer})
                script.append({'seconds':3.0, 'layer':None})

                #script.append({'seconds':3.0, 'layer':self.scores_layer})
#                for frame in highscore.generate_highscore_frames(self.game.highscore_categories):
#                    new_layer = dmd.FrameLayer(frame=frame)
#                    new_layer.transition = dmd.PushTransition(direction='west')
#                    script.append({'seconds':2.0, 'layer':new_layer})

                self.create_high_scores(script)

                script.append({'seconds':4.0, 'layer':self.lyman_tribute_layer})

                if self.game.user_settings['Machine (Standard)']['Show Date and Time'].startswith('Y'):
                    script.append({'seconds':10.0, 'layer':self.date_time_layer})

                #add in the game over screen
                index=3
                time=3
                if self.game.system_status=='game_over':
                    index=0
                    time=10
                    self.game.system_status='attract'

                script.insert(index,{'seconds':time, 'layer':self.game_over_layer})

                self.layer = dmd.ScriptedLayer(width=128, height=32, script=script)
                #self.layer = dmd.ScriptedLayer(128, 32, [{'seconds':10.0, 'layer':self.mypinballs_logo}, {'seconds':2.0, 'layer':self.press_start}, {'seconds':2.0, 'layer':None}])
                #self.game.set_status("V1.0")



        def mode_stopped(self):
                self.game.lampctrl.stop_show()
                #close the swordsman
                self.game.swordsman.close()



        def mode_tick(self):
                pass


        def sound_effects(self):
             if time.time()-self.sound_timestamp>5:
                self.game.sound.play_voice('flipperAttract')
                self.sound_timestamp=time.time()


        # Enter service mode when the enter button is pushed.
        def sw_enter_active(self, sw):
                self.game.modes.remove(self.game.coin_door)
                self.game.lampctrl.stop_show()
                self.cancel_delayed('lampshow')
                for lamp in self.game.lamps:
                        lamp.disable()
                self.game.modes.add(self.game.service_mode)
                return True

        def sw_exit_active(self, sw):
                return True

        #coin door mode control
        #def sw_coinDoorClosed_inactive(self, sw):
        def sw_statusInterlock50v_active_for_500ms(self, sw):
                if not self.game.modes.__contains__(self.game.coin_door):
                    self.game.modes.add(self.game.coin_door)


        # Outside of the service mode, up/down control audio volume.
        #def sw_down_active(self, sw):
                #volume = int(self.game.sound.volume_down())
                #self.game.set_status("Volume Down : " + str(volume*10)+"%")
                #return True

        #def sw_up_active(self, sw):
                #volume = int(self.game.sound.volume_up())
                #self.game.set_status("Volume Up : " + str(volume*10)+"%")
                #return True



        # Start button starts a game if the trough is full.  Otherwise it
        # initiates a ball search.
        # This is probably a good place to add logic to detect completely lost balls.
        # Perhaps if the trough isn't full after a few ball search attempts, it logs a ball
        # as lost?
        def sw_startButton_active(self, sw):
                if self.game.trough.is_full():
                        # Remove attract mode from mode queue - Necessary?
                        self.game.modes.remove(self)
                        # Initialize game
                        if self.game.switches.flipperLwR.is_active(0.5):
                            self.game.start_game(force_moonlight=True)
                        else:
                            self.game.start_game(force_moonlight=False)
                        # Add the first player
                        self.game.add_player()
                        # Start the ball.  This includes ejecting a ball from the trough.
                        self.game.start_ball()
                else:

                        #self.game.set_status("Ball Search!")
                        self.game.ball_search.perform_search()
                return True

        def coin_switch_handler(self, sw):
            self.credits =  audits.display(self.game,'general','creditsCounter')
            audits.update_counter(self.game,'credits',self.credits+1)
            self.show_pricing()
            self.game.sound.play("coin")
            self.update_start_lamp()


        def sw_flipperLwL_active(self, sw):
                self.sound_effects()

        def sw_flipperLwR_active(self, sw):
                self.sound_effects()
