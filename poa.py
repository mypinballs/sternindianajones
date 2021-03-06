import procgame
import locale
import logging
from procgame import *
from adventure import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,mode)
		self.mode = mode

	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()

class POA(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(POA, self).__init__(game, priority)

                self.log = logging.getLogger('ij.poa')
                
                self.adventure_mode = Adventure(self.game,priority+1)

		self.text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['07x5'], "center")
		self.award_layer = dmd.TextLayer(128/2, 17, self.game.fonts['num_14x10'], "center")
		self.layer = dmd.GroupedLayer(128, 32, [self.text_layer, self.award_layer])
		self.time = 0
		self.awards = ['award1','award2']

                #setup global mode variables
                #self.lamps=['adventureA','adventureD','adventureV','adventureE1','adventureN','adventureT','adventureU','adventureR','adventureE2']
                self.lamps = ['jonesJ','jonesJ','jonesO','jonesO','jonesN','jonesN','jonesE','jonesE','jonesS'] 

                #register music files
                self.game.sound.register_music('poa_play', music_path+"poa.aiff")

                #setup sound calls
		self.game.sound.register_sound('take_path', speech_path+'take_the_poa.aiff')
		self.game.sound.register_sound('target', sound_path+'adv_target_1.aiff')
                self.game.sound.register_sound('target', sound_path+'adv_target_2.aiff')
                self.game.sound.register_sound('target', sound_path+'adv_target_3.aiff')
                self.game.sound.register_sound('target', sound_path+'adv_target_4.aiff')
                self.game.sound.register_sound('poa_lit_jingle', sound_path+'poa_lit_jingle.aiff')
                self.game.sound.register_sound('adventure_start', sound_path+'poa_start.aiff')

                #setup the switches which pause an active poa 
                self.poa_pausing_switchnames = []
                for switch in self.game.switches.items_tagged('poa_pause'):
                    self.poa_pausing_switchnames.append(switch.name)
                    self.log.info("POA Pausing Switch is:"+switch.name)
                    
                for switch in self.poa_pausing_switchnames:
			self.add_switch_handler(name=switch, event_type='active', \
				delay=None, handler=self.adventure_paused)  
                                

        def reset(self):
                self.adventure_started  = False
                #self.adventure_running = False
                self.adventure_continuing  = False
                self.adventure_queued=False
                self.letters_collected = 0
                self.letters_spotted = 0
                self.set1 = False
                self.set2 = False
                self.set3 = False
                self.adventureA_lit = False
                self.adventureD_lit = False
                self.adventureV_lit = False
                self.adventureE1_lit = False
                self.adventureN_lit = False
                self.adventureT_lit = False
                self.adventureU_lit = False
                self.adventureR_lit = False
                self.adventureE2_lit = False
                self.flag = [False,False,False,False,False,False,False,False,False]
                
                self.pit_value_base = 20000000
                
                self.reset_lamps()
                self.reset_pit_value()

	
	def mode_started(self):
                self.log.info("POA Mode Started")
                #reset variables
                self.reset()
                
                self.full_sets_completed = 0 #reset each ball?

                #setup mode general stuff
                self.adventure_continue_timer = self.game.user_settings['Gameplay (Feature)']['Adventure Continue Timer']
                self.pause_length = self.game.user_settings['Gameplay (Feature)']['Mode Timers Pause Length']
                self.pit_active_level = int(self.game.user_settings['Gameplay (Feature)']['Path of Adventure Pit Lit Level'])
                self.score_layer = ModeScoreLayer(48, 1, self.game.fonts['num_09Bx7'], self)

                #load player specific data
                self.flag = self.game.get_player_stats('poa_flag')
                self.load_aux_flags()
                self.letters_spotted = self.game.get_player_stats('adventure_letters_spotted')
                self.letters_collected = self.game.get_player_stats('adventure_letters_collected')
                self.pit_value = self.game.get_player_stats('pit_value')

                #update lamp states
                self.update_lamps()

                #debug
                #self.poa_ready()
                #self.adventure_start()
        
        
        def mode_tick(self):
                #monitor game flags for modes where adventure needs to end if running
                #important game setup logic - possibly add settings to change this list?
                if self.game.get_player_stats('poa_enabled') and (self.game.get_player_stats("multiball_started") or self.game.get_player_stats("quick_multiball_started") or self.game.get_player_stats('multiball_mode_started') or self.game.get_player_stats("path_mode_started") or self.game.get_player_stats("video_mode_started")):
                   self.log.debug("enabled adventure being cancelled and requeued by special mode starting")
                   self.poa_requeue()
                
                #monitor scenario to clear continue display from running over the top of started modes
