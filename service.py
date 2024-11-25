import logging
import locale
import audits
import os
import sys
import glob
import pwd
import grp
       
import shutil
from procgame import *
from distutils import dir_util

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones2/"
#proc_path = base_path+"pyprocgame/procgame/"
import procgame
proc_path = procgame.__file__[:-13]
speech_path = game_path +"speech/"
sound_path = game_path +"sound/service/"
music_path = game_path +"music/"

class ServiceModeSkeleton(game.Mode):
        """Service Mode List base class."""
        def __init__(self, game, priority, font):
                super(ServiceModeSkeleton, self).__init__(game, priority)
                self.log = logging.getLogger('ij.service')
                self.name = ""
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_bgnd.dmd').frames[0])
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
                self.item_layer = dmd.TextLayer(1, 11, self.game.fonts['8x6'], "left")
                self.instruction_layer = dmd.TextLayer(1, 25, font, "left")
                self.instruction_layer.composite_op = "blacksrc"
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.instruction_layer])
                self.no_exit_switch = game.machine_type == 'sternWhitestar'

        def mode_started(self):
                self.title_layer.set_text(str(self.name))
                self.game.sound.play('service_enter')

        def mode_stopped(self):
                self.game.sound.play('service_exit')

        def disable(self):
                pass

        def sw_down_active(self, sw):
                if self.game.switches.enter.is_active():
                        self.game.modes.remove(self)
                        return True

        def sw_exit_active(self, sw):
                self.game.modes.remove(self)
                #restart the lamp show if exiting out of the service mode front
                if self.name.find(self.game.system_version)>0:
                    self.game.attract_mode.change_lampshow()                    
                return True

class ServiceModeList(ServiceModeSkeleton):
        """Service Mode List base class."""
        def __init__(self, game, priority, font):
                super(ServiceModeList, self).__init__(game, priority, font)
                self.items = []

        def mode_started(self):
                super(ServiceModeList, self).mode_started()

                self.iterator = 0
                self.change_item()

        def change_item(self):
                ctr = 0
                for item in self.items:
                        if (ctr == self.iterator):
                                self.item = item
                        ctr += 1
                self.max = ctr - 1
                self.item_layer.set_text(str(self.iterator+1)+') '+str(self.item.name))

        def sw_up_active(self,sw):
                if self.game.switches.enter.is_inactive():
                        self.item.disable()
                        if (self.iterator < self.max):
                                self.iterator += 1
                        else:
                            self.iterator =0
                        self.game.sound.play('service_next')
                        self.change_item()
                return True

        def sw_down_active(self,sw):
                if self.game.switches.enter.is_inactive():
                        self.item.disable()
                        if (self.iterator > 0):
                                self.iterator -= 1
                        else:
                            self.iterator =self.max
                        self.game.sound.play('service_previous')
                        self.change_item()
                elif self.no_exit_switch:
                        self.exit()
                return True

        def sw_enter_active(self,sw):
                self.game.modes.add(self.item)
                return True

        def exit(self):
                self.item.disable()
                self.game.modes.remove(self)
                return True


class ServiceMode(ServiceModeList):
        """Service Mode."""
        def __init__(self, game, priority, font,big_font, extra_tests=[]):
                super(ServiceMode, self).__init__(game, priority,font)
                #self.title_layer.set_text('Service Mode')
                
                #setup sounds
                self.game.sound.register_sound('service_enter', sound_path+"menu_enter.wav")
                self.game.sound.register_sound('service_exit', sound_path+"menu_exit.wav")
                self.game.sound.register_sound('service_next', sound_path+"menu_up.wav")
                self.game.sound.register_sound('service_previous', sound_path+"menu_down.wav")
                self.game.sound.register_sound('service_switch_edge', sound_path+"menu_switch_edge.wav")
                self.game.sound.register_sound('service_save', sound_path+"menu_save.wav")
                self.game.sound.register_sound('service_cancel', sound_path+"menu_cancel.wav")
                self.game.sound.register_sound('service_reject', sound_path+"menu_reject.wav")
                self.game.sound.register_sound('service_alert', sound_path+"service_alert.aiff")
                self.game.sound.register_sound('service_start', sound_path+"service_startup.aiff")
                
                self.name = 'Service Mode - OS v'+str(self.game.system_version)
                self.tests = Tests(self.game, self.priority+1, font, big_font, extra_tests)
                self.items = [self.tests]
                if len(self.game.settings) > 0: 
                        self.settings = Settings(self.game, self.priority+1, font, big_font, 'Settings', self.game.settings)
                        self.items.append(self.settings)


                #if len(self.game.game_data) > 0: 
                self.statistics = Statistics(self.game, self.priority+1, font, big_font, 'Statistics', self.game.game_data)
                self.items.append(self.statistics)
                
                self.utilities = Utilities(self.game, self.priority+1, font, big_font, 'Utilities')
                self.items.append(self.utilities)
                        
                        
class Tests(ServiceModeList):
        """Service Mode."""
        def __init__(self, game, priority, font, big_font, extra_tests=[]):
                super(Tests, self).__init__(game, priority,font)
                #self.title_layer.set_text('Tests')
                self.name = 'Tests'
                self.lamp_test = LampTest(self.game, self.priority+1, font, big_font)
                self.coil_test = CoilTest(self.game, self.priority+1, font, big_font)
                self.ark_test = ArkTest(self.game, self.priority+1, font, big_font)
                self.swordsman_test = SwordsmanTest(self.game, self.priority+1, font, big_font)
                self.trough_test = TroughTest(self.game, self.priority+1, font, big_font)
                self.switch_test = SwitchTest(self.game, self.priority+1, font, big_font)
                self.items = [self.switch_test, self.lamp_test, self.coil_test,self.ark_test,self.swordsman_test,self.trough_test]
                for test in extra_tests:
                        self.items.append(test)

                
class LampTest(ServiceModeList):
        """Lamp Test"""
        def __init__(self, game, priority, font, big_font):
                super(LampTest, self).__init__(game, priority,font)
                #set mode name
                self.name = "Lamp Test"

                #set layers
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_bgnd.dmd').frames[0])
                self.matrix_grid_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/stern_lamp_test_grid.dmd').frames[0])
                self.matrix_grid_layer.composite_op = "blacksrc"
                self.matrix_grid_layer.target_x = 100
                self.matrix_grid_layer.target_y = 0
                #self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
                #self.matrix_layer.composite_op = "blacksrc"
                #self.matrix_layer.target_x = 128
                #self.matrix_layer.target_y = 32
                self.matrix_layer_group = []
                self.matrix_layer = dmd.GroupedLayer(128, 32, self.matrix_layer_group)
                self.matrix_layer.composite_op = "blacksrc"
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
                self.instruction_layer = dmd.TextLayer(45, 0, font, "left")
                self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
                self.drive_layer = dmd.TextLayer(1, 24, font, "left")
                self.wire_layer = dmd.TextLayer(1, 18, self.game.fonts['7x4'], "left")
                self.number_layer = dmd.TextLayer(99, 24, font, "right")
                self.conn_layer = dmd.TextLayer(100, 24, font, "right")
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.instruction_layer,self.item_layer,self.conn_layer,self.wire_layer,self.drive_layer,self.number_layer,self.conn_layer,self.matrix_grid_layer,self.matrix_layer])

                self.lamp_index = []
                self.row_max = 10
                self.col_max = 8
                
                #connector setup
                self.base_colour =['Red','Yellow']
                self.connector_key = [7,2]
                self.connections=['J12','J13']
                self.lamp_row_transistor = []
                self.lamp_col_ic = []
        
                
                for r in range(33,43):
                    self.lamp_row_transistor.append(r)
                for c in reversed(range(10,18)):
                    self.lamp_col_ic.append(c)    
                    
                self.log.debug("Row Transistors:%s",self.lamp_row_transistor)
                self.log.debug("Col ICs:%s",self.lamp_col_ic)

                #populate connector colours
                for j in range (len(self.base_colour)):
                    self.colours = ['Brown','Red','Orange','Yellow','Green','Blue','Purple','Grey','White','No Stripe']
                    colour_set = self.colours
                    #colour_set.pop(self.connector_key[j]-1)
                    for i in range(len(colour_set)):
                        if colour_set[i]==self.base_colour[j]:
                         colour_set[i] = "Black"
                    if j==0:
                        self.row_colour = colour_set
                    elif j==1:
                        self.col_colour = colour_set

                #setup the full lamp item list
                self.items = sorted(self.game.lamps.items_not_tagged('gi'),key=lambda item: item.yaml_number)
                
                #setup for row/col tests
                self.row_test_num = 1 #default
                self.row_lamps = self.items[(self.row_test_num*8)-8:self.row_test_num*8]
                for item in self.row_lamps:
                    self.log.debug("ROW Test lamps: %s,%s",item.yaml_number,item.label)
              
                self.col_items = sorted(self.game.lamps.items_not_tagged('gi'),key=lambda item: item.number)
                self.col_test_num = 1 #default
                self.col_lamps = self.col_items[(self.col_test_num*10)-10:self.col_test_num*10]
                for item in self.col_lamps:
                    self.log.debug("COL Test lamps: %s,%s",item.yaml_number,item.label)
                

        def mode_started(self):
                self.action = 'repeat'
                self.instruction_layer.set_text(' - Repeat')
                
                super(LampTest, self).mode_started()
        
                self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)

        def mode_stopped(self):
                self.cancel_delayed('repeat')

        def change_item(self):
                super(LampTest, self).change_item()
                #self.log.debug("items total:"+str(len(self.items)))
                ctr = 0
                for item in self.items:
                    if (ctr == self.iterator) and item.yaml_number.count('L')>0:
                        self.item = item

                    ctr += 1
                    #self.log.debug("Lamp:%s %s",item.label,item.yaml_number)

                self.set_matrix()
        
        #special change method for column test as list is in different order
        def change_col_item(self):
                super(LampTest, self).change_item()
                #self.log.debug("items total:"+str(len(self.items)))
                ctr = 0
                for item in self.col_items:
                    if (ctr == self.iterator) and item.yaml_number.count('L')>0:
                        self.item = item

                    ctr += 1
                    #self.log.debug("Lamp:%s %s",item.label,item.yaml_number)

                self.set_matrix()

        def process_repeat(self):
            self.change_item()
            self.item.schedule(schedule=0x00ff00ff, cycle_seconds=2, now=True)
            self.set_matrix()
            self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_repeat)
            
        def process_auto(self):
                if (self.action == 'repeat'):
                    self.item.schedule(schedule=0x00ff00ff, cycle_seconds=2, now=True)
                    self.set_matrix()
                elif (self.action == 'auto'):
                    self.item.schedule(schedule=0x00ff00ff, cycle_seconds=2, now=True)
                    self.change_item()
                    if (self.iterator < self.max):
                        self.iterator += 1
                    else:
                        self.iterator =0
                elif (self.action == 'all'):
                    self.iterator =0
                    for item in self.items:
                        item.schedule(schedule=0x00ff00ff, cycle_seconds=2, now=True)
                        self.change_item()
                        if (self.iterator < self.max):
                            self.iterator += 1
                        else:
                            self.iterator =0
                elif (self.action=='row'):
                    self.row_lamps = self.items[(self.row_test_num*8)-8:self.row_test_num*8]
                    for item in self.row_lamps:
                        item.schedule(schedule=0x00ff00ff, cycle_seconds=2, now=True)
                        self.change_item()
                        if (self.iterator < self.max):
                            self.iterator += 1
                        else:
                            self.iterator =0
                    self.row_test_num+=1
                    if (self.row_test_num <= 8):
                        self.row_test_num += 1
                    else:
                        self.row_test_num =1
                elif (self.action=='col'):
                    self.col_lamps = self.col_items[(self.col_test_num*10)-10:self.col_test_num*10]
                    for item in self.col_lamps:
                        item.schedule(schedule=0x00ff00ff, cycle_seconds=2, now=True)
                        self.change_col_item()
                        if (self.iterator < self.max):
                            self.iterator += 1
                        else:
                            self.iterator =0
                    self.col_test_num+=1
                    if (self.col_test_num <= 8):
                        self.col_test_num += 1
                    else:
                        self.col_test_num =1
                            
                self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)

        
