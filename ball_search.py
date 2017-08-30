import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"


class Ball_Search(game.Mode):
	"""Ball Search mode improvements."""
	def __init__(self, game, priority, countdown_time, coils=[], reset_switches=[], stop_switches=[], enable_switch_names=[], special_handler_modes=[]):
                super(Ball_Search, self).__init__(game, priority)
                
                self.log = logging.getLogger('ij.ball_search')
                self.game.sound.register_sound('elephant_alert', sound_path+"elephant.aiff")
                
                self.countdown_time =  int(self.game.user_settings['Machine (Standard)']['Ball Search Timer'])
                
                self.stop_switches = []#stop_switches
                for switch in self.game.switches.items_tagged('ballsearch_stop'):
                    self.stop_switches.append(switch.name)
                
                self.reset_switches = []#reset_switches
                for switch in self.game.switches.items_tagged('ballsearch_reset'):
                    self.reset_switches.append(switch.name)
		
                self.coils = []#coils
                for coil in self.game.coils.items_tagged('ballsearch'):
                    self.coils.append(coil.name)
                    
		self.special_handler_modes = special_handler_modes
		
		for switch in self.reset_switches:
			self.add_switch_handler(name=str(switch), event_type='inactive', delay=None, handler=self.reset)
		for switch in self.stop_switches:
			self.add_switch_handler(name=str(switch), event_type='active', delay=None, handler=self.stop)
                        self.add_switch_handler(name=str(switch), event_type='inactive', delay=None, handler=self.reset)

                #output game defs
                self.log.info("Ball Search Coils are:%s",self.coils)
                self.log.info("Ball Search Stop Switches are:%s",self.stop_switches)
                self.log.info("Ball Search Reset Switches are:%s",self.reset_switches)

                #setup vars
                self.enabled = 0;
                self.max_ball_search_attempts = 10
                self.score1 = 0
                self.score2 = 0
                self.trough_issues = 0
                self.balls_lost_count = 0
                self.ball_search_count=0
                self.ballsearch_attempts=0
                self.ball_resting_flag = False
                
                
        def enable(self):
            self.log.debug("Ball Search Enabled")
            self.enabled = 1;
            self.ballsearch_attempts=0
            self.score1 = self.game.current_player().score
            self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.process)
         

	def disable(self):
            self.log.debug("Ball Search Disabled")
            self.enabled = 0;
            self.cancel_delayed('ball_search_coil')
            self.cancel_delayed('ball_search_countdown')
            self.ballsearch_attempts=0
            self.clear()
            

#        def reset(self,sw):
#		if self.enabled:
#			# Stop delayed coil activations in case a ball search has
#			# already started.
#			for coil in self.coils:
#				self.cancel_delayed('ball_search_coil')
#			self.cancel_delayed('start_special_handler_modes')
#			self.cancel_delayed
#			schedule_search = 1
#			for switch in self.stop_switches:
#
#				# Don't restart the search countdown if a ball
#				# is resting on a stop_switch.  First,
#				# build the appropriate function call into
#				# the switch, and then call it using getattr()
#				sw = self.game.switches[str(switch)]
#				state_str = str(self.stop_switches[switch])
#				m = getattr(sw, 'is_%s' % (state_str))
#				if m():
#					schedule_search = 0
#
#			if schedule_search:
#				self.cancel_delayed(name='ball_search_countdown');
#				self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.perform_search, param=0)

        #this method cancels the ball search timer
        def stop(self,sw):
            if self.game.ball>0:
                self.cancel_delayed(name='ball_search_countdown');
                self.ball_resting_flag = True
                
        #this method will start the ball search routine if it is not called within the set timer
        def reset(self,sw):
            if self.game.ball>0:
                self.ball_resting_flag = False
                self.disable()
                self.enable()
                 