#                if self.adventure_started and self.game.get_player_stats('mode_running') and self.layer!=None:
#                    self.clear()
                    

        def mode_stopped(self):
                #save player specific data
                self.game.set_player_stats('poa_flag',self.flag)
                self.game.set_player_stats('adventure_letters_spotted',self.letters_spotted)
                self.letters_collected +=self.letters_spotted
                self.game.set_player_stats('adventure_letters_collected',self.letters_collected)

                #end adventure
                self.adventure_expired()

        
        def load_aux_flags(self):
                self.adventureA_lit = self.flag[0]
                self.adventureD_lit = self.flag[1]
                self.adventureV_lit = self.flag[2]
                self.adventureE1_lit = self.flag[3]
                self.adventureN_lit = self.flag[4]
                self.adventureT_lit = self.flag[5]
                self.adventureU_lit = self.flag[6]
                self.adventureR_lit = self.flag[7]
                self.adventureE2_lit = self.flag[8]

        def spell_adventure(self):
                bgnd = dmd.FrameLayer(opaque=False,frame=dmd.Animation().load(game_path+'dmd/adventure_bgnd.dmd').frames[0])     

                A = dmd.FrameLayer(opaque=False)
                D = dmd.FrameLayer(opaque=False)
                V = dmd.FrameLayer(opaque=False)
                E1 = dmd.FrameLayer(opaque=False)
                N = dmd.FrameLayer(opaque=False)
                T = dmd.FrameLayer(opaque=False)
                U = dmd.FrameLayer(opaque=False)
                R = dmd.FrameLayer(opaque=False)
                E2 = dmd.FrameLayer(opaque=False)
                completed = dmd.FrameLayer(opaque=False)

                if self.adventureA_lit:
                     A.frame = dmd.Animation().load(game_path+'dmd/adventure_a.dmd').frames[0]
                     A.composite_op = "blacksrc"
                if self.adventureD_lit:
                     D.frame = dmd.Animation().load(game_path+'dmd/adventure_d.dmd').frames[0]
                     D.composite_op = "blacksrc"
                if self.adventureV_lit:
                     V.frame = dmd.Animation().load(game_path+'dmd/adventure_v.dmd').frames[0]
                     V.composite_op = "blacksrc"
                if self.adventureE1_lit:
                     E1.frame = dmd.Animation().load(game_path+'dmd/adventure_e1.dmd').frames[0]
                     E1.composite_op = "blacksrc"
                if self.adventureN_lit:
                     N.frame = dmd.Animation().load(game_path+'dmd/adventure_n.dmd').frames[0]
                     N.composite_op = "blacksrc"
                if self.adventureT_lit:
                     T.frame = dmd.Animation().load(game_path+'dmd/adventure_t.dmd').frames[0]
                     T.composite_op = "blacksrc"
                if self.adventureU_lit:
                     U.frame = dmd.Animation().load(game_path+'dmd/adventure_u.dmd').frames[0]
                     U.composite_op = "blacksrc"
                if self.adventureR_lit:
                     R.frame = dmd.Animation().load(game_path+'dmd/adventure_r.dmd').frames[0]
                     R.composite_op = "blacksrc"
                if self.adventureE2_lit:
                     E2.frame = dmd.Animation().load(game_path+'dmd/adventure_e2.dmd').frames[0]
                     E2.composite_op = "blacksrc"

                if (self.adventureA_lit and self.adventureD_lit==True and self.adventureV_lit==True):
                    self.set1=True

                if (self.adventureE1_lit==True and self.adventureN_lit==True and self.adventureT_lit==True):
                    self.set2=True

                if (self.adventureU_lit==True and self.adventureR_lit==True and self.adventureE2_lit==True):
                    self.set3=True

                adventure_layer = dmd.GroupedLayer(128, 32, [bgnd,A,D,V,E1,N,T,U,R,E2,completed])
                
                if self.game.get_player_stats('mode_running_id')!=0 and not self.game.get_player_stats("ark_mode_started"): #do not display adventure graphic if get the idol or ark shot modes are running
                    self.layer = adventure_layer
                

                if self.letters_spotted==9:
                    completed.frame = dmd.Animation().load(game_path+'dmd/adventure_completed.dmd').frames[0]
                    completed.composite_op = "blacksrc"

                    self.delay(name='poa_ready', event_type=None, delay=2, handler=self.poa_ready)
                #elif self.adventure_started  
                   # self.delay(name='act_delay', event_type=None, delay=2, handler=self.adventure_continue_display)

                else:
                    self.delay(name='clear', event_type=None, delay=2, handler=self.clear)


                print(self.letters_spotted)
                


        def poa_ready(self):
            
            #set no. sets of letters completed
            self.full_sets_completed +=1
            print(self.full_sets_completed)

            anim = dmd.Animation().load(game_path+"dmd/poa_lit_bgnd.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,repeat=True,frame_time=3)
            text_layer1 = dmd.TextLayer(90, 15, self.game.fonts['8x6'], "center")
            text_layer2 = dmd.TextLayer(90, 23, self.game.fonts['8x6'], "center")
            text_layer1.composite_op='blacksrc'
            text_layer2.composite_op='blacksrc'

            if self.full_sets_completed>1:  #display new pit value if second or more time around
                self.pit_value +=10000000
                text_layer1.set_text('Pit Value'.upper())
                text_layer2.set_text('Increased'.upper())
            elif self.game.get_player_stats("multiball_started") or self.game.get_player_stats('multiball_mode_started'):  #multiball started
                text_layer1.set_text('Lit After'.upper())
                text_layer2.set_text('Multiball'.upper())
                self.game.set_player_stats("poa_queued",True)
            elif self.game.get_player_stats("path_mode_started"):  #path mode started
                text_layer1.set_text('Lit After'.upper())
                text_layer2.set_text('Path Mode'.upper())
                self.game.set_player_stats("poa_queued",True)
            else:
                #run poa ready graphics
                text_layer1.font =  self.game.fonts["num_09Bx7"]
                text_layer1.y=17
                text_layer1.set_text('Is Lit'.upper())

                #play speech
                self.game.sound.play('take_path')
                
                
            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer1,text_layer2])

            #queue display change
            timer=2.5
            #if self.adventure_started:
            #    self.delay(name='act_delay', event_type=None, delay=timer, handler=self.adventure_continue_display)
            #else:
            self.delay(name='clear', event_type=None, delay=timer, handler=self.clear)

            #update player stats - pit value
            self.game.set_player_stats('pit_value',self.pit_value)
            
            #reset variables
            self.reset()
            
            #poa enabled logic
            self.poa_enabled()


        def poa_enabled(self):
            if self.game.get_player_stats("poa_queued")==False:
                
                #setup poa flasher
                #self.game.coils.flasherKingdom.schedule(0x30003000, cycle_seconds=0, now=True)
                self.game.effects.drive_flasher('flasherKingdom','medium',time=0)
                self.game.effects.drive_flasher('flasherSkull','fast',time=2)

                #play jingle
                self.game.sound.play('poa_lit_jingle')
                
                #set player stats
                self.game.set_player_stats('poa_enabled',True)

                #timer for poa start
                self.delay(name='adventure_timeout', event_type=None, delay=55, handler=self.adventure_expired)
                self.cancel_delayed("poa_enabled_check")
                
                self.log.info('POA Enabled & Timer Running')
            else:
                self.delay(name='poa_enabled_check', event_type=None, delay=1, handler=self.poa_enabled)
                
        
        def poa_requeue(self):
            if self.game.get_player_stats('poa_enabled'):
                #cancel the activated items
                self.cancel_delayed('adventure_timeout')
                #self.game.coils.divertorHold.disable()
                self.game.coils.flasherKingdom.disable()
            
                #update the player stats
                self.game.set_player_stats('poa_enabled',False)
                self.game.set_player_stats("poa_queued",True)
            
                #setup the queue
                self.poa_enabled()


        def adventure_start(self):
            #self.game.mini_playfield.path_sequence()
            
            #stop ball
            self.stop_ball()
            
            self.game.coils.flasherKingdom.disable()
            
            self.adventure_started  = True
            self.adventure_continuing  = False
            self.game.set_player_stats('adventure_started',self.adventure_started)
            self.game.set_player_stats('adventure_continuing',self.adventure_continuing)
            
            self.adventure_mode.showcase_arrow_lamps() #this starts the flashing arrow lamps for instructional use
            
            #anim = dmd.Animation().load(game_path+"dmd/poa_instructions.dmd")
            #self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=True,repeat=True,frame_time=6)
            
            anim = dmd.Animation().load(game_path+"dmd/poa_lit_bgnd.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,repeat=True,frame_time=3)
            text_layer1 = dmd.TextLayer(90, 15, self.game.fonts['8x6'], "center")
            text_layer2 = dmd.TextLayer(90, 23, self.game.fonts['8x6'], "center")
            text_layer1.composite_op='blacksrc'
            text_layer2.composite_op='blacksrc'
            text_layer1.set_text('Shoot All'.upper())
            text_layer2.set_text('Lit Arrows'.upper())
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer1,text_layer2])

            self.game.sound.play("adventure_start")
            self.game.sound.play_music('poa_play', loops=-1)
            
            self.cancel_delayed('adventure_timeout')
            #cancel any queued unpausing now we are ready to contiune
            self.cancel_delayed('adventure_unpause')
            #cancel the continune timer in case we came here from a continue
            self.cancel_delayed('adventure_continue_timer')
            
            self.delay(name='adv_start_delay', event_type=None, delay=4, handler=self.adventure_start2)


        def adventure_start2(self,timer=0):
            #add the adventure mode
            self.game.modes.add(self.adventure_mode)
            #release the ball
            self.release_ball()
            self.game.update_lamps()
            self.adventure_continue_timer = self.game.user_settings['Gameplay (Feature)']['Adventure Continue Timer'] #reset the continue timer to stored value here for each new attempt if needed
                
            
        def adventure_continue(self):
                self.adventure_continuing  = True
                self.game.set_player_stats('adventure_continuing',self.adventure_continuing)
                
                #self.game.coils.flasherKingdom.schedule(0x30003000, cycle_seconds=0, now=True)
                self.game.effects.drive_flasher('flasherKingdom','medium',time=0)
                self.game.effects.drive_flasher('flasherSkull','fast',time=2)

                bgnd_anim = dmd.Animation().load(game_path+"dmd/poa_continue_bgnd.dmd")
                bgnd_layer = dmd.FrameLayer(frame=bgnd_anim.frames[0])

                self.score_layer.x = 48
                self.score_layer.y=0
                self.score_layer.justify='center'

                info_layer1 = dmd.TextLayer(48, 14, self.game.fonts['8x6'], "center", opaque=False)
                info_layer2 = dmd.TextLayer(48, 22, self.game.fonts['8x6'], "center", opaque=False)

                info_layer1.set_text("Continue Path".upper(), color=dmd.PURPLE)
                info_layer2.set_text("Of Adventure".upper(),  color=dmd.PURPLE)

                self.timer_layer = dmd.TimerLayer(115, 4, self.game.fonts['23x12'],self.adventure_continue_timer,"right")

                self.adventure_continue_layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer1,info_layer2,self.score_layer,self.timer_layer])
                self.adventure_continue_display()
                #reset timer for each attempt
                self.cancel_delayed('adventure_continue_timer')
                self.delay(name='adventure_continue_timer', event_type=None, delay=self.adventure_continue_timer, handler=self.adventure_expired)
                self.cancel_delayed("poa_exited_check")
            #else:
            #    self.delay(name='poa_exited_check', event_type=None, delay=1, handler=self.adventure_continue)


        def adventure_continue_display(self):
            self.layer =  self.adventure_continue_layer
            
        
        def adventure_paused(self,sw): #relating to continue
            if self.adventure_continuing:
                self.timer_layer.pause(True)
                self.cancel_delayed('adventure_continue_timer')
                self.cancel_delayed('adventure_unpause')
                if sw!= None:
                    self.delay(name='adventure_unpause', delay=self.pause_length,handler=self.adventure_unpaused)
            
            
        def adventure_unpaused(self): #relating to continue
            if self.adventure_continuing:
                self.timer_layer.pause(False) 
                self.delay(name='adventure_continue_timer', event_type=None, delay=self.timer_layer.get_time_remaining(), handler=self.adventure_expired)
        

        def adventure_queue(self,enable): #relating to continue
            #monitor scenario to clear pause continue timer and clear display from running over the top of starting modes
            if enable:
                self.adventure_paused(sw=None)
                self.adventure_queued=True
                self.clear()
            else:
                self.adventure_continue_timer = self.timer_layer.get_time_remaining()
                self.adventure_continue()
                #self.adventure_unpaused()
                self.adventure_queued=False

            
        def adventure_expired(self): #change name to poa_expired?
            # Manually cancel  delays in case this function was called externally.
            self.cancel_delayed('adventure_continue_timer')
            self.cancel_delayed('poa_enabled_check')

            self.game.coils.flasherKingdom.disable()
            self.reset_lamps()
            
            #self.game.mini_playfield.path_ended()
            #remove the adventure mode
            if self.adventure_started:
                self.game.modes.remove(self.adventure_mode)
            
            self.adventure_started  = False
            self.game.set_player_stats('adventure_started',self.adventure_started)
            self.adventure_continuing  = False
            self.game.set_player_stats('adventure_continuing',self.adventure_continuing)
            
            #continue any previously active mode music
            self.game.utility.resume_mode_music()    

            self.clear()


	def begin(self):
            #self.reset_lamps()
            pass


        def update_lamps(self):
            #flags=[self.adventureA_lit,self.adventureD_lit,self.adventureV_lit,self.adventureE1_lit,self.adventureN_lit,self.adventureT_lit,self.adventureU_lit,self.adventureR_lit,self.adventureE2_lit]