#        def set_all_matrix(self):
#            self.item_layer.set_text('ALL LAMPS',color=dmd.YELLOW)
#            self.wire_layer.set_text('')
#            self.drive_layer.set_text('')
#            self.conn_layer.set_text('')
#            self.matrix_layer.target_x = 102
#            self.matrix_layer.target_y = 2
            
            #clear matrix display after set time
            #self.delay(name='clear_matrix', event_type=None, delay=1, handler=self.clear_matrix)
            
        def set_matrix(self):
            
            if self.item.yaml_number.count('L')>0:
                    matrix =[]
                    lamp_num = int(self.item.yaml_number[1:])-1
                    matrix.append(lamp_num/8)
                    matrix.append(lamp_num%8)
                    self.log.debug("Lamp Matrix for lamp %s :%s",self.item.yaml_number,matrix)
                    
                    row_colour = self.base_colour[0]+'/'+self.row_colour[matrix[0]]                
                    col_colour = self.base_colour[1]+'/'+self.col_colour[matrix[1]]
                    
                    pin_row = matrix[0]+1
                    if pin_row>=self.connector_key[0]:
                        pin_row-=1
                    
                    pin_col = 9-matrix[1]
                    if pin_row>=self.connector_key[1]:
                        pin_col+=1

                    #update matrix to show active coil
                    #self.matrix_layer.target_x = 102+int(matrix[1])*3
                    #self.matrix_layer.target_y = 2+int(matrix[0])*3
                   
                    matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
                    matrix_layer.composite_op = "blacksrc"
                    matrix_layer.target_x = 128
                    matrix_layer.target_y = 32
                    matrix_layer.target_x = 102+int(matrix[1])*3
                    matrix_layer.target_y = 2+int(matrix[0])*3
                    
                    self.matrix_layer_group.append(matrix_layer)
                    self.lamp_index.append(lamp_num)
                    self.log.debug('Lamp Index:%s',self.lamp_index)
                        
                    #set text for the layers
                    if self.action=='all':
                        self.item_layer.set_text('ALL LAMPS',color=dmd.YELLOW)
                        self.wire_layer.set_text('')
                        self.drive_layer.set_text('')
                        self.conn_layer.set_text('')
                    elif self.action=='row':
                        self.item_layer.set_text('ROW RETURNS',color=dmd.YELLOW)
                        self.wire_layer.set_text(str(row_colour),color = dmd.BROWN)
                        self.drive_layer.set_text("Q"+str(self.lamp_row_transistor[matrix[0]]),color=dmd.CYAN)
                        self.conn_layer.set_text(str(self.connections[0])+"-"+str(pin_row),color=dmd.GREEN)
                    elif self.action=='col':
                        self.item_layer.set_text('COL DRIVES',color=dmd.YELLOW)
                        self.wire_layer.set_text(str(col_colour),color = dmd.BROWN)
                        self.drive_layer.set_text("IC-U"+str(self.lamp_col_ic[matrix[1]]),color=dmd.CYAN)
                        self.conn_layer.set_text(str(self.connections[1])+"-"+str(pin_col),color=dmd.GREEN)
                    else:
                        self.item_layer.set_text(self.item.label,color=dmd.YELLOW)
                        self.wire_layer.set_text(str(row_colour)+" "+str(col_colour),color = dmd.BROWN)
                        self.drive_layer.set_text("Q"+str(self.lamp_row_transistor[matrix[0]])+" IC-U"+str(self.lamp_col_ic[matrix[1]]),color=dmd.CYAN)
                        self.conn_layer.set_text(str(self.connections[0])+"-"+str(pin_row)+" "+str(self.connections[1])+"-"+str(pin_col),color=dmd.GREEN)

                    #clear matrix display after set time
                    self.delay(name='clear_matrix', event_type=None, delay=1, handler=lambda:self.clear_matrix(matrix_layer,lamp_num))


        def clear_matrix(self,layer,lamp_num):
            layer.target_x = 128
            layer.target_y = 32
            index = self.lamp_index.index(lamp_num)
            self.matrix_layer_group.pop(index)
            self.lamp_index.pop(index)


        def sw_enter_active(self,sw):
                if (self.action == 'manual'):
                        self.action = 'repeat'
                        self.instruction_layer.set_text(' - Repeat')
                elif (self.action == 'repeat'):
                        self.action = 'auto'
                        self.instruction_layer.set_text(' - Auto')
                elif (self.action == 'auto'):
                        self.action = 'all'
                        self.instruction_layer.set_text(' - All')
                elif (self.action == 'all'):
                        self.action = 'row'
                        self.instruction_layer.set_text(' - Row')
                        self.iterator = 0
                elif (self.action == 'row'):
                        self.action = 'col'                  
                        self.instruction_layer.set_text(' - Column')
                        self.iterator = 0
                elif (self.action == 'col'):
                        self.action = 'manual'
                        self.instruction_layer.set_text(' - Manual')
                return True

        def sw_startButton_active(self,sw):
                if (self.action == 'manual'):
                        self.item.schedule(schedule=0x00ff00ff, cycle_seconds=2, now=True)
                        self.set_matrix()
                return True


