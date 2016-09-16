import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class EntrySequenceManager(procgame.highscore.EntrySequenceManager):
	
#    def __init__(self, game, priority):
#        super(EntrySequenceManager, self).__init__(game, priority)
#        self.info_layer = dmd.TextLayer(128/2, 7, self.game.fonts['10x7_bold'], "center", opaque=False)
#        
    def create_highscore_entry_mode(self, left_text, right_text, entered_handler):
	# Override this to return our own RDC-based high score entry mode.
	return InitialEntryMode(game=self.game, priority=self.priority+1, left_text=left_text, right_text=right_text, entered_handler=entered_handler)
        
    def highscore_entered(self, mode, inits):
        # Override this
        self.logic.store_initials(key=self.active_prompt.key, inits=inits)
        self.remove_child_mode(self.highscore_entry) # same as *mode*
        self.celebrateIndex = 0
        self.celebrateCount = len(self.active_prompt.right)
        self.celebrate(inits)

    def celebrate(self,inits):
        self.game.sound.stop_music()
        run_length= self.game.sound.play('celebrate_player_jingle')
        
        #self.active_prompt.right[self.fanfareIndex].upper() 
        #info_layer = dmd.AnimatedTextLayer(128/2, 7, self.game.fonts['9x7_bold'], "center",4)
        info_layer = dmd.TextLayer(128/2, 0, self.game.fonts['30x13'], "center", opaque=False)
        info_layer.composite_op ="blacksrc"
        info_layer.set_text(inits,color=dmd.GREEN, blink_frames=2)
        
        bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
        #combine the parts together
        self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer, info_layer]) 
         
        self.celebrateIndex += 1
        if self.celebrateIndex == self.celebrateCount:
            #save the high score data - rewrite to make this database driven instead
            self.game.save_game_data()
            #queue cleanup
            self.delay(name='clean_up_hs_entry',delay=run_length,handler=self.clear)
        else:
            self.delay(delay = 2,handler=self.celebrate,param=inits)


    def clear(self):
        self.layer = None
        self.next()
                
                
                
  


class InitialEntryMode(game.Mode):
	"""Mode that prompts the player for their initials.

	*left_text* and *right_text* are strings or arrays to be displayed at the
	left and right corners of the display.  If they are arrays they will be
	rotated.

	:attr:`entered_handler` is called once the initials have been confirmed.

	This mode does not remove itself; this should be done in *entered_handler*."""

	entered_handler = None
	"""Method taking two parameters: `mode` and `inits`."""

	char_back = '<'
	char_done = '='
	
	max_inits = 3

	init_font = None
	font = None
	letters_font = None

	def __init__(self, game, priority, left_text, right_text, entered_handler):
		super(InitialEntryMode, self).__init__(game, priority)

		self.entered_handler = entered_handler
                self.log = logging.getLogger('ij.high_score_entry')
                
                #sound setup
                self.game.sound.register_music('hs_entry_music', music_path+"raiders_march.aiff")
                self.game.sound.register_sound('initial_letter_move', sound_path+"swipe_1.aiff")
                self.game.sound.register_sound('initial_letter_enter', sound_path+"match_success.aiff")
                self.game.sound.register_sound('celebrate_player_jingle', sound_path+"ij400A8_jones_jingle.aiff")
                self.game.sound.register_sound('well_done', speech_path+"well_done_my_friend.aiff")
                

		if type(right_text) != list:
			right_text = [right_text]
		if type(left_text) != list:
			left_text = [left_text]
		
		self.left_text = ', '.join(left_text)
		self.right_text = ', '.join(right_text)
		
		self.letters = []
		for idx in range(26):
			self.letters += [chr(ord('A')+idx)]
		self.letters += [' ', '.', self.char_back]
		self.current_letter_index = 0
		self.inits = ''
		
		self.animate_to_index(0)

	def animate_to_index(self, new_index, inc = 0):
		self.current_letter_index = new_index
		self.load_display()


	def load_display(self):
		inits = self.inits + self.letters[self.current_letter_index]
                #only way i can currentyl work out how to get the player id in here?? wtf...
                data = self.left_text.split(' ')
                player_id = int(data[1])-1
                score = locale.format("%d",self.game.players[player_id].score , True) #
                #store initials in a place hs server class can access - future inclusion
                self.game.last_entered_inits = inits
                self.log.debug('returning inits:%s', inits)
                bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/hs_entry_bgnd.dmd").frames[0])
                title_layer = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text(self.right_text.upper(),color=dmd.ORANGE)
                player_layer = dmd.TextLayer(30, 10, self.game.fonts['5px_az'], "left", opaque=False).set_text(self.left_text.upper(),color=dmd.CYAN)
                inits_layer = dmd.TextLayer(70, 8, self.game.fonts['9x7_bold'], "left", opaque=False).set_text(inits,color=dmd.GREEN,blink_frames=10)
                score_layer = dmd.TextLayer(64, 20, self.game.fonts['9px_az'], "center", opaque=False).set_text(score,color=dmd.BROWN)
                # combine the parts together
                self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,title_layer,player_layer,inits_layer,score_layer])
                
                
	def letter_increment(self, inc):
		new_index = (self.current_letter_index + inc)
		if new_index < 0:
			new_index = len(self.letters) + new_index
		elif new_index >= len(self.letters):
			new_index = new_index - len(self.letters)
                self.game.sound.play('initial_letter_move')
		self.animate_to_index(new_index, inc)


	def letter_accept(self):
		letter = self.letters[self.current_letter_index]
                self.game.sound.play('initial_letter_enter')
		if letter == self.char_back:
			if len(self.inits) > 0:
				self.inits = self.inits[:-1]
				if len(self.inits) == 0:
					self.current_letter_index = 0
		elif letter == self.char_done or len(self.inits) > 10: # We don't use the done character anymore, but if we did...
			if self.entered_handler != None:
				self.entered_handler(mode=self, inits=self.inits)
			else:
				self.game.logger.warning('InitialEntryMode finished but no entered_handler to notify!')
			return
		else:
			self.inits += letter
			if len(self.inits) == self.max_inits:
				if self.entered_handler != None:
					self.entered_handler(mode=self, inits=self.inits) 
				else:
					self.game.logger.warning('InitialEntryMode finished but no entered_handler to notify!')
                                
                                return
		self.letter_increment(0)
                
                

	def sw_flipperLwL_active(self, sw):
		self.periodic_left()
		return procgame.game.SwitchStop

	def sw_flipperLwL_inactive(self, sw):
		self.cancel_delayed('periodic_movement')

	def sw_flipperLwR_active(self, sw):
		self.periodic_right()
		return procgame.game.SwitchStop

	def sw_flipperLwR_inactive(self, sw):
		self.cancel_delayed('periodic_movement')

	def periodic_left(self):
		self.letter_increment(-1)
		self.delay(name='periodic_movement', event_type=None, delay=0.2, handler=self.periodic_left)
	def periodic_right(self):
		self.letter_increment(1)
		self.delay(name='periodic_movement', event_type=None, delay=0.2, handler=self.periodic_right)

	def sw_startButton_active(self, sw):
		self.letter_accept()
		return procgame.game.SwitchStop