#            for i in range(len(self.flag)):
#                if self.flag[i]:
#                    self.game.effects.drive_lamp(self.lamps[i],'on')
#                else:
#                    self.game.effects.drive_lamp(self.lamps[i],'medium')
            pass


	def reset_lamps(self):
#                for i in range(len(self.lamps)):
#                    self.game.effects.drive_lamp(self.lamps[i],'medium')
            pass
                    

        def reset_pit_value(self):
            self.pit_value = self.pit_value_base


        def clear(self):
            self.layer=None


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)


        def letter_hit(self,toggle,lamp_name):
            if toggle == False:
                self.game.effects.drive_lamp(lamp_name,'smarton')
                self.letters_spotted +=1
                toggle=True;
                print("adventure lamp lit: %s "%(lamp_name))
                print("toggle value: %s "%(str(toggle)))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            

        def light_next_in_sequence(self):

            if self.adventureA_lit==False:
                self.sw_adventureA_active(self)
            elif self.adventureD_lit==False:
                self.sw_adventureD_active(self)
            elif self.adventureV_lit==False:
                self.sw_adventureV_active(self)
            elif self.adventureE1_lit==False:
                self.sw_adventureE1N_active(self)
            elif self.adventureN_lit==False:
                self.sw_adventureE1N_active(self)
            elif self.adventureT_lit==False:
                self.sw_adventureT_active(self)
            elif self.adventureU_lit==False:
                self.sw_adventureUR_active(self)
            elif self.adventureR_lit==False:
                self.sw_adventureUR_active(self)
            elif self.adventureE2_lit==False:
                self.sw_adventureE2_active(self)


	def sw_adventureA_active(self, sw):
            #self.target_hit(0)
            if self.adventureA_lit == False:
                #self.game.drive_lamp(self.lamps[0],'on')
                self.letters_spotted +=1
                self.adventureA_lit=True;
                self.flag[0]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[0]))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)
                if self.set1==True:
                    self.light_next_in_sequence()

            self.game.sound.play("target")
           
        
        def sw_adventureD_active(self, sw):

            if self.adventureD_lit == False:
                #self.game.drive_lamp(self.lamps[1],'on')
                self.letters_spotted +=1
                self.adventureD_lit=True;
                self.flag[1]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[1]))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)
                if self.set1==True:
                    self.light_next_in_sequence()

            self.game.sound.play("target")
            
                
        def sw_adventureV_active(self, sw):
            if self.adventureV_lit == False:
                #self.game.drive_lamp(self.lamps[2],'on')
                self.letters_spotted +=1
                self.adventureV_lit=True;
                self.flag[2]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[2]))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)
                if self.set1==True:
                    self.light_next_in_sequence()

            self.game.sound.play("target")
            
                