class CoilTest(ServiceModeList):
        """Coil Test"""
        def __init__(self, game, priority, font, big_font):
                super(CoilTest, self).__init__(game, priority, font)
                #set mode name
                self.name = "Coil Test"

                #setup layers
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_bgnd.dmd').frames[0])
                self.matrix_grid_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/stern_coil_test_grid.dmd').frames[0])
                self.matrix_grid_layer.composite_op = "blacksrc"
                self.matrix_grid_layer.target_x = 101
                self.matrix_grid_layer.target_y = 1
                self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
                self.matrix_layer.composite_op = "blacksrc"
                self.matrix_layer.target_x = 128
                self.matrix_layer.target_y = 32
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
                self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
                self.wire_layer = dmd.TextLayer(1, 18, font, "left")
                self.instruction_layer = dmd.TextLayer(45, 0, font, "left")
                self.board_layer = dmd.TextLayer(1, 18, font, "left")
                self.drive_layer = dmd.TextLayer(1, 24, font, "left")
                self.conn_layer = dmd.TextLayer(100, 24, font, "right")
                
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.item_layer,self.wire_layer,self.board_layer,self.drive_layer,self.conn_layer,self.instruction_layer,self.matrix_grid_layer,self.matrix_layer])

                #connector setup
                self.bank_colours = ['Brown','Blue','Purple','Black','Orange']
                self.connector_key =[2,3,1,9,4]
                self.connections=['J8','J9','J7','J6','J2']
                self.wire_colour = []
                
                #populate connector colours
                for j in range (len(self.bank_colours)):
                    self.colours = ['Brown','Red','Orange','Yellow','Green','Blue','Purple','Grey','White']
                    colour_set = self.colours
                    #colour_set.pop(self.connector_key[j]-1)
                    for i in range(len(colour_set)):
                        if colour_set[i]==self.bank_colours[j]:
                            colour_set[i] = "Black"
                    
                    self.wire_colour.append(colour_set)
                             
                self.log.debug("Coil Wire Colours Created:%s",self.wire_colour)

                self.items = sorted(self.game.coils,key=lambda item: item.number) #self.game.coils   
                
                self.max = len(self.items)
                self.log.debug("Max:"+str(self.max))


        def mode_started(self):
                super(CoilTest, self).mode_started()
                self.action = 'manual'
                self.instruction_layer.set_text(' - Manual')

                #check this line is needed
                if self.game.lamps.has_key('start'): self.game.lamps.start.schedule(schedule=0xff00ff00, cycle_seconds=0, now=False)

                self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)


        def mode_stopped(self):
                self.cancel_delayed('repeat')


        def change_item(self):
                self.log.debug("items total:"+str(len(self.items)))
                ctr = 0
                for item in self.items:
                    if (ctr == self.iterator):
                        self.item = item

                    ctr += 1
                    self.log.debug("item:%s %s",item.label,item.yaml_number)

                self.set_matrix()
                
                
        def process_auto(self):
                if (self.action == 'repeat'):
                    self.item.pulse()
                    self.set_matrix()
                elif (self.action == 'auto'):
                    self.change_item()
                    self.item.pulse()
                    self.set_matrix()
                    if (self.iterator < self.max):
                        self.iterator += 1
                    else:
                        self.iterator =0
                self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)


        def set_matrix(self):
            #update matrix to show active coil
            num =self.item.number-32
            #fix for aux mappings on stern driver
            if self.item.number>=72:
                num =self.item.number-39
                
            coil_num = num+1
            self.log.debug('coil number:%s coil name:%s',self.item.number,self.item.name)
           
            bank= num/8
            drive = num%8
            pin_num = drive+1
            self.log.debug('coil bank:%s coil drive:%s',bank,drive)
            if pin_num>=self.connector_key[bank]:
                pin_num+=1
                
            self.matrix_layer.target_x = 103+(bank*5)
            self.matrix_layer.target_y = 8+(drive*3)
            
            wire_colour = str(self.bank_colours[bank])+'/'+str(self.wire_colour[bank][drive])
            
            if coil_num<=32:
                self.drive_layer.set_text("Q"+str(coil_num)+" Sol "+str(coil_num),color=dmd.CYAN)
            else: #auxiliary drivers
                self.drive_layer.set_text("B"+str(num-32)+ " (Data) Sol "+str(coil_num),color=dmd.CYAN)
            self.conn_layer.set_text(str(self.connections[bank])+"-"+str(pin_num),color=dmd.GREEN)
            self.item_layer.set_text(self.item.label,color=dmd.YELLOW)       
            self.wire_layer.set_text(wire_colour,color=dmd.BROWN)
            
            #clear matrix display after set time
            self.delay(name='clear_matrix', event_type=None, delay=1, handler=self.clear_matrix)


        def clear_matrix(self):
            self.matrix_layer.target_x = 128
            self.matrix_layer.target_y = 32


        def sw_enter_active(self,sw):
                if (self.action == 'manual'):
                        self.action = 'repeat'
                        if self.game.lamps.has_key('start'): self.game.lamps.start.disable()
                        self.instruction_layer.set_text(' - Repeat')
                elif (self.action == 'repeat'):
                        self.action = 'auto'
                        if self.game.lamps.has_key('start'): self.game.lamps.start.disable()
                        self.instruction_layer.set_text(' - Auto')
                elif (self.action == 'auto'):
                        self.action = 'manual'
                        if self.game.lamps.has_key('start'): self.game.lamps.start.schedule(schedule=0xff00ff00, cycle_seconds=0, now=False)
                        self.instruction_layer.set_text(' - Manual')
                        #self.cancel_delayed('repeat')
                return True

        def sw_startButton_active(self,sw):
                if (self.action == 'manual'):
                        self.item.pulse(20)
                        self.set_matrix()
                return True

class SwitchTest(ServiceModeSkeleton):
        """Switch Test"""
        def __init__(self, game, priority, font, big_font):
                super(SwitchTest, self).__init__(game, priority,font)
                self.name = "Switch Test"
                #layer setup
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_bgnd.dmd').frames[0])
                self.matrix_grid_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/stern_switch_test_grid.dmd').frames[0])
                self.matrix_grid_layer.composite_op = "blacksrc"
                self.matrix_grid_layer.target_x = 78
                self.matrix_grid_layer.target_y = 1
                self.matrix_layer_group = []
                self.matrix_layer = dmd.GroupedLayer(128, 32, self.matrix_layer_group)
                self.matrix_layer.composite_op = "blacksrc"
                self.direct_matrix_layer_group = []
                self.direct_matrix_layer = dmd.GroupedLayer(128, 32, self.direct_matrix_layer_group)
                self.direct_matrix_layer.composite_op = "blacksrc"
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
                self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
                self.row_layer = dmd.TextLayer(1, 18, font, "left")
                self.column_layer = dmd.TextLayer(1, 24, font, "left")
                self.number_layer = dmd.TextLayer(78, 24, font, "left")
                
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.item_layer, self.row_layer,self.column_layer,self.number_layer,self.matrix_grid_layer,self.matrix_layer,self.direct_matrix_layer])
                
                #grid indexes setup
                self.switch_index = []
                self.direct_switch_index = []
                
                #connector setup
                self.base_colour =['White','Brown','Green','Pink','Grey','Light Green']
                self.connector_key = [4,5,2,5,3,2]
                self.wire_colour = []
                
                #populate connector colours
                for j in range (len(self.base_colour)):
                    self.colours = ['Brown','Red','Orange','Yellow','Green','Blue','Purple','Grey','White']
                    colour_set = self.colours
                    colour_set.pop(self.connector_key[j]-1)
                    for i in range(len(colour_set)):
                        if colour_set[i]==self.base_colour[j]:
                         colour_set[i] = "Black"
                    
                    self.wire_colour.append(colour_set)
                             
                self.log.debug("Wire Colours Created:%s",self.wire_colour)
               
                #self.direct_colours = ['Green','Brown','Red','Orange','Yellow','Black','Blue','Purple','Grey','Green','','']
                
                for switch in self.game.switches:
                        if self.game.machine_type == 'sternWhitestar':
                                add_handler = 1
                        elif switch != self.game.switches.exit:
                                add_handler = 1
                        else:
                                add_handler = 0
                        if add_handler:
                            self.add_switch_handler(name=switch.name, event_type='inactive', delay=None, handler=self.switch_handler)
                            self.add_switch_handler(name=switch.name, event_type='active', delay=None, handler=self.switch_handler)
                            self.log.debug("Added Switch:%s",switch.name)
                       
                            
        def mode_started(self):
            super(SwitchTest, self).mode_started()
            for switch in self.game.switches:
                if switch.is_active():
                    self.switch_handler(switch)
                    self.log.debug("Active Switch:%s",switch.name)
                    
                    
        def switch_handler(self, sw):
                if (sw.state):
                    self.game.sound.play('service_switch_edge')
                
                matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
                matrix_layer.composite_op = "blacksrc"
                matrix_layer.target_x = 128
                matrix_layer.target_y = 32
                
                self.item_layer.set_text(str(sw.label),color=dmd.YELLOW)

                x_offset = 80
                
                if sw.yaml_number.count('S')>0 and sw.yaml_number.count('D')==0 and sw.yaml_number.count('F')==0:
                    
                    matrix =[]
                    sw_num = int(sw.yaml_number[1:])-1
                    matrix.append(sw_num/16)
                    matrix.append(sw_num%16)
                    #self.log.debug(matrix)
                    y_offset = 3
                    
                    if int(matrix[1])<8:
                        row_colour = self.base_colour[0]+'/'+self.wire_colour[0][matrix[1]]
                    else:
                        row_colour = self.base_colour[1]+'/'+self.wire_colour[1][matrix[1]-8]
                        
                    col_colour = self.base_colour[2]+'/'+self.wire_colour[2][matrix[0]]

                    #sw_num = 32+ 16*int(matrix[0])+int(matrix[1])
                    self.row_layer.set_text(row_colour,color=dmd.BROWN)
                    self.column_layer.set_text(col_colour,color=dmd.BROWN)
                    self.number_layer.set_text(sw.yaml_number,color=dmd.CYAN)
                    if sw.state:
                        matrix_layer.target_x = x_offset+(matrix[1]*3)
                        matrix_layer.target_y = y_offset+(matrix[0]*3)
                        self.matrix_layer_group.append(matrix_layer)
                        self.switch_index.append(sw_num)
                    else:
                        try: #try except needed for first enter press
                           matrix_layer.target_x = 128
                           matrix_layer.target_y = 32
                           num = self.switch_index.index(sw_num)
                           self.matrix_layer_group.pop(num)
                           self.switch_index.pop(num)
                        except Exception, err:
                            return
                    #self.log.info(self.matrix_layer_group)
                    #self.log.info(self.switch_index)
                    
                elif sw.yaml_number.count('D')>0:
                    sw_num = int(sw.yaml_number[2:])-1
                    matrix =[]
                    matrix.append(sw_num/8)
                    matrix.append(sw_num%8)
                    #self.log.debug(matrix)
                    y_offset = 14
                    
                    if matrix[0]==0:
                        row_colour = self.base_colour[3]+'/'+self.wire_colour[3][matrix[1]]
                    elif matrix[0]==1:
                        row_colour = self.base_colour[4]+'/'+self.wire_colour[4][matrix[1]]
                        x_offset += 24
                    else:
                        row_colour = self.base_colour[5]+'/'+self.wire_colour[5][matrix[1]]

                    col_colour = 'Black'
                    
                    self.row_layer.set_text(row_colour,color=dmd.BROWN)
                    self.column_layer.set_text(col_colour,color=dmd.BROWN)
                    self.number_layer.set_text(sw.yaml_number,color=dmd.CYAN)
                    
                    if sw.state:
                        matrix_layer.target_x = x_offset+(matrix[1]*3)
                        matrix_layer.target_y = y_offset+(matrix[0]*3)
                        self.direct_matrix_layer_group.append(matrix_layer)
                        self.direct_switch_index.append(sw_num)
                    else:
                        try: #try except needed for first enter press
                            matrix_layer.target_x = 128
                            matrix_layer.target_y = 32
                            num = self.direct_switch_index.index(sw_num)
                            self.direct_matrix_layer_group.pop(num)
                            self.direct_switch_index.pop(num)
                        except Exception, err:
                            return
                    
                    #self.log.info(self.direct_matrix_layer_group)
                    #self.log.info(self.direct_switch_index)

                return True

        #def sw_enter_active(self,sw):
        #        return True
        
       
