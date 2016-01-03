# Volume Adjustment


import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Volume(game.Mode):

	def __init__(self, game):
            super(Volume, self).__init__(game, 100)
            
            self.log = logging.getLogger('ij.volume')
            self.game.sound.register_music('volume_adjust_play', music_path+"shooter_groove.aiff")
            
            self.volume_level = self.game.user_settings['Sound']['Initial Volume'] 
            self.volume_level_max = 38
            #update the sound mode
            self.game.sound.music_volume_offset = 0.0
            self.game.sound.set_volume(float(self.volume_level)/float(self.volume_level_max)) 
            
            self.timer = 3 # timer to clear display if no inputs
            self.music_playing = False
            

        def adjust(self,value):

            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/volume_bgnd.dmd").frames[0])
            bgnd_layer.composite_op="blacksrc"
            info_layer = dmd.TextLayer(128/2, 8, self.game.fonts['07x5'], "center")
            info_layer.composite_op="blacksrc"

            self.play_music()
            
            #update the volume level
            self.volume_level +=value
            #make the sound adjustment
            self.log.info(float(self.volume_level)/float(self.volume_level_max))
            self.game.sound.set_volume(float(self.volume_level)/float(self.volume_level_max)) 
            
            
            
                
            bar_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/volume_bar.dmd").frames[0])
            #bar_layer.x = 2
            #bar_layer.y = 6
            bar_layer.target_y = 15
            bar_layer.target_x = 6
            bar_layer.composite_op="blacksrc"
            layer_group = [bgnd_layer,info_layer,bar_layer]
            next_bar_layer = []
            
            x_posn=9
            for i in range(self.volume_level):
                #set the volume bar colour
                if i<26:
                    frame_num=0 #green
                elif i<34:
                    frame_num=1 #yellow
                else:
                    frame_num =2 #red
                
                next_bar_layer.append(dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/volume_bar.dmd").frames[frame_num]))
                #next_bar_layer[i] = bar_layer
                next_bar_layer[i].target_x=x_posn
                next_bar_layer[i].target_y=bar_layer.target_y
                next_bar_layer[i].composite_op="blacksrc"
                layer_group.append(next_bar_layer[i])
                x_posn+=3
                
            info_layer.set_text('VOLUME '+str(self.volume_level),color=dmd.CYAN)

            #update display layer
            #self.log.info(layer_group)
            self.layer = dmd.GroupedLayer(128, 32, layer_group)
            
            #update stored settings
            self.game.user_settings['Sound']['Initial Volume']=self.volume_level
            self.game.save_settings()


            self.delay(name='no_input_clear_delay', event_type=None, delay=self.timer, handler=self.clear)


        def clear(self):
            self.play_music(False)
            self.layer = None
            
        def play_music(self,enable=True):
            if enable:
                #play music
                if not self.music_playing:
                    self.game.sound.play_music('volume_adjust_play', loops=-1)
                    self.music_playing = True
            else:
                if self.game.ball>0:
                    self.game.utility.resume_mode_music()
                else:
                    self.game.sound.stop_music()
                self.music_playing = False
                
            
            
        # Outside of the service mode, up/down control audio volume.
	def sw_down_active(self, sw):
                self.cancel_delayed('no_input_clear_delay')
                if self.volume_level>0:
                    self.adjust(-1)
		
                #volume = int(self.game.sound.volume_down())
		#self.game.set_status("Volume Down : " + str(volume*10)+"%")
		#return True

	def sw_up_active(self, sw):
                self.cancel_delayed('no_input_clear_delay')
                if self.volume_level<self.volume_level_max:
                    self.adjust(1)
                
		#volume = int(self.game.sound.volume_up())
		#self.game.set_status("Volume Up : " + str(volume*10)+"%")
		#return True
                