#        def sw_adventureE1_active(self, sw):
#            if self.adventureE1_lit == False:
#                #self.game.drive_lamp(self.lamps[3],'on')
#                self.letters_spotted +=1
#                self.adventureE1_lit=True;
#                self.flag[3]=True;
#                self.game.set_player_stats('poa_flag',self.flag)
#                #print("adventure lamp lit: %s "%(self.lamps[3]))
#                self.game.score(500000)
#                self.spell_adventure()
#            else:
#                self.game.score(100000)
#                if self.set2==True:
#                    self.light_next_in_sequence()
#
#            self.game.sound.play("target")
            
        
        def sw_adventureE1N_active(self, sw):
            if self.adventureE1_lit == False:
                #self.game.drive_lamp(self.lamps[3],'on')
                self.letters_spotted +=1
                self.adventureE1_lit=True;
                self.flag[3]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[3]))
                self.game.score(500000)
                self.spell_adventure()
            elif self.adventureN_lit == False:
                #self.game.drive_lamp(self.lamps[4],'on')
                self.letters_spotted +=1
                self.adventureN_lit=True;
                self.flag[4]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[4]))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)
                if self.set2==True:
                    self.light_next_in_sequence()


            self.game.sound.play("target")
            
                
        def sw_adventureT_active(self, sw):
            if self.adventureT_lit == False:
                #self.game.drive_lamp(self.lamps[5],'on')
                self.letters_spotted +=1
                self.adventureT_lit=True;
                self.flag[5]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[5]))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)
                if self.set2==True:
                    self.light_next_in_sequence()


            self.game.sound.play("target")
            
                
