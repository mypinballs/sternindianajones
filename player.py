import procgame.game


class Player(procgame.game.Player):

        def __init__(self, name):
                super(Player, self).__init__(name)

                #create player stats
                self.player_stats = {}

                #set player stats defaults
                self.player_stats['status']=''
                self.player_stats['bonus_x']=1
                self.player_stats['bonus_mode_tracking']=[]
                self.player_stats['slingshot_hits']=0
                self.player_stats['friends_collected']=0
                self.player_stats['loops_completed']=0
                self.player_stats['loops_made']=0
                self.player_stats['loop_value']=1000000 #1M default
                self.player_stats['ramps_made']=0
                self.player_stats['super_pops_required']=100
                self.player_stats['super_pops_level']=1
                self.player_stats['dog_fight_running']=False
                self.player_stats['dog_fights_completed']=0
                self.player_stats['adventure_letters_collected']=0
                self.player_stats['adventures_started']=0
                self.player_stats['burps_collected']=0
                self.player_stats['soc_baskets_searched']=0
                self.player_stats['snakes_torched']=0
                self.player_stats['stones_collected']=0
                self.player_stats['rope_bridge_distance']=0
                self.player_stats['tank_chase_distance']=0
                self.player_stats['challenges_collected']=0
                self.player_stats['current_mode_num']=0
                self.player_stats['hof_status']='off'
                self.player_stats['mode_enabled']=False
                self.player_stats['mode_starting']=False
                self.player_stats['mode_running'] = False
                self.player_stats['mode_running_id'] = 99
                self.player_stats['mode_status_tracking']= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                #self.player_stats['mode_status_tracking']= [0,1,1,1,1,1,1,1,1,1,1,1,1,1] #for testing final adventure more easily
                self.player_stats['mode_blocking'] = False
                self.player_stats['mode_paused'] = False
                self.player_stats['film_set_flags'] = [0,0,0,0]
                self.player_stats['multiball_mode_started'] = False
                self.player_stats['path_mode_started'] = False
                self.player_stats['temple_mode_started'] = False
                self.player_stats['ark_mode_started'] = False
                self.player_stats['video_mode_started'] = False
                self.player_stats['lock_lit'] = False
                self.player_stats['lock_in_progress'] = False
                self.player_stats['lock_progress_hits'] =0
                self.player_stats['multiball_ready'] = False
                self.player_stats['multiball_started'] = False
                self.player_stats['multiball_running'] = False
                self.player_stats['quick_multiball_ready'] = False
                self.player_stats['quick_multiball_started'] = False
                self.player_stats['quick_multiball_running'] = False
                self.player_stats['qm_jackpots_collected'] = 0
                self.player_stats['jackpots_collected'] = 0
                self.player_stats['super_qm_qualified'] = False
                self.player_stats['super_quick_multiball_started'] = False
                self.player_stats['super_quick_multiball_running'] = False
                self.player_stats['cheat_count'] = 0
                self.player_stats['treasures_collected']=0
                self.player_stats['balls_locked'] = 0
                self.player_stats['pit_value'] = 0
                self.player_stats['indy_lanes_flag']= [False,False,False,False]
                self.player_stats['indy_lanes_letters_spotted'] = 0
                self.player_stats['poa_flag']= [False,False,False,False,False,False,False,False,False]
                self.player_stats['poa_queued'] = False
                self.player_stats['poa_enabled'] = False
                self.player_stats['adventure_letters_spotted']=0
                self.player_stats['adventure_paused'] = False
                self.player_stats['adventure_started'] = False
                self.player_stats['adventure_continuing'] = False
                self.player_stats['last_mode_score']=0
                self.player_stats['get_the_idol_score']=0
                self.player_stats['castle_grunwald_score']=0
                self.player_stats['monkey_brains_score']=0
                self.player_stats['streets_of_cairo_score']=0
                self.player_stats['well_of_souls_score']=0
                self.player_stats['steal_the_stones_score']=0
                self.player_stats['rope_bridge_score']=0
                self.player_stats['the_three_challenges_score']=0
                self.player_stats['werewolf_score']=0
                self.player_stats['mine_cart_score']=0
                self.player_stats['choose_wisely_level']=1#int(self.game.user_settings['Gameplay (Feature)']['Choose Wisely Level Start'])
                self.player_stats['moonlight_total']=0
                self.player_stats['moonlight_status']=False
                self.player_stats['extra_ball_lit']=False
                self.player_stats['map_banks_completed']=0
                self.player_stats['jva_ships_destroyed'] = 0
                self.player_stats['jva_smart_bombs'] = 0
                self.player_stats['jones_vs_aliens_score'] = 0
                self.player_stats['warehouse_items_collected']=0
                self.player_stats['warehouse_raid_score']=0
                self.player_stats['skull_face_stones_removed']=0
                self.player_stats['return_the_skull_score']=0
                self.player_stats['nuke_test_score']=0
                self.player_stats['frankenstein_sets_completed'] = 0
                self.player_stats['frankenstein_millions_score'] = 0
                self.player_stats['music_playing'] = False
                self.player_stats['loopin_jackpots_collected'] = 0
                self.player_stats['ark_hits'] = 0
                self.player_stats['jones_banks_completed'] = 0
                self.player_stats['jones_flags']= [False,False,False,False,False]
                self.player_stats['8ball_multiball_lit'] = False
                self.player_stats['final_adventure_total']=0
                self.player_stats['final_adventure_status']=False
                self.player_stats['final_adventure_started']=False
                self.player_stats['spinner_level']=0
                self.player_stats['ringmasters_defeated'] = 0
                self.player_stats['ringmaster_smart_bombs'] = 0
                self.player_stats['ringmaster_score'] = 0
                self.player_stats['skillshot_level'] = 1
                self.player_stats['adventure_flags']= [False,False,False,False,False,False]
                self.player_stats['adventure_smart_bombs'] = 0
                self.player_stats['trough_issue_count'] = 0
                self.player_stats['ball_start_score'] = 0
