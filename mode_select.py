# Mode Select

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import random
import logging
import audits

from procgame import *
from get_the_idol import *
from streets_of_cairo import *
from well_of_souls import *
from monkey_brains import *
from steal_the_stones import *
from minecart import *
from rope_bridge import *
from castle_grunwald import *
from tank_chase import *
from the_three_challenges import *
from choose_wisely import *
from werewolf import *
from raven_bar import *
from warehouse_raid import *
from jones_vs_aliens import *
from ringmaster import *
from final_adventure import *


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Mode_Select(game.Mode):

	def __init__(self, game, priority):
            super(Mode_Select, self).__init__(game, priority)
            self.log = logging.getLogger('ij.mode_select')

            self.name_layer = dmd.TextLayer(128/2, 6, self.game.fonts['num_09Bx7'], "center")
            self.info_layer = dmd.TextLayer(128/2, 16, self.game.fonts['07x5'], "center")
            self.info2_layer = dmd.TextLayer(128/2, 22, self.game.fonts['07x5'], "center")

            #setup sound
            self.game.sound.register_sound('scene_started', sound_path+'mode_started.aiff')
            self.game.sound.register_sound('scene_ended', sound_path+'mode_ended.aiff')

            self.lamp_list = ['getTheIdol','streetsOfCairo','wellOfSouls','ravenBar','monkeyBrains','stealTheStones','mineCart','ropeBridge','castleGrunwald','tankChase','theThreeChallenges','chooseWisely','warehouseRaid','jonesVsAliens','kingdom3']
           
            #default mode bonus value
            self.mode_bonus_value = int(self.game.user_settings['Gameplay (Feature)']['Mode Bonus Value (Mil)'])*1000000 #2000000
            self.mode_start_value = int(self.game.user_settings['Gameplay (Feature)']['Mode Start Value (Mil)'])*1000000 #5000000
            
            #default timer value
            self.timer=30
            self.pause_length = self.game.user_settings['Gameplay (Feature)']['Mode Timers Pause Length']
            
            #setup game modes
            self.get_the_idol = Get_The_Idol(self.game, 80,self)
            self.streets_of_cairo = Streets_Of_Cairo(self.game, 81,self)
            self.well_of_souls = Well_Of_Souls(self.game, 82,self)
            self.raven_bar = Raven_Bar(self.game, 83,self)
            self.werewolf = Werewolf(self.game, 83,self)
            self.monkey_brains = Monkey_Brains(self.game, 84,self)
            self.steal_the_stones = Steal_The_Stones(self.game, 85,self)
            self.mine_cart = Minecart(self.game, 86,self)
            self.rope_bridge = Rope_Bridge(self.game, 87,self)
            self.castle_grunwald = Castle_Grunwald(self.game, 88,self)
            self.tank_chase = Tank_Chase(self.game, 89,self)
            self.the_three_challenges = The_Three_Challenges(self.game, 90,self)
            self.choose_wisely = Choose_Wisely(self.game, 91,self)
            self.warehouse_raid = Warehouse_Raid(self.game, 92,self)
            self.jones_vs_aliens = Jones_Vs_Aliens(self.game, 93,self)
            self.ringmaster = Ringmaster(self.game, 94,self)
            self.final_adventure = Final_Adventure(self.game,150)
            
             #setup the switches which pause an active mode
            self.mode_pausing_switchnames = []
            for switch in self.game.switches.items_tagged('mode_pause'):
                    self.mode_pausing_switchnames.append(switch.name)
                    self.log.info("Mode Pausing Switch is:"+switch.name)


        def reset(self):
            self.choice_id =0
            #setup flags
            self.mode_starting = False
            self.mode_running = False
            self.secret_mode = False
            self.all_scenes_complete = False
            
            #setup mode enabled flag from game settings
            if self.game.user_settings['Gameplay (Feature)']['Mode Start Lit']!='Off':
                self.mode_enabled = True
            else:
                self.mode_enabled = False
                
            self.total_score = 0
            self.timer_layer = None
            
            self.name_text =''
            self.info_text =''
            self.info2_text =''
            
            #reset lamps
            self.reset_lamps()
            

        def reset_lamps(self):
            #loop round and turn off all lamps
            for i in range(len(self.lamp_list)):
                self.game.effects.drive_lamp(self.lamp_list[i],'off')

            self.mode_start_lamp(self.mode_enabled)
            
            
        def reset_scenes(self):
            #clear completed scenes
            self.select_list= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            self.game.set_player_stats('mode_status_tracking',self.select_list)
            self.all_scenes_complete = False
            
            #setup new scene
            self.unplayed_scenes()
            self.mode_enabled=True


        def mode_start_lamp(self,flag):
            lamp_name ='grail'
            if flag:
                self.game.effects.drive_lamp(lamp_name,'medium')
            else:
                self.game.effects.drive_lamp(lamp_name,'off')
                
            if self.all_scenes_complete:
                self.game.effects.drive_lamp(lamp_name,'fast')


        def mode_started(self):
            self.log.info("Main Mode Select Started")
            
            self.reset()
            
            self.game.set_player_stats('mode_enabled',self.mode_enabled)
            
            #setup pause switch handlers
            for switch in self.mode_pausing_switchnames:
		self.add_switch_handler(name=switch, event_type='active', delay=None, handler=self.mode_paused)  
                                
            #load player stats
            self.current_mode_num = self.game.get_player_stats('current_mode_num')
            self.select_list = self.game.get_player_stats('mode_status_tracking')

            #reset bonus mode tracking at ball start - no carry over
            self.game.set_player_stats('bonus_mode_tracking',[])
            
            #setup scene list
            self.unplayed_scenes()

        def mode_tick(self):
            pass

        def mode_stopped(self):
            #cancel timers
            self.cancel_delayed('scene_timeout')

            #clean up any running modes
            if self.mode_running:
                #remove the active scene
                self.remove_selected_scene()
                #call the common end scene code
                self.end_scene_common(0.1)
                
            #update player stats
            self.game.set_player_stats('current_mode_num',self.current_mode_num)
            self.game.set_player_stats('mode_status_tracking',self.select_list)


        def mode_paused(self,sw=None):
            if self.mode_running:
                self.timer_layer = None #clear time_layer reference first as not all modes use this
                if self.current_mode_num==0:
                    self.timer_layer = self.get_the_idol.timer_layer
                elif self.current_mode_num==1:
                    self.timer_layer = self.streets_of_cairo.timer_layer
                elif self.current_mode_num==4:
                    self.timer_layer = self.monkey_brains.timer_layer
                elif self.current_mode_num==5:
                    self.timer_layer = self.steal_the_stones.timer_layer
                elif self.current_mode_num==7:
                    self.timer_layer = self.rope_bridge.timer_layer
                elif self.current_mode_num==8:
                    self.timer_layer = self.castle_grunwald.timer_layer
                elif self.current_mode_num==9:
                    self.timer_layer = self.tank_chase.timer_layer
                elif self.current_mode_num==10:
                    self.timer_layer = self.the_three_challenges.timer_layer
                elif self.current_mode_num==13:
                    self.timer_layer = self.jones_vs_aliens.timer_layer
                elif self.current_mode_num==14:
                    self.timer_layer = self.ringmaster.timer_layer
                
                if self.timer_layer !=None:
                    self.timer_layer.pause(True)
                    self.cancel_delayed('scene_timeout')
                    self.cancel_delayed('scene_unpause')
                    if sw !=None:
                        self.delay(name='scene_unpause', delay=self.pause_length,handler=self.mode_unpaused)
                    
                    self.game.set_player_stats('mode_paused',True)
            
            
        def mode_unpaused(self):
            if self.mode_running and self.timer_layer !=None:
                self.timer_layer.pause(False) 
                self.cancel_delayed('scene_timeout')
                self.delay(name='scene_timeout', event_type=None, delay=self.timer_layer.get_time_remaining(), handler=self.end_scene)
                self.game.set_player_stats('mode_paused',False)
        
        
        def update_lamps(self):
            self.log.debug("Updating Mode Lamps")

            #current mode
            self.game.effects.drive_lamp(self.lamp_list[self.current_mode_num],'medium')

            #completed modes
            for i in range(len(self.lamp_list)):
                if self.select_list[i]==1:
                    self.game.effects.drive_lamp(self.lamp_list[i],'on')

            #mode start
            self.mode_start_lamp(self.mode_enabled)


        def unplayed_scenes(self,dirn=None):

            #turn off current mode lamp
            self.game.drive_lamp(self.lamp_list[self.current_mode_num],'off')

            #create list of unplayed scene numbers
            choice_list=[]
            for i in range(len(self.lamp_list)):
                if self.select_list[i]==0:
                    choice_list.append(i)
           
            if len(choice_list)>0:
               
                #adjust choice number
                if dirn=='left':
                    self.choice_id -=1
                elif dirn=='right':
                    self.choice_id +=1
                else:
                    self.choice_id = random.randint(0, len(choice_list)-1)

                #create wrap around
                if self.choice_id>len(choice_list)-1:
                    self.choice_id=0
                elif self.choice_id<0:
                    self.choice_id=len(choice_list)-1

                #set new mode number
                self.current_mode_num = choice_list[self.choice_id]

                self.log.debug("mode now active:"+str(self.lamp_list[self.current_mode_num]))
            else:
                self.all_scenes_complete = True
                self.mode_enabled = False
                self.game.effects.drive_flasher('flasherCrusade',style='super',time=0)
            
            #update lamps
            self.update_lamps()


        def move_left(self):
            
            self.unplayed_scenes('left')

            #self.game.coils.flasherLeftRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            #self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherLeftRamp.disable)


        def move_right(self):
            
            self.unplayed_scenes('right')

            self.game.coils.flasherRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherRamp.disable)


        def eject_ball(self):
            timer=1
            self.game.effects.drive_flasher('flasherCrusade',style='fast',time=timer-0.1)
            self.delay(name='eject_kick_delay',delay=timer,handler=self.eject_kick)
            
            
        def eject_kick(self):
            self.game.effects.drive_flasher('flasherCrusade',style='super',time=0.2)
            self.game.lampctrl.play_show('mode_start_eject', repeat=False,callback=self.game.update_lamps)
            self.game.coils.grailEject.pulse()
            #reset the temple ball count
            self.game.temple.balls=0
            
            #continue any active mode timers paused by this or other entries to the scoops (ball lock etc)
            #once mode is under way
            if not self.mode_starting:
                self.mode_unpaused()
            else:
                self.mode_starting = False
                self.game.set_player_stats('mode_starting',self.mode_starting)
     

        def start_scene(self):
            if self.mode_enabled and self.game.get_player_stats('multiball_started')==False and self.game.get_player_stats('quick_multiball_running')==False and self.game.get_player_stats('lock_in_progress')==False and self.game.get_player_stats('dog_fight_running')==False:
                
                self.name_text =''
                self.info_text =''
                self.info2_text =''
            
                #play sound
                self.game.sound.play("scene_started")

                if self.current_mode_num==0:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Get The Idol Timer']
                    self.name_text = 'GET THE IDOL'
                    self.info_text = 'HIT TEMPLE'
                    self.info2_text = 'CAPTIVE BALL'

                elif self.current_mode_num==1:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Streets Of Cairo Timer']
                    self.name_text = 'STREETS OF CAIRO'
                    self.info_text = 'SHOOT LIT SHOTS'
                    self.info2_text = 'TO FIND MARION'

                elif self.current_mode_num==2:
                    self.name_text = 'WELL OF SOULS'
                    self.info_text = 'SHOOT CENTER HOLE'

                elif self.current_mode_num==3:
                    if self.secret_mode:
                        self.name_text = 'Werewolf Attack!'.upper()
                        self.info_text = 'Secret Video Mode'.upper()
                    else:
                        self.name_text = 'RAVEN BAR'
                        self.info_text = 'VIDEO MODE'

                elif self.current_mode_num==4:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Monkey Brains Timer']
                    self.name_text = 'MONKEY BRAINS'
                    self.info_text = 'SHOOT LIT SHOTS'

                elif self.current_mode_num==5:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Steal The Stones Timer']
                    self.name_text = 'STEAL THE STONES'
                    self.info_text = 'SHOOT RAMP THEN'
                    self.info2_text = 'JONES TARGETS'
                    
                elif self.current_mode_num==6:
                    self.name_text = 'MINE CART'
                    self.info_text = 'VIDEO MODE'

                elif self.current_mode_num==7:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Rope Bridge Timer']
                    self.name_text = 'ROPE BRIDGE'
                    self.info_text = 'SHOOT RAMPS'
                    self.info2_text = 'TO CROSS ROPE BRIDGE'

                elif self.current_mode_num==8:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Castle Brunwald Timer']
                    self.name_text = 'CASTLE BRUNWALD'
                    self.info_text = 'HIT UPPER CAPTIVE BALL'
                    self.info2_text = 'TO ESCAPE CASTLE'

                elif self.current_mode_num==9:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Tank Chase Timer']
                    self.name_text = 'TANK CHASE'
                    self.info_text = 'SHOOT LOOPS'
                    self.info2_text = 'TO DESTROY TANK'

                elif self.current_mode_num==10:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['The 3 Challenges Timer']
                    self.name_text = '3 CHALLENGES'
                    self.info_text = 'SHOOT MOVING SHOTS'
                    self.info2_text = 'TO PASS'

                elif self.current_mode_num==11:
                    self.name_text = 'CHOOSE WISELY'
                    self.info_text = 'VIDEO MODE'
                
                elif self.current_mode_num==12:
                    self.name_text = 'WAREHOUSE RAID'
                    self.info_text = 'LOCK BALLS ON RAMP'
                    self.info2_text = 'TO FIND ITEMS'
                
                elif self.current_mode_num==13:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Jones Vs Aliens Timer']
                    self.name_text = 'JONES VS ALIENS'
                    self.info_text = 'DESTROY SHIPS'
                    self.info2_text = 'TO SAVE EARTH'
                
                elif self.current_mode_num==14:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Ringmaster Timer']
                    self.name_text = 'RINGMASTER'
                    self.info_text = 'BATLLE RINGMASTER'
                    self.info2_text = 'TO SAVE EARTH'
                
                self.mode_starting = True
                self.game.set_player_stats('mode_starting',self.mode_starting)
                
                #pause and queue the contiuning adventure whilst we run a scene mode
                if self.game.get_player_stats('adventure_continuing'):
                    self.game.base_game_mode.poa.adventure_queue(True)

                anim = dmd.Animation().load(game_path+"dmd/start_scene.dmd")
                self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=4)
                
                self.animation_layer.add_frame_listener(-1,self.mode_text)

                self.ssd_count=0#temp fix for frame_listener multi call with held
                self.animation_layer.add_frame_listener(-1,self.scene_start_delay)
                

                self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.name_layer,self.info_layer,self.info2_layer])

                #update mode flags and player stats
                self.mode_enabled=False
                self.game.set_player_stats('mode_enabled',self.mode_enabled)

                #update lamp for mode start
                self.mode_start_lamp(self.mode_enabled)
                
                
                #score
                self.game.score(self.mode_start_value)
                
            elif self.mode_running and self.game.get_player_stats('multiball_started')==False and self.game.get_player_stats('quick_multiball_running')==False and self.game.get_player_stats('lock_in_progress')==False and self.game.get_player_stats('dog_fight_running')==False  and self.game.get_player_stats('multiball_mode_started')== False:
                self.mode_bonus()
            else:
                timer = 0
                #lengthen the timer if these events are running
                if self.game.get_player_stats('multiball_started')  or self.game.get_player_stats('quick_multiball_running') or self.game.get_player_stats('lock_in_progress'):
                    timer =2
                    
                if self.game.get_player_stats('multiball_mode_started'):
                    timer =1
                    
                #hold a ball for while multiball running for multiple jackpots use
                if self.game.get_player_stats('multiball_running'): 
                    timer = 10
                    if self.game.temple.balls==self.game.trough.num_balls_in_play: #dont hold if all balls are in temple subway
                        timer=0
                        
                #check for scene completetion and therefore start final adventure
                if self.all_scenes_complete and not self.game.get_player_stats('final_adventure_started'):
                    self.start_final_adventure()
                    
                self.delay(name='eject_delay', event_type=None, delay=timer, handler=self.eject_ball)
                
                

        def add_selected_scene(self):

            self.log.debug("Adding Movie Scene Mode"+str(self.current_mode_num))
            if self.current_mode_num==0:
                self.game.modes.add(self.get_the_idol)
            elif self.current_mode_num==1:
                self.game.modes.add(self.streets_of_cairo)
            elif self.current_mode_num==2:
                self.game.modes.add(self.well_of_souls)
            elif self.current_mode_num==3:
                if self.secret_mode:
                    self.game.modes.add(self.werewolf)
                else:
                    self.game.modes.add(self.raven_bar)
            elif self.current_mode_num==4:
                self.game.modes.add(self.monkey_brains)
            elif self.current_mode_num==5:
                self.game.modes.add(self.steal_the_stones)
            elif self.current_mode_num==6:
                self.game.modes.add(self.mine_cart)
            elif self.current_mode_num==7:
                self.game.modes.add(self.rope_bridge)
            elif self.current_mode_num==8:
                self.game.modes.add(self.castle_grunwald)
            elif self.current_mode_num==9:
                self.game.modes.add(self.tank_chase)
            elif self.current_mode_num==10:
                self.game.modes.add(self.the_three_challenges)
            elif self.current_mode_num==11:
                self.game.modes.add(self.choose_wisely)
            elif self.current_mode_num==12:
                self.game.modes.add(self.warehouse_raid)
            elif self.current_mode_num==13:
                self.game.modes.add(self.jones_vs_aliens)
            elif self.current_mode_num==14:
                self.game.modes.add(self.ringmaster)
                
            #update mode flags and player stats
            self.mode_running = True
            self.game.set_player_stats('mode_running',self.mode_running)
            self.game.set_player_stats('mode_running_id',self.current_mode_num)
            #record audits
            audits.record_value(self,'modeStarted')


        def remove_selected_scene(self):
            self.log.debug("Removing Movie Scene Mode"+str(self.current_mode_num))
            if self.current_mode_num==0:
                self.game.modes.remove(self.get_the_idol)
            elif self.current_mode_num==1:
                self.game.modes.remove(self.streets_of_cairo)
            elif self.current_mode_num==2:
                self.game.modes.remove(self.well_of_souls)
            elif self.current_mode_num==3:
                if self.secret_mode:
                    self.game.modes.remove(self.werewolf)
                else:
                    self.game.modes.remove(self.raven_bar)
            elif self.current_mode_num==4:
                self.game.modes.remove(self.monkey_brains)
            elif self.current_mode_num==5:
                self.game.modes.remove(self.steal_the_stones)
            elif self.current_mode_num==6:
                self.game.modes.remove(self.mine_cart)
            elif self.current_mode_num==7:
                self.game.modes.remove(self.rope_bridge)
            elif self.current_mode_num==8:
                self.game.modes.remove(self.castle_grunwald)
            elif self.current_mode_num==9:
                self.game.modes.remove(self.tank_chase)
            elif self.current_mode_num==10:
                self.game.modes.remove(self.the_three_challenges)
            elif self.current_mode_num==11:
                self.game.modes.remove(self.choose_wisely)
            elif self.current_mode_num==12:
                self.game.modes.remove(self.warehouse_raid)
            elif self.current_mode_num==13:
                self.game.modes.remove(self.jones_vs_aliens)
            elif self.current_mode_num==14:
                self.game.modes.remove(self.ringmaster)

                    
        def mode_text(self):
            self.name_layer.set_text(self.name_text, color=dmd.BROWN)
            self.info_layer.set_text(self.info_text, color=dmd.CYAN)
            self.info2_layer.set_text(self.info2_text, color=dmd.CYAN)


        def scene_start_delay(self):
            time = 2

            if self.ssd_count==0: #make sure the following delays only get called once
                if self.current_mode_num !=2 and self.current_mode_num!=3 and self.current_mode_num!=6 and self.current_mode_num!=11 and self.current_mode_num!=12: #don't set timeout for these non time based modes, mode 11 needs to be included here as it has its own choice timeout but not a timeout from here.
                    #self.cancel_delayed('scene_timeout')
                    self.cancel_delayed('scene_unpause')
                    self.delay(name='scene_timeout', event_type=None, delay=self.timer+time, handler=self.end_scene)
                self.delay(name='scene_delay', event_type=None, delay=time, handler=self.add_selected_scene)
                if self.current_mode_num!=3 and self.current_mode_num!=6 and self.current_mode_num!=11: #don't eject ball for video modes, scene will eject it itself at end
                    self.delay(name='eject_delay', event_type=None, delay=time-1, handler=self.eject_ball)
                self.delay(name='clear_delay', event_type=None, delay=time, handler=self.clear)
                self.ssd_count+=1


        def cancel_timeout(self):
            self.cancel_delayed('scene_timeout')


        def end_scene(self):
            #play sound
            self.game.sound.stop_music()
            self.game.sound.play("scene_ended")

            #remove the active scene
            self.remove_selected_scene()

            #display mode total on screen
            self.total_score = self.mode_start_value+self.game.get_player_stats('last_mode_score')
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
            self.info_layer.set_text(locale.format("%d",self.total_score,True), color=dmd.GREEN)
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.name_layer,self.info_layer])

            #call the common end scene code
            self.end_scene_common(3)
          
            
        def end_scene_common(self,timer):
            #cancel any running timers in case mode was completed
            self.cancel_delayed('scene_timeout')
            self.cancel_delayed('scene_unpause')
            
            #update mode completed status tracking
            self.select_list[self.current_mode_num] =1
            #set next mode to be played
            self.unplayed_scenes('right')

            #update the bonus mode tracking
            bonus_mode_tracking = self.game.get_player_stats('bonus_mode_tracking')
            bonus_mode_tracking.append({'name':self.name_text,'score':self.total_score})
            self.game.set_player_stats('bonus_mode_tracking',bonus_mode_tracking)
            #debug
            self.log.info("bonus mode tracking:%s",bonus_mode_tracking)

            #clean up
            self.delay(name='clear_display', event_type=None, delay=timer, handler=self.pre_clear)
            self.update_lamps()

            #update mode running flag and player stats
            self.mode_running = False
            self.game.set_player_stats('mode_running',self.mode_running)
            self.game.set_player_stats('mode_running_id',99)
            
            #unpause any contiuning adventures now the scene mode is finished
            if self.game.get_player_stats('adventure_continuing'):
                self.game.base_game_mode.poa.adventure_queue(False)
                
            #continue any previously active mode music
            self.game.utility.resume_mode_music()  
            
            
        def start_final_adventure(self):
            self.game.modes.add(self.final_adventure)
            self.mode_enabled = False
            
            
        def mode_bonus(self):
            timer=2
            self.game.screens.mode_bonus(timer,self.mode_bonus_value)
            self.delay(name='eject_delay', event_type=None, delay=timer-1, handler=self.eject_ball)
            
            #pause any active modes for bonus
            self.mode_paused()

            audits.record_value(self,'modeBonus')


        def pre_clear(self):
            self.name_layer.set_text("")
            self.info_layer.set_text("")
            self.info2_layer.set_text("")
            self.clear()

        def clear(self):
            self.layer=None
            

        def sw_grailEject_active_for_500ms(self,sw):
            #check and enable secret flag if correct sequence
            if self.game.switches.flipperLwR.is_active(0.5):
                self.secret_mode = True
            else:
                self.secret_mode = False
                
            if self.game.get_player_stats('hof_status')!='lit' and not self.game.get_player_stats('mode_blocking'):
                self.start_scene()
                 
                #return procgame.game.SwitchStop   

        def sw_grailEject_active(self,sw):
            self.game.lampctrl.play_show('mode_start_shot', repeat=False,callback=self.game.update_lamps)
            

        def sw_captiveBallRear_inactive(self, sw):
            if not self.mode_running:
                self.move_left()

        def sw_rightRampMade_active(self, sw):
            if not self.mode_running and self.game.switches.rightRampMade.time_since_change()>1:
                self.move_right()

        def sw_leftLoopTop_active(self, sw):
            if not self.mode_enabled and not self.mode_running and not self.all_scenes_complete:
                self.mode_enabled=True
                self.game.set_player_stats('mode_enabled',self.mode_enabled)

                self.mode_start_lamp(self.mode_enabled)

        def sw_rightLoopTop_active(self, sw):
            if not self.mode_enabled and not self.mode_running and not self.all_scenes_complete:
                self.mode_enabled=True
                self.game.set_player_stats('mode_enabled',self.mode_enabled)
                
                self.mode_start_lamp(self.mode_enabled)