#        def sw_adventureU_active(self, sw):
#            if self.adventureU_lit == False:
#                #self.game.drive_lamp(self.lamps[6],'on')
#                self.letters_spotted +=1
#                self.adventureU_lit=True;
#                self.flag[6]=True;
#                self.game.set_player_stats('poa_flag',self.flag)
#                #print("adventure lamp lit: %s "%(self.lamps[6]))
#                self.game.score(500000)
#                self.spell_adventure()
#            else:
#                self.game.score(100000)
#                if self.set3==True:
#                    self.light_next_in_sequence()
#
#            self.game.sound.play("target")
            
                
        def sw_adventureUR_active(self, sw):
            if self.adventureU_lit == False:
                #self.game.drive_lamp(self.lamps[6],'on')
                self.letters_spotted +=1
                self.adventureU_lit=True;
                self.flag[6]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[6]))
                self.game.score(500000)
                self.spell_adventure()
            elif self.adventureR_lit == False:
                #self.game.drive_lamp(self.lamps[7],'on')
                self.letters_spotted +=1
                self.adventureR_lit=True;
                self.flag[7]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[7]))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)
                if self.set3==True:
                    self.light_next_in_sequence()

            self.game.sound.play("target")
           
                
        def sw_adventureE2_active(self, sw):
            if self.adventureE2_lit == False:
                #self.game.drive_lamp(self.lamps[8],'on')
                self.letters_spotted +=1
                self.adventureE2_lit=True;
                self.flag[8]=True;
                self.game.set_player_stats('poa_flag',self.flag)
                #print("adventure lamp lit: %s "%(self.lamps[8]))
                self.game.score(500000)
                self.spell_adventure()
            else:
                self.game.score(100000)
                if self.set3==True:
                    self.light_next_in_sequence()

            self.game.sound.play("target")
           
            
        def sw_templeStandup_active(self, sw):
            self.game.score(100000)
            if self.set2==True:
                self.light_next_in_sequence()
            
            self.game.sound.play("target")
            

        def sw_rightRampMade_active(self, sw): #top post replacement
            self.log.debug("poa mode top post watcher")
            self.log.debug("full sets %s",self.full_sets_completed)
            self.log.debug("poa queued %s",self.game.get_player_stats("poa_queued"))
            if self.full_sets_completed>=1 and not self.game.get_player_stats("poa_queued") and self.game.switches.rightRampMade.time_since_change()>1:
                if not self.adventure_started:
                    self.adventure_start()
                elif self.adventure_continuing and not self.adventure_queued:
#                    self.adventure_start2()
#                    self.status_display()
                    self.adventure_start()
                    
                return procgame.game.SwitchStop


        def status_display(self):
            anim = dmd.Animation().load(game_path+"dmd/poa_info_bgnd.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False, frame_time=6)

            #set text layers
            text_layer1 = dmd.TextLayer(64, 18, self.game.fonts['tiny7'], "center", opaque=False)
            text_layer2 = dmd.TextLayer(64, 24, self.game.fonts['tiny7'], "center", opaque=False)
            #text_layer1.set_text(("Adventure "+str(self.game.mini_playfield.get_level())+". Pit lit at "+str(self.pit_active_level)).upper(), color=dmd.CYAN)
            text_layer1.set_text(("Pit lit at "+str(self.pit_active_level)).upper(), color=dmd.CYAN)
            text_layer2.set_text(("Pit Value:"+locale.format("%d", self.game.get_player_stats('pit_value'), True)).upper(),blink_frames=4, color=dmd.PURPLE)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer1,text_layer2])


        def stop_ball(self):
            self.game.coils.rampBallStop.patter(2,20,self.game.coils.rampBallStop.default_pulse_time,True)
            
            
        def release_ball(self):
            self.game.coils.rampBallStop.disable()
            self.clear()
        