# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Extra_Ball(game.Mode):

	def __init__(self, game):
            super(Extra_Ball, self).__init__(game, 90)

            self.game.sound.register_sound('extra_ball_collected', sound_path+"extra_ball_collected_ff.aiff")
            self.game.sound.register_sound('extra_ball_lit', sound_path+"extra_ball_lit_ff.aiff")
            self.game.sound.register_sound('extra_ball_speech', speech_path+"extra_ball.aiff")


        def collect(self,play_anim=True):
            print("Extra Ball Collected")
            if play_anim:
                anim = dmd.Animation().load(game_path+"dmd/extra_ball.dmd")
                self.collect_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=6)
                self.collect_layer.add_frame_listener(-1, self.collect_cleanup)
                self.layer=self.collect_layer
                
            self.game.sound.play('extra_ball_collected')
            #self.game.sound.play_voice('extra_ball_speech')
            self.game.effects.drive_lamp('extraBall','off')
            self.game.effects.drive_lamp('shootAgain','smarton')
            
            self.game.set_player_stats('extra_ball_lit',False)
            self.game.extra_ball_count()
            
            
            
        def collect_cleanup(self,wait=1):
            self.delay(name='eb_collect_cleanup',delay=wait,handler=self.clear)
            
        
        def clear(self):
            self.layer = None


        def lit(self,type='anim'):
            text = "EXTRA BALL LIT"
            text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            
            if type=='banner':
                text_layer.set_text(text,color=dmd.ORANGE)
                return text_layer
            elif type=='anim':
                text_layer.set_text(text,seconds=1.5,blink_frames=2,color=dmd.RED)
                self.layer = text_layer
                self.game.sound.play('extra_ball_lit')
                self.game.effects.drive_lamp('extraBall','smarton')
                
                #set player stats
                self.game.set_player_stats('extra_ball_lit',True)
                
                
        def update_lamps(self):
            if self.game.get_player_stats('extra_ball_lit'):
                self.game.effects.drive_lamp('extraBall','on')
            else:
                self.game.effects.drive_lamp('extraBall','off')
                
            p = self.game.current_player()
            
            if p.extra_balls>=1:
                self.game.effects.drive_lamp('shootAgain','on')
            else:
                self.game.effects.drive_lamp('shootAgain','off')
                
        
        #switch handlers
        def sw_grailEject_active_for_250ms(self,sw):
            if self.game.ball >0:
                if self.game.get_player_stats('extra_ball_lit'):
                    self.collect()
                