#	def perform_search(self, completion_wait_time, completion_handler = None):
#		if (completion_wait_time != 0):
#			self.ball_missing()
#		delay = .150
#		for coil in self.coils:
#			self.delay(name='ball_search_coil', event_type=None, delay=delay, handler=self.pop_coil, param=str(coil))
#			delay = dely + .150
#		self.delay(name='start_special_handler_modes', event_type=None, delay=delay, handler=self.start_special_handler_modes)
#
#		if (completion_wait_time != 0):
#			pass
#		else:
#			self.cancel_delayed(name='ball_search_countdown');
#			self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.perform_search, param=0)
            
        
        def issue_display(self,message1=None,message2=None,severity=1,timer=2):
            #info_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            #info_layer2 = dmd.TextLayer(128/2, 18, self.game.fonts['7px_narrow_az'], "center", opaque=False)
            info_layer = dmd.TextLayer(128/2, 7, self.game.fonts['7px_narrow_az'], "center", opaque=False)
            info_layer2 = dmd.TextLayer(128/2, 18, self.game.fonts['num_09Bx7'], "center", opaque=False)
            bgnd_layer = dmd.FrameLayer(opaque=False)
            bgnd_layer.frame = dmd.Animation().load(game_path+'dmd/scene_ended_bgnd.dmd').frames[0]
            
            colour = dmd.GREEN
            if severity==2:
                colour = dmd.RED
            else:
                colour = dmd.YELLOW
            info_layer.set_text(message1, color=colour,seconds=timer)
            info_layer2.set_text(message2,color=dmd.GREEN,blink_frames=5,seconds=2)
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer2,info_layer])
            self.game.sound.play('elephant_alert')
            self.log.debug(message1)

            self.delay(name='clear',delay=timer, handler=self.clear)
        
        
        def ball_missing_display(self,timer=2):
            multiple = ''
            balls_missing = self.game.num_balls_total - self.game.trough.num_balls()
            if balls_missing>1:
                multiple='S'
            
            if balls_missing>0:
                message = str(balls_missing)+" BALL"+multiple+" MISSING!"
                self.issue_display(message1=message, message2="SEARCHING...",timer=timer)
            else:
                #call this is 0 balls lost and here. Must be a trough issue with bounce backs.
                self.trough_issue()
        
        
        def ball_lost_display(self,timer=2):
            self.issue_display(message1="BALL LOST!", message2="LAUNCHING ANOTHER...",severity=2,timer=timer)
            
            
        def clear(self):
            self.layer = None
            
        
#	def start_special_handler_modes(self):
#		for special_handler_mode in self.special_handler_modes:
#			self.game.modes.add(special_handler_mode)
#			self.delay(name='remove_special_handler_mode', event_type=None, delay=7, handler=self.remove_special_handler_mode, param=special_handler_mode)
#
#	def remove_special_handler_mode(self,special_handler_mode):
#		self.game.modes.remove(special_handler_mode)        
        

        def process(self):
            self.score2 = self.game.current_player().score
            self.log.info("score1:%s",self.score1)
            self.log.info("score2:%s",self.score2)
            
            if self.score1 == self.score2 and not self.ball_resting_flag:
                self.ballsearch_attempts+=1
                if self.ballsearch_attempts==self.max_ball_search_attempts:
                    self.delay('ball_lost', event_type=None, delay=2, handler=self.perform_ball_lost)
                else:
                     self.perform_search()
            else:
               self.score1 = self.score2
               self.ballsearch_attempts=0
               
            self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.process)
           

        def perform_ball_lost(self):
            self.cancel_delayed('ball_lost')
            self.cancel_delayed('ball_search_countdown')
            self.balls_lost_count+=1
            self.ball_lost_display()
            self.game.trough.launch_balls(1,stealth=True,callback=self.enable)
            self.ballsearch_attempts=0
            
            
        def trough_issue(self):
            self.cancel_delayed('ball_lost')
            self.cancel_delayed('ball_search_countdown')
            self.trough_issues+=1
            self.issue_display(message1='TROUGH MALFUNCTION',message2='CHECK EJECT...',severity=2,timer=3)
            self.game.trough.launch_balls(1,stealth=True,callback=self.enable)
            self.ballsearch_attempts=0
            

        def perform_search(self):
            wait = .180
            delay=wait
           
            self.log.debug("Performing Search....")
            self.ball_missing_display()
           
            for coil in self.coils:
                self.delay(name="ball_search_coil", event_type=None,delay=delay,handler=self.pop_coil,param=str(coil))
                delay=delay+wait
            
            #add a cycle of the temple mech for multiple concurrent even ball searches - ball stuck in mech?
            if self.ballsearch_attempts>1 and self.ballsearch_attempts/2==0:
                self.game.temple.cycle_temple()


        def pop_coil(self,coil):
            self.game.coils[coil].pulse()
            if self.game.current_player():
                self.game.current_player().score=self.score2
      