class ArkTest(ServiceModeSkeleton):
    """docstring for ResetAudits"""
    def __init__(self, game, priority, font, big_font):
        super(ArkTest, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.service.ark_test')
        self.name = 'Ark Test'
        
        self.switch_layer = dmd.TextLayer(1, 19, self.game.fonts['7x4'], "left")
        
        self.status = ''
        self.info = ''
        self.okToUpdate=False
                
                
    def mode_started(self):
        super(ArkTest,self).mode_started()
        
        self.item_layer.set_text("Balls in Ark: "+str(self.game.ark.num_balls()),color=dmd.YELLOW)
        self.instruction_layer.set_text("Press Enter to Cycle",color=dmd.GREEN)
        self.okToUpdate=True
        
    
    def mode_stopped(self):
        super(ArkTest,self).mode_stopped()
        self.cancel_delayed('arktest_display_update')
         
         
    def cycle_ark(self):
        self.game.ark.reset()
        
        self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/ark_test_bgnd.dmd').frames[0])
        self.bgnd_layer.composite_op='blacksrc'
        self.item_layer.y=9
        self.item_layer.set_text("Cycling Ark",color=dmd.YELLOW)
        self.item_layer.composite_op='blacksrc'
        self.switch_layer.set_text(self.get_ark_sw_states(),color=dmd.MAGENTA)
        self.instruction_layer.font = self.game.fonts['7x4']
        self.instruction_layer.set_text("Do Not Power Off",color=dmd.RED)
        
        self.layer = dmd.GroupedLayer(128, 32, [self.title_layer, self.item_layer, self.instruction_layer, self.switch_layer,self.bgnd_layer])
        
        self.delay(name='arktest_display_update',delay=5,handler=self.display_update)
       
        
    def display_update(self):
        #self.item_layer.set_text("Cycling Ark",color=dmd.YELLOW)
        self.switch_layer.set_text(self.get_ark_sw_states(),color=dmd.MAGENTA)
        self.instruction_layer.set_text("Balls in Ark: "+str(self.game.ark.num_balls()),color=dmd.GREEN)
        self.cancel_delayed('arktest_display_update')
        self.delay(name='arktest_display_update',delay=1,handler=self.display_update)
        
        
    def get_ark_sw_states(self):
        if self.game.switches.arkMotorUp.is_active():
            up_text ="Closed"
        else:
             up_text ="Open"
        text = "Ark Up Sw:"+up_text
        
        if self.game.switches.arkMotorDown.is_active():
            down_text ="Closed"
        else:
             down_text ="Open"
        text = text+ " Ark Down Sw:"+down_text
        
        return text
        
        
    def sw_arkMotorUp_active(self,sw):
        self.display_update()
        
    def sw_arkMotorUp_inactive(self,sw):
        self.display_update()
        
    def sw_arkMotorDown_active(self,sw):
        self.display_update()
        
    def sw_arkMotorDown_inactive(self,sw):
        self.display_update()
        
    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
             # if enter is pressed, cycle the ark
            self.cycle_ark()
        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop

class SwordsmanTest(ServiceModeSkeleton):
    """docstring for ResetAudits"""
    def __init__(self, game, priority, font, big_font):
        super(SwordsmanTest, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.service.swordsman_test')
        self.name = 'Swordsman Test'
        
        self.switch_layer = dmd.TextLayer(1, 19, self.game.fonts['7x4'], "left")
        
        self.status = ''
        self.info = ''
        self.okToUpdate=False
                
                
    def mode_started(self):
        super(SwordsmanTest,self).mode_started()

        self.item_layer.set_text("Swordsman is: "+self.game.swordsman.get_state(),color=dmd.YELLOW)
        self.instruction_layer.set_text("Press Enter to Change Posn",color=dmd.GREEN)
        self.okToUpdate=True
        
    
    def mode_stopped(self):
        super(SwordsmanTest,self).mode_stopped()
        self.cancel_delayed('swordsman_test_display_update')
        self.game.swordsman.cycle(False) #this cancels the cycle and also closes the swordsman
         
         
    def process(self):
        #setup display
        self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/swordsman_test_bgnd.dmd').frames[0])
        self.bgnd_layer.composite_op='blacksrc'
        self.item_layer.y=9
        self.item_layer.set_text("Cycling Swordsman",color=dmd.YELLOW)
        self.item_layer.composite_op='blacksrc'
        self.switch_layer.set_text(self.get_swordsman_sw_states(),color=dmd.MAGENTA)
        self.instruction_layer.font = self.game.fonts['7x4']
        self.instruction_layer.set_text("Do Not Power Off",color=dmd.RED)
        
        self.layer = dmd.GroupedLayer(128, 32, [self.title_layer, self.item_layer, self.instruction_layer, self.switch_layer,self.bgnd_layer])
        
        self.delay(name='swordsman_test_display_update',delay=1,handler=self.display_update)

        self.game.swordsman.cycle()
       
        
    def display_update(self):
        self.item_layer.set_text("Cycling Swordsman",color=dmd.YELLOW)
        self.switch_layer.set_text(self.get_swordsman_sw_states(),color=dmd.MAGENTA)
        self.instruction_layer.set_text("Swordsman is: "+self.game.swordsman.get_state(),color=dmd.GREEN)
        self.cancel_delayed('swordsman_test_display_update')
        self.delay(name='swordsman_test_display_update',delay=0.25,handler=self.display_update)
        
        
    def get_swordsman_sw_states(self):
        if self.game.switches.swordsmanForward.is_active():
            forward_text ="Closed"
        else:
            forward_text ="Open"
        text = "Forward Sw: "+forward_text
        
        if self.game.switches.swordsmanBack.is_active():
            home_text ="Closed"
        else:
            home_text ="Open"
        text = text+ " Home Sw: "+home_text
        
        return text
        
        
    def sw_swordsmanForward_active(self,sw):
        self.display_update()
        
    def sw_swordsmanForward_inactive(self,sw):
        self.display_update()
        
    def sw_swordsmanBack_active(self,sw):
        self.display_update()
        
    def sw_swordsmanBack_inactive(self,sw):
        self.display_update()
        
    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
             # if enter is pressed, run the test
            self.process()
        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop        

              
              
class TroughTest(ServiceModeSkeleton):
    """docstring for ResetAudits"""
    def __init__(self, game, priority, font, big_font):
        super(TroughTest, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.service.trough_test')
        self.name = 'Trough Test'
        
        self.text_trough1_layer = dmd.TextLayer(97, 20, self.game.fonts['7x4'], "left")
        self.text_trough2_layer = dmd.TextLayer(80, 19, self.game.fonts['7x4'], "left")
        self.text_trough3_layer = dmd.TextLayer(65, 18, self.game.fonts['7x4'], "left")
        self.text_trough4_layer = dmd.TextLayer(1, 19, self.game.fonts['7x4'], "left")
        self.text_trough5_layer = dmd.TextLayer(1, 19, self.game.fonts['7x4'], "left")
        self.text_trough6_layer = dmd.TextLayer(1, 19, self.game.fonts['7x4'], "left")
        self.text_jam_layer = dmd.TextLayer(1, 19, self.game.fonts['7x4'], "left")
        self.text_shooter_lane_layer = dmd.TextLayer(115, 20, self.game.fonts['7x4'], "left")
        
        self.status = ''
        self.info = ''
        self.okToUpdate=False
                
                
    def mode_started(self):
        super(TroughTest,self).mode_started()
        
        trough_anim = dmd.Animation().load(game_path+"dmd/trough_bgnd.dmd")
        self.trough_layer = dmd.FrameLayer(frame=trough_anim.frames[0])
        self.trough_layer.composite_op ="blacksrc"
        
        self.trough_display_layer = [self.bgnd_layer,self.trough_layer,self.title_layer,self.instruction_layer]
        
        #create a map of the ball positions
        #posns = [[111,15],[93,0],[93,15],[77,14],[61,13],[45,12],[29,11],[13,10]] #6 ball trough
        posns = [[111,15],[93,0],[93,15],[77,14],[61,13],[45,12],[29,11]] #5 ball trough
        self.ball_posns = posns
        for id,switch in enumerate(self.game.switches.items_tagged('trough_test')):
            self.create_ball_posn(switch,posns[id][0],posns[id][1])
            self.add_switch_handler(name=switch.name, event_type='active', delay=0.25, handler=self.ttrough_active_sw)
            self.add_switch_handler(name=switch.name, event_type='inactive', delay=0.25, handler=self.ttrough_inactive_sw)
            
            #add update for initial states
            if switch.is_active():
                self.ttrough_active_sw(switch)
                self.log.info("Initial Active Trough Test Switch:%s",switch.name)
            else:
                self.ttrough_inactive_sw(switch)
                self.log.info("Initial Inactive Trough Test Switch:%s",switch.name)
        
#        for switch in self.game.switches.items_tagged('trough_jam'):
#            self.create_ball_posn(switch,posns[5][0],posns[5][1])
#        
#        for switch in self.game.switches.items_tagged('shooter_lane'):
#            self.create_ball_posn(switch,posns[6][0],posns[6][1])
            
        self.layer = dmd.GroupedLayer(128, 32, self.trough_display_layer)
        
        
        self.okToUpdate=True
        
        
    
    def mode_stopped(self):
        super(TroughTest,self).mode_stopped()
        self.cancel_delayed('arktest_display_update')
         
    
    def create_ball_posn(self,sw,x,y):
        #create a ball outline with sw number and positon in the trough
        
        #num = self.game.switches[sw].number
        self.log.info('creating trough test graphics: %s',sw.name)
        sw_num = sw.yaml_number[1:]
        text_layer = dmd.TextLayer(x+4, y+5, self.game.fonts['tiny7'], "left")
        text_layer.composite_op ="blacksrc"
        text_layer.set_text(sw_num,color=dmd.RED)
        
        ball_anim = dmd.Animation().load(game_path+"dmd/trough_ball.dmd")
        ball_layer = dmd.FrameLayer(frame=ball_anim.frames[1])
        ball_layer.target_x=x
        ball_layer.target_y=y
        ball_layer.composite_op ="blacksrc"
        
        #add to the display layer group
        self.trough_display_layer.append(ball_layer)
        self.trough_display_layer.append(text_layer)
        
    
    def ttrough_active_sw(self,sw):
        
        #num = self.game.switches[sw].number
        sw_num = sw.yaml_number[1:]
        id=(int(sw_num)-23)*-1

        ball_anim = dmd.Animation().load(game_path+"dmd/trough_ball.dmd")
        ball_layer = dmd.FrameLayer(frame=ball_anim.frames[0])
        ball_layer.composite_op ="blacksrc"
        ball_layer.target_x=self.ball_posns[id][0]
        ball_layer.target_y=self.ball_posns[id][1]
        
        self.trough_display_layer[(id*2)+4] = ball_layer
        self.trough_display_layer[(id*2)+5].set_text(sw_num,color=dmd.GREEN)
        
        self.display_update()
        
    
    def ttrough_inactive_sw(self,sw):
        
        #num = self.game.switches[sw].number
        sw_num = sw.yaml_number[1:]
        id=(int(sw_num)-23)*-1

        ball_anim = dmd.Animation().load(game_path+"dmd/trough_ball.dmd")
        ball_layer = dmd.FrameLayer(frame=ball_anim.frames[1])
        ball_layer.composite_op ="blacksrc"
        ball_layer.target_x=self.ball_posns[id][0]
        ball_layer.target_y=self.ball_posns[id][1]
        
        self.trough_display_layer[(id*2)+4] = ball_layer
        self.trough_display_layer[(id*2)+5].set_text(sw_num,color=dmd.YELLOW)
        
        self.display_update()
        
        
#    def trough_active_sw(self,sw,id):
#        
#        #num = self.game.switches[sw].number
#        sw_num = sw.yaml_number[1:]
#
#        ball_anim = dmd.Animation().load(game_path+"dmd/trough_ball.dmd")
#        ball_layer = dmd.FrameLayer(frame=ball_anim.frames[0])
#        ball_layer.composite_op ="blacksrc"
#        ball_layer.target_x=self.ball_posns[id][0]
#        ball_layer.target_y=self.ball_posns[id][1]
#        
#        self.trough_display_layer[(id*2)+3] = ball_layer
#        self.trough_display_layer[(id*2)+4].set_text(sw_num,color=dmd.GREEN)
#        
#        self.display_update()
#    
#    def trough_inactive_sw(self,sw,id):
#        
#        #num = self.game.switches[sw].number
#        sw_num = sw.yaml_number[1:]
#
#        ball_anim = dmd.Animation().load(game_path+"dmd/trough_ball.dmd")
#        ball_layer = dmd.FrameLayer(frame=ball_anim.frames[1])
#        ball_layer.composite_op ="blacksrc"
#        ball_layer.target_x=self.ball_posns[id][0]
#        ball_layer.target_y=self.ball_posns[id][1]
#        
#        self.trough_display_layer[(id*2)+3] = ball_layer
#        self.trough_display_layer[(id*2)+4].set_text(sw_num,color=dmd.RED)
#        
#        self.display_update()
         
           
    def display_update(self):  
        self.instruction_layer.set_text("Balls: "+str(self.game.trough.num_balls()),color=dmd.GREEN)
        self.layer = dmd.GroupedLayer(128, 32, self.trough_display_layer)
        #self.cancel_delayed('arktest_display_update')
        #self.delay(name='arktest_display_update',delay=1,handler=self.display_update)
    
    
    def launch_callback(self):
        self.delay(name='launch_delay',delay=0.5,handler=self.game.coils.ballLaunch.pulse)
    
        
    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
             # if enter is pressed, eject a ball
            self.game.trough.launch_balls(1, self.launch_callback)
        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop        
          
            
            
class Statistics(ServiceModeList):
        """Service Mode."""
        def __init__(self, game, priority, font, big_font, name, itemlist):
                super(Statistics, self).__init__(game, priority,font)

                self.name = name
                self.items = []
                audits_list = self.game.displayed_audits
                
                #for section in sorted(itemlist.iterkeys()):
                for audits_section in audits_list.iterkeys():
                    self.log.info("Stats Section:"+str(audits_section))
                    self.items.append( AuditDisplay( self.game, priority + 1, font, big_font, section_key=audits_section,itemlist =audits_list[audits_section] ))
                                
            
class AuditDisplay(ServiceModeList):
        """Service Mode."""
        def __init__(self, game, priority, font, big_font, section_key, itemlist):
                super(AuditDisplay, self).__init__(game, priority, font)
                self.name = itemlist['label'] #name of section is set as a label, so the key is seperate

                self.item_layer = dmd.TextLayer(1, 8, font, "left")
                self.value_layer = dmd.TextLayer(1, 16, big_font, "left")
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.value_layer])

                self.items = []
                for item in sorted(itemlist.iterkeys()):
                    if item!='label':
                        self.log.info("Stats Item:"+str(item))
                        audit_value = audits.display(self.game,section_key,item) #calc the required value from the audits database. formating is also handled in the audits class
                        self.items.append(AuditItem(name=str(itemlist[item]['label']).upper(), value=audit_value))    
   

        def mode_started(self):
                super(AuditDisplay, self).mode_started()


        def change_item(self):
                super(AuditDisplay, self).change_item()
                self.value_layer.set_text(str(self.item.value))


        def sw_enter_active(self, sw):
                return True
            

#class StatsDisplay(ServiceModeList):
#        """Service Mode."""
#        def __init__(self, game, priority, font, big_font, name, itemlist):
#                super(StatsDisplay, self).__init__(game, priority, font)
#                self.name = name
#
#                self.item_layer = dmd.TextLayer(1, 11, font, "left")
#                self.value_layer = dmd.TextLayer(127, 11, big_font, "right")
#                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.value_layer])
#
#                self.items = []
#                for item in sorted(itemlist.iterkeys()):
#                    #self.log.info("Stats Item:"+str(item))
#                    if type(itemlist[item])==type({}):
#                        self.items.append( HighScoreItem(str(item), itemlist[item]['inits'], itemlist[item]['score']) )
#                    else:
#                        self.items.append( StatsItem(str(item), itemlist[item]) )
#
#                
#        def mode_started(self):
#                super(StatsDisplay, self).mode_started()
#
#        def change_item(self):
#                super(StatsDisplay, self).change_item()
#                try:
#                        self.item.score
#                except:
#                        self.item.score = 'None'
#
#                if self.item.score == 'None':
#                        self.value_layer.set_text(str(self.item.value))
#                else:
#                        self.value_layer.set_text(self.item.value + ": " + str(self.item.score))
#
#        def sw_enter_active(self, sw):
#                return True

class AuditItem:
        """Service Mode."""
        def __init__(self, name, value):
                self.name = name
                self.value = value

        def disable(self):
                pass

#class HighScoreItem:
#        """Service Mode."""
#        def __init__(self, name, value, score):
#                self.name = name
#                self.value = value
#                self.score = score
#
#        def disable(self):
#                pass


class Settings(ServiceModeList):
        """Service Mode."""
        def __init__(self, game, priority, font, big_font, name, itemlist):
                super(Settings, self).__init__(game, priority,font)
                #self.title_layer.set_text('Settings')
                self.name = name
                self.items = []
                self.font = font
                for x,section in enumerate(sorted(itemlist.iterkeys())):
                        self.items.append( SettingsEditor( self.game, priority + 1, font, big_font, x,str(section),itemlist[section] ))

class SettingsEditor(ServiceModeList):
        """Service Mode."""
        def __init__(self, game, priority, font, big_font, id,name, itemlist):
                super(SettingsEditor, self).__init__(game, priority, font)
                small_font = self.game.fonts['7x4']
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_adjust_bgnd.dmd').frames[0])
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
                self.item_layer = dmd.TextLayer(1, 8, small_font, "left")
                self.value_layer = dmd.TextLayer(128, 15, big_font, "right")
                self.instruction_layer = dmd.TextLayer(1, 26, small_font, "left")
                self.instruction_layer.composite_op = "blacksrc"
                self.no_exit_switch = game.machine_type == 'sternWhitestar'
                #self.title_layer.set_text('Settings')
                
                self.id=id+1
                self.name = name
                self.items = []
                
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.value_layer, self.instruction_layer])
                for item in sorted(itemlist.iterkeys()):
                        #self.items.append( EditItem(str(item), itemlist[item]['options'], itemlist[item]['value'] ) )
                        if 'increments' in itemlist[item]:
                                num_options = ((itemlist[item]['options'][1]-itemlist[item]['options'][0]) / itemlist[item]['increments'])+1
                                option_list = []
                                for i in range(0,int(num_options)):
                                        option_list.append(itemlist[item]['options'][0] + (i * itemlist[item]['increments']))
                                self.items.append( EditItem(str(item), option_list, self.game.user_settings[self.name][item]) )
                        else:
                                self.items.append( EditItem(str(item), itemlist[item]['options'], self.game.user_settings[self.name][item]) )
                self.state = 'nav'
                self.stop_blinking = True
                self.item = self.items[0]
                
                #add custom code here for display of procgame version match on name?
                self.value_layer.set_text(str(self.item.value))
                
                self.option_index = self.item.options.index(self.item.value)

        def mode_started(self):
                super(SettingsEditor, self).mode_started()

        def mode_stopped(self):
                self.game.sound.play('service_exit')

        def sw_enter_active(self, sw):
                if not self.no_exit_switch:
                        self.process_enter()
                return True

        def process_enter(self):
                if self.state == 'nav':
                        self.state = 'edit'
                        self.blink = True
                        self.stop_blinking = False
                        self.delay(name='blink', event_type=None, delay=.3, handler=self.blinker)
                else:
                        self.state = 'nav'
                        self.instruction_layer.set_text("Change saved",color=dmd.GREEN)
                        self.delay(name='change_complete', event_type=None, delay=1, handler=self.change_complete)
                        self.game.sound.play('service_save')
                        self.game.user_settings[self.name][self.item.name]=self.item.value
                        self.stop_blinking = True
                        self.game.save_settings()

        def sw_exit_active(self, sw):
                self.process_exit()
                return True

        def process_exit(self):
                if self.state == 'nav':
                        self.game.modes.remove(self)
                else:
                        self.state = 'nav'
                        self.value_layer.set_text(str(self.item.value))
                        self.stop_blinking = True
                        self.game.sound.play('service_cancel')
                        self.instruction_layer.set_text("Change cancelled",color=dmd.GREEN)
                        self.delay(name='change_complete', event_type=None, delay=1, handler=self.change_complete)
                        
        def sw_up_active(self, sw):
                if self.game.switches.enter.is_inactive():
                        self.process_up()

                else:
                        self.process_enter()
                return True

        def process_up(self):
                if self.state == 'nav':
                        self.item.disable()
                        if (self.iterator < self.max):
                                self.iterator += 1
                        else:
                            self.iterator =0

                        self.game.sound.play('service_next')
                        self.change_item()
                else:
                        if self.option_index < (len(self.item.options) - 1):
                                self.option_index += 1
                                self.item.value = self.item.options[self.option_index]
                                self.value_layer.set_text(str(self.item.value))
                                

        def sw_down_active(self, sw):
                if self.game.switches.enter.is_inactive():
                        self.process_down()
                else:
                        self.process_exit()
                return True

        def process_down(self):
                if self.state == 'nav':
                        self.item.disable()
                        if (self.iterator > 0):
                                self.iterator -= 1
                        else:
                            self.iterator =self.max
                            
                        self.game.sound.play('service_previous')
                        self.change_item()
                else:
                        if self.option_index > 0:
                                self.option_index -= 1
                                self.item.value = self.item.options[self.option_index]
                                self.value_layer.set_text(str(self.item.value))

        def change_item(self):
                ctr = 0
                for item in self.items:
                        if ctr == self.iterator:
                                self.item = item
                        ctr += 1
                self.max = ctr - 1
                self.item_layer.set_text(str(self.id)+'.'+str(self.iterator+1)+') '+str(self.item.name))
                self.value_layer.set_text(str(self.item.value))
                self.log.info('Setting :%s',self.item.name)
                self.option_index = self.item.options.index(self.item.value)
                        
        def disable(self):
                pass

        def blinker(self):
                if self.blink: 
                        self.value_layer.set_text(str(self.item.value))
                        self.blink = False
                else:
                        self.value_layer.set_text("")
                        self.blink = True
                if not self.stop_blinking:
                        self.delay(name='blink', event_type=None, delay=.3, handler=self.blinker)
                else:
                        self.value_layer.set_text(str(self.item.value))
        
        def change_complete(self):
                self.instruction_layer.set_text("")
                
class EditItem:
        """Service Mode."""
        def __init__(self, name, options, value):
                self.name = name
                self.options = options
                self.value = value

        def disable(self):
                pass
            
            
class Utilities(ServiceModeList):
        """Service Mode."""
        def __init__(self, game, priority, font, big_font, name):
                super(Utilities, self).__init__(game, priority,font)
                
                self.name = name
                self.end_game = EndGame(self.game, self.priority+1, font, big_font)
                self.software_update = SoftwareUpdate(self.game, self.priority+1, font, big_font)
                self.log_download = LogsDownload(self.game, self.priority+1, font, big_font)
                self.set_date_time = SetDateTime(self.game, self.priority+1, font, big_font)
                self.reset_audits = ResetAudits(self.game, self.priority+1, font, big_font)
                self.reboot_game = Reboot(self.game, self.priority+1, font, big_font)
                self.items = [self.end_game,self.software_update,self.log_download,self.reset_audits,self.reboot_game,self.set_date_time]
                
                
#mode to manually update the game software
class SoftwareUpdate(ServiceModeSkeleton):

    def __init__(self, game, priority, font, big_font):
        super(SoftwareUpdate, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.software_update')
        
        self.usb_location = config.value_for_key_path('usb_path')
        self.main_update_location = '/indiana-jones-update-files'
        self.game_update_location = '/game-update'
        self.proc_update_location = '/procgame-update'
        self.temp_store_path = base_path+"/temp"

        self.name = 'Software Update'
        self.spin = False
        self.proc_update = False

        try:
            self.proc_uid = pwd.getpwnam("proc").pw_uid
            self.proc_gid = grp.getgrnam("proc").gr_gid
        except:
            try:
                self.proc_uid = pwd.getpwnam("pinball").pw_uid
                self.proc_gid = grp.getgrnam("pinball").gr_gid
            except:
                self.proc_uid = None
        
        
    def mode_started(self):
        super(SoftwareUpdate,self).mode_started()
        self.update()


    def update(self):
        self.myLocation = None
        dirs = []
        self.okToUpdate = False
        
        # list the contents of the USB path
        try:
            dirs = os.listdir(self.usb_location)
        except Exception, err:
            pass
            #self.log.info('Directory Read Error:%s',err)

        # check them all for the update files
        for directory in dirs:
            checkThis = self.usb_location + self.main_update_location
            #self.log.info('Directory path found:%s',checkThis)
            if os.path.isdir(checkThis):
                self.log.info("Found the update")
                self.myLocation = checkThis
                
                #check for procfiles to update
                mylocation_dirs = []
                try:
                    mylocation_dirs = os.listdir(self.myLocation)
                except Exception, err:
                    pass
                
                for directory in mylocation_dirs:
                    checkThis = self.usb_location + self.main_update_location + self.proc_update_location
                    if os.path.isdir(checkThis):
                        self.proc_update = True;
                        self.log.info("procgame files to be updated")
                        
                break;
            

        if self.myLocation != None:
            self.okToUpdate = True
            self.item_layer.set_text("Files Found For Update",color=dmd.YELLOW)
            self.instruction_layer.set_text("Press Enter to Update",color=dmd.GREEN)
        else:
            self.okToUpdate = False
            self.log.info("Didn't find the update")
            self.item_layer.set_text("Files Not Found",color=dmd.RED)
            self.instruction_layer.set_text("Check USB Drive",color=dmd.GREEN)

       
    
    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
            # if enter is pressed, copy the files
            # update the layer to say copying files
            self.item_layer.set_text("Copying Files",color=dmd.YELLOW)
            self.instruction_layer.set_text("Do Not Power Off",color=dmd.RED)
            self.spin = True
            self.delay(delay=1,handler=self.copy_files)

        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop



    def copy_files(self):

        #remove the tmp directory if exists
        try:
            shutil.rmtree(self.temp_store_path)
        except:
            pass

        #then copy the allowed files to a temp store
        try:
            shutil.copytree(src=self.myLocation, dst=self.temp_store_path, ignore=shutil.ignore_patterns('*.pyc','*.psd','*.jpg','*.bmp','.png','*.exe','*.zip','*.sh'))
            
            #fix permissions for game installs
            recursive= True
            if self.proc_uid !=None:                
                os.chown(self.temp_store_path, self.proc_uid, self.proc_gid)
                if recursive:
                    for root, dirs, files in os.walk(self.temp_store_path):
                        for d in dirs:
                            os.chown(os.path.join(root, d), self.proc_uid, self.proc_gid)
                        for f in files:
                            os.chown(os.path.join(root, f), self.proc_uid, self.proc_gid)
                            
        except OSError as err:
            self.log.info('Temp store not created. Error: %s' % err)

        #then copy temp store to the game folder
        try:
            dir_util.copy_tree(src=self.temp_store_path+self.game_update_location,dst=game_path,update=True)
            if self.proc_update:
                dir_util.copy_tree(src=self.temp_store_path+self.proc_update_location,dst=proc_path,update=True)
        except OSError as err:
            self.log.info('Files not Updated. Error: %s' % err)
            
        #cleanup - remove the tmp directory if exists
#        try:
#            shutil.rmtree(self.temp_store_path)
#        except:
#            pass


        self.item_layer.set_text("Copy Finished",color=dmd.YELLOW)
        self.instruction_layer.set_text("Press Exit Button",color=dmd.GREEN)
        self.spin = False

        self.busy = False
        
        
#mode to download logs to usb stick for analysis
class LogsDownload(ServiceModeSkeleton):

    def __init__(self, game, priority, font, big_font):
        super(LogsDownload, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.service.logs_download')
        
        self.usb_location = config.value_for_key_path('usb_path')
        self.logs_location = game_path+'/var/logs'
        self.temp_store_path = base_path+"/temp"
        self.log_store_path = self.usb_location+"/indiana-jones-logs"

        self.name = 'Logs Download'
        self.spin = False
        self.proc_update = False


    def mode_started(self):
        super(LogsDownload,self).mode_started()
        self.update()


    def update(self):
        self.myLocation = None
        dirs = []
        self.okToUpdate = False
        
        # check for usb stick inserted and named correctly
        try:
            dirs = os.listdir(self.usb_location)
            self.okToUpdate = True
            self.item_layer.set_text("Store Disk Found",color=dmd.YELLOW)
            self.instruction_layer.set_text("Press Enter to Download",color=dmd.GREEN)
            
        except Exception, err:
            self.okToUpdate = False
            self.log.info("Didn't find the storage usb drive")
            self.item_layer.set_text("Store Not Found",color=dmd.RED)
            self.instruction_layer.set_text("Check USB Drive",color=dmd.GREEN)
           
    
    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
            # if enter is pressed, copy the files
            # update the layer to say copying files
            self.item_layer.set_text("Copying Log Files",color=dmd.YELLOW)
            self.instruction_layer.set_text("Do Not Power Off",color=dmd.RED)
            self.spin = True
            self.delay(delay=1,handler=self.copy_files)

        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop


    def copy_files(self):

        #remove the tmp directory if exists and remove the usb drive log folder if exists
        try:
            shutil.rmtree(self.temp_store_path)
        except:
            pass

        #then copy the allowed files to a temp store
        try:
            shutil.copytree(src=self.logs_location, dst=self.temp_store_path, ignore=shutil.ignore_patterns('*.pyc','*.psd','*.jpg','*.bmp','.png','*.exe','*.zip','*.sh'))
        except OSError as err:
            self.log.info('Temp store not created. Error: %s' % err)

        #then copy temp store to the usb drive
        try:
            dir_util.copy_tree(src=self.temp_store_path,dst=self.log_store_path,update=True)
            if self.proc_update:
                dir_util.copy_tree(src=self.temp_proc_store_path,dst=proc_path,update=True)
        except OSError as err:
            self.log.info('Files not Updated. Error: %s' % err)
            
        #cleanup - remove the tmp directory if exists
#        try:
#            shutil.rmtree(self.temp_store_path)
#        except:
#            pass

        self.item_layer.set_text("Log Download Finished",color=dmd.YELLOW)
        self.instruction_layer.set_text("Press Exit Button",color=dmd.GREEN)
        self.spin = False
        self.busy = False


class ResetAudits(ServiceModeSkeleton):
    """docstring for ResetAudits"""
    def __init__(self, game, priority, font, big_font):
        super(ResetAudits, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.service.reset_audits')
        self.name = 'Reset Audits'
        self.status = ''
        self.info = ''
        self.spin = False
        self.okToUpdate=False
                
                
    def mode_started(self):
        super(ResetAudits,self).mode_started()
        self.log.info(audits.database_path(self.game))
        if audits.database_path(self.game) !=None:
            self.item_layer.set_text("Audit Database Exists",color=dmd.YELLOW)
            self.instruction_layer.set_text("Press Enter to Clear Audits",color=dmd.GREEN)
            self.okToUpdate=True
            self.spin = True
        else:
            self.item_layer.set_text("Audit Database Cannot Be Cleared",color=dmd.RED)
            self.instruction_layer.set_text("Press Exit Button",color=dmd.GREEN)
                
                    
    def clear_audits(self):
            audits.delete_all(self.game)
            self.item_layer.set_text( "Audit Clearing Completed",color=dmd.YELLOW)
            self.instruction_layer.set_text("Press Exit Button",color=dmd.GREEN)
            self.spin = False
            self.busy = False


    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
            # if enter is pressed, reboot the game
            self.item_layer.set_text("Clearing Audit Data",color=dmd.YELLOW)
            self.instruction_layer.set_text("Do Not Power Off",color=dmd.RED)
            self.spin = True
            self.delay(delay=1,handler=self.clear_audits)
        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop
    

class EndGame(ServiceModeSkeleton):
    """docstring for ResetAudits"""
    def __init__(self, game, priority, font, big_font):
        super(EndGame, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.service.end_game')
        self.name = 'End Game'
        self.status = ''
        self.info = ''
        self.spin = False
        self.okToUpdate=False
                
                
    def mode_started(self):
        super(EndGame,self).mode_started()
    
        if self.game.ball>0:
            self.item_layer.set_text("Game In Progress",color=dmd.YELLOW)
            self.instruction_layer.set_text("Press Enter to Stop",color=dmd.GREEN)
            self.okToUpdate=True
            self.spin = True
        else:
            self.item_layer.set_text("No Game is Running",color=dmd.RED)
            self.instruction_layer.set_text("Press Exit Button",color=dmd.GREEN)
                
                    
    def end_game(self):
            self.game.end_game()
            #self.game.reset()
            
            self.item_layer.set_text("Game Stopped",color=dmd.YELLOW)
            self.instruction_layer.set_text("Press Exit Button",color=dmd.GREEN)
            self.spin = False
            self.busy = False


    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
            # if enter is pressed, stop the game
            self.item_layer.set_text("Stopping Game",color=dmd.YELLOW)
            self.instruction_layer.set_text("Do Not Power Off",color=dmd.RED)
            self.spin = True
            self.delay(delay=1,handler=self.end_game)
        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop
      
      
class Reboot(ServiceModeSkeleton):

    def __init__(self, game, priority, font, big_font):
        super(Reboot, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.restart')
        self.name = 'Reboot Game'
        
        
    def mode_started(self):
        super(Reboot,self).mode_started()
        self.okToUpdate = True
        self.item_layer.set_text("Game will be restarted",color=dmd.YELLOW)
        self.instruction_layer.set_text("Press Enter to Confirm",color=dmd.GREEN)


    def reboot(self):
        self.stop_proc()

        # Import and run the startup script, further execution of this script is halted until the run_loop is stopped.
        import game
        game.main()

        # Reset mode & restart P-ROC / pyprocgame
        self.restart_proc()


    def stop_proc(self):

        self.game.sound.stop_music()
        self.game.end_run_loop()
        while len(self.game.dmd.frame_handlers) > 0:
                del self.game.dmd.frame_handlers[0]
        del self.game.proc


    def restart_proc(self):
        self.game.proc = self.game.create_pinproc()
        self.game.proc.reset(1)
        self.game.load_config(self.game.yamlpath)
        self.game.dmd.frame_handlers.append(self.game.proc.dmd_draw)
        self.game.dmd.frame_handlers.append(self.game.set_last_frame)
        self.game.run_loop()
    
    
    def sw_enter_active(self,sw):
        if self.okToUpdate:
            self.busy = True
            # if enter is pressed, reboot the game
            self.item_layer.set_text("Rebooting...",color=dmd.YELLOW)
            self.instruction_layer.set_text("Do Not Power Off",color=dmd.RED)
            self.spin = True
            self.delay(delay=1,handler=self.reboot)
        else:
            self.game.sound.play('service_cancel')
        return game.SwitchStop
    
    
class SetDateTime(ServiceModeSkeleton):

    def __init__(self, game, priority, font, big_font):
        super(SetDateTime, self).__init__(game, priority,font)
        self.log = logging.getLogger('ij.set_date_time')
        self.name = 'Set Date & Time'
        
        self.date_layer = dmd.DateLayer(1, 10,  self.game.fonts['7px_narrow_az'],"all", "left", opaque=False, colour=dmd.YELLOW)
        self.adjust_layer = dmd.TextLayer(1, 18,  self.game.fonts['5px_az'], "left", opaque=False)
        self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.instruction_layer,self.adjust_layer,self.date_layer])
        
        self.adjust_id=99
        self.adjust_types=['Month','Day','Year','Hours','Minutes']
        self.adjust_max=len(self.adjust_types)
        
        
    def mode_started(self):
        super(SetDateTime,self).mode_started()
        self.instruction_layer.set_text("+- To Change,Enter to Confirm",color=dmd.GREEN)
        self.adjust_layer.set_text("PRESS ENTER TO BEGIN",blink_frames=8,color=dmd.CYAN)


    def sw_up_active(self, sw):
        if self.adjust_id<self.adjust_max:
            self.process_up()
        #return game.SwitchStop
        
    def sw_down_active(self, sw):
        if self.adjust_id<self.adjust_max:
            self.process_down()
        #return game.SwitchStop
        
    def process_up(self):
        if self.adjust_id==0:
            self.date_layer.adjust_month(1)
        elif self.adjust_id==1:
            self.date_layer.adjust_day(1)
        elif self.adjust_id==2:
            self.date_layer.adjust_year(1)
        elif self.adjust_id==3:
            self.date_layer.adjust_hours(1)
        elif self.adjust_id==4:
            self.date_layer.adjust_minutes(1)
             
                 
    def process_down(self):
        if self.adjust_id==0:
            self.date_layer.adjust_month(-1)
        elif self.adjust_id==1:
            self.date_layer.adjust_day(-1)
        elif self.adjust_id==2:
            self.date_layer.adjust_year(-1)
        elif self.adjust_id==3:
            self.date_layer.adjust_hours(-1)
        elif self.adjust_id==4:
            self.date_layer.adjust_minutes(-1)
            
    
    def sw_enter_active(self,sw):
        
        self.adjust_id+=1
        
        if self.adjust_id==self.adjust_max:
            self.date_layer.adjust_completed()
            self.adjust_layer.set_text("ADJUST COMPLETED",color=dmd.CYAN)
        else:
            if self.adjust_id>self.adjust_max:
                self.adjust_id=0
                self.date_layer.adjust_month(0) #added to force correct text on a second adjustment run start
            self.adjust_layer.set_text("ADJUSTING "+self.adjust_types[self.adjust_id].upper(),blink_frames=8,color=dmd.RED)

        return game.SwitchStop
        

#mode for coin door opening & showing game health
class CoinDoor(game.Mode):

        def __init__(self, game):
                super(CoinDoor, self).__init__(game, priority=999)

                self.log = logging.getLogger('ij.coindoor')
        
                self.name = "Coin Door"
                self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/coindoor_bgnd.dmd').frames[0])
                self.bgnd_layer.composite_op='blacksrc'
                self.info_layer_top = dmd.TextLayer(64, -1, self.game.fonts['9px_az'], "center")
                self.info_layer_bottom = dmd.TextLayer(64, 9, self.game.fonts['9px_az'], "center")
                self.status_layer_top = dmd.TextLayer(64, 20, self.game.fonts['4px_az'] , "center")
                self.status_layer_bottom = dmd.TextLayer(64, 26, self.game.fonts['4px_az'] , "center")
                self.status_layer_top.composite_op='blacksrc'
                self.status_layer_bottom.composite_op='blacksrc'
                self.layer = dmd.GroupedLayer(128, 32, [self.info_layer_bottom,self.info_layer_top,self.status_layer_bottom,self.status_layer_top,self.bgnd_layer])

                self.info_message=[]
                self.status_messages =[]
                self.status=''
                self.status_message_posn=0
                self.status_colour = dmd.WHITE
                self.sound_repeats = 3
               

        def reset(self):
                self.sound_counter = 0

        def mode_started(self):
                super(CoinDoor, self).mode_started()

                #reset
                self.reset()

                #load messages for status label
                self.load_messages()

                #play sound
                self.play_sound()

                #start the update of the status info
                self.update()

        def mode_stopped(self):
                super(CoinDoor, self).mode_stopped()

                #cancel update loops
                self.cancel_delayed('update_status')
                self.cancel_delayed(self.sound_repeat_delay)

        def play_sound(self):
                #play sound
                timer=0.5
                self.game.sound.play('service_alert')
                self.sound_counter+=1
                self.sound_repeat_delay = self.delay(delay=timer,handler=self.play_sound)
                if self.sound_repeats == self.sound_counter:
                    self.cancel_delayed(self.sound_repeat_delay)


        def load_messages(self):
                self.info_layer_top.set_text('Coin Door Open'.upper(),color=dmd.YELLOW)
                self.info_layer_bottom.set_text('High Voltage Disabled'.upper(),color=dmd.YELLOW)

                self.status_layer_top.set_text(self.game.system_name+' '+self.game.system_version,color=dmd.ORANGE)
                
                self.status_messages =[]
                self.status_messages.append('myPinballs Electronics 2020')
                self.status_messages.append('info@mypinballs.co.uk')
                self.status_messages.append('Press "ENTER" For Main Menu')

                if self.game.health_status =='OK':
                    self.status_messages.append('No Errors To Report')
                    self.status_colour = dmd.GREEN
                elif self.game.health_status =='ERRORS':
                    self.status_colour = dmd.RED
                    for error in sorted(self.game.switch_error_log):
                        self.status_messages.append('Check Switch: '+error)#.switch_name


        def update(self):

                update_interval = 2

                if self.status_message_posn==len(self.status_messages):
                    self.status_message_posn=0

                self.status = self.status_messages[self.status_message_posn]

                #request update
                self.status_layer_bottom.set_text(self.status_messages[self.status_message_posn].upper(),color=self.status_colour)
                #inc message posn
                self.status_message_posn+=1

                #create loop with delay
                self.delay(name='update_status', event_type=None, delay=update_interval, handler=self.update)


        def layer_info(self):
                self.log.info("updating game status messages")
                params = {}
                #params['messageTop'] = "COIN DOOR IS OPEN"
                #params['messageMiddle']="COILS AND FLASHERS"
                #params['messageBottom']="ARE DISABLED"
                params['thestatus'] = self.status
                return ('content-coin-door_r1', params)

        #def sw_coinDoorClosed_active(self, sw):
        def sw_statusInterlock50v_inactive(self, sw):
                self.game.modes.remove(self)
        
       