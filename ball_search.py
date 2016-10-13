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
                
                self.stop_switches = stop_switches
		self.countdown_time = countdown_time
		self.coils = coils
		self.special_handler_modes = special_handler_modes
		self.enabled = 0;
		for switch in reset_switches:
			self.add_switch_handler(name=str(switch), event_type=str(reset_switches[switch]), delay=None, handler=self.reset)
		for switch in stop_switches:
			self.add_switch_handler(name=str(switch), event_type=str(stop_switches[switch]), delay=None, handler=self.stop)

                
        def enable(self):
		self.enabled = 1;
		self.reset('None')


	def disable(self):
		self.stop(None)
		self.enabled = 0;


        def reset(self,sw):
		if self.enabled:
			# Stop delayed coil activations in case a ball search has
			# already started.
			for coil in self.coils:
				self.cancel_delayed('ball_search_coil1')
			self.cancel_delayed('start_special_handler_modes')
			self.cancel_delayed
			schedule_search = 1
			for switch in self.stop_switches:

				# Don't restart the search countdown if a ball
				# is resting on a stop_switch.  First,
				# build the appropriate function call into
				# the switch, and then call it using getattr()
				sw = self.game.switches[str(switch)]
				state_str = str(self.stop_switches[switch])
				m = getattr(sw, 'is_%s' % (state_str))
				if m():
					schedule_search = 0

			if schedule_search:
				self.cancel_delayed(name='ball_search_countdown');
				self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.perform_search, param=0)


        def stop(self,sw):
		self.cancel_delayed(name='ball_search_countdown');


	def perform_search(self, completion_wait_time, completion_handler = None):
		if (completion_wait_time != 0):
			self.ball_missing()
		delay = .150
		for coil in self.coils:
			self.delay(name='ball_search_coil1', event_type=None, delay=delay, handler=self.pop_coil, param=str(coil))
			delay = delay + .150
		self.delay(name='start_special_handler_modes', event_type=None, delay=delay, handler=self.start_special_handler_modes)

		if (completion_wait_time != 0):
			pass
		else:
			self.cancel_delayed(name='ball_search_countdown');
			self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.perform_search, param=0)


        def ball_missing(self):
            info_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            bgnd_layer = dmd.FrameLayer(opaque=False)
            bgnd_layer.frame = dmd.Animation().load(game_path+'dmd/scene_ended_bgnd.dmd').frames[0]

            multiple = ''
            balls_missing = self.game.num_balls_total - self.game.trough.num_balls()
            if balls_missing>1:
                multiple='s'

            message = str(balls_missing)+" BALL"+multiple+" LOST!"
            info_layer.set_text(message,2,5)#on for 1.5 seconds 5 blinks
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer])
            self.game.sound.play('elephant_alert')
            self.log.info(message)

            self.delay(name='clear',delay=2, handler=self.clear)

            
        def clear(self):
            self.layer = None
            
            
        def pop_coil(self,coil):
		self.game.coils[coil].pulse()

	def start_special_handler_modes(self):
		for special_handler_mode in self.special_handler_modes:
			self.game.modes.add(special_handler_mode)
			self.delay(name='remove_special_handler_mode', event_type=None, delay=7, handler=self.remove_special_handler_mode, param=special_handler_mode)

	def remove_special_handler_mode(self,special_handler_mode):
		self.game.modes.remove(special_handler_mode)