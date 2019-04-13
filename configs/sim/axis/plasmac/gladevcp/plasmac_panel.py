#!/usr/bin/env python

'''
plasmac_panel.py
Copyright (C) 2018 2019 Phillip A Carter

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import os
import gtk
import linuxcnc
import gobject
import hal
from   gladevcp.persistence import widget_defaults,select_widgets
import gladevcp
from   subprocess import Popen,PIPE

class HandlerClass:

    def check_materials_file(self):
        version = '[VERSION 1]'
        tempMaterialsList = []
        if os.path.exists(self.materialsFile):
            if not version in open(self.materialsFile).read():
                print '*** upgrading material file...'
                with open(self.materialsFile, 'r') as f_in:
                    for line in f_in:
                        if not line.strip().startswith('#') and len(line.strip()):
                            name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts = line.split(',')
                            name = name.strip()
                            tempMaterialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
                with open(self.materialsFile, 'w') as f_out:
                    f_out.write('\
#plasmac configuration file\
\n#the next line is required for version checking\
\n' + version + '\n\
\n#example only, may be deleted\
\n#[MILD STEEL 1thick]\
\n#PIERCE_HEIGHT      = \
\n#PIERCE_DELAY       = \
\n#PUDDLE_JUMP_HEIGHT = (optional, set to 0 or delete if not required)\
\n#PUDDLE_JUMP_DELAY  = (optional, set to 0 or delete if not required)\
\n#CUT_HEIGHT         = \
\n#CUT_SPEED          = \
\n#CUT_AMPS           = (optional, only used for operator information)\
\n#CUT_VOLTS          = (modes 0 & 1 only, if not using auto voltage sampling)\
\n')
                    for material in tempMaterialsList:
                        f_out.write('\
\n[' + material[0] + ']\
\nPIERCE_HEIGHT      = ' + material[1] + '\
\nPIERCE_DELAY       = ' + material[2] + '\
\nPUDDLE_JUMP_HEIGHT = ' + material[3] + '\
\nPUDDLE_JUMP_DELAY  = ' + material[4] + '\
\nCUT_HEIGHT         = ' + material[5] + '\
\nCUT_SPEED          = ' + material[6] + '\
\nCUT_AMPS           = ' + material[7] + '\
\nCUT_VOLTS          = ' + material[8] + '\
')
        else:
            with open(self.materialsFile, 'w') as f_out:
                f_out.write('\
#plasmac configuration file\
\n#the next line is required for version checking\
\n' + version + '\n\
\n#example only, may be deleted\
\n#[MILD STEEL 1thick]\
\n#PIERCE_HEIGHT      = \
\n#PIERCE_DELAY       = \
\n#PUDDLE_JUMP_HEIGHT = (optional, set to 0 or delete if not required)\
\n#PUDDLE_JUMP_DELAY  = (optional, set to 0 or delete if not required)\
\n#CUT_HEIGHT         = \
\n#CUT_SPEED          = \
\n#CUT_AMPS           = (optional, only used for operator information)\
\n#CUT_VOLTS          = (modes 0 & 1 only, if not using auto voltage sampling)\
\n')
            print '*** new material file,', self.materialsFile, 'created'

    def get_materials(self):
        name = 'Default'
        p_height = self.builder.get_object('pierce-height').get_value()
        p_delay = self.builder.get_object('pierce-delay').get_value()
        pj_height = self.builder.get_object('puddle-jump-height').get_value()
        pj_delay = self.builder.get_object('puddle-jump-delay').get_value()
        c_height = self.builder.get_object('cut-height').get_value()
        c_speed = self.builder.get_object('cut-feed-rate').get_value()
        c_amps = self.builder.get_object('cut-amps').get_value()
        c_volts = self.builder.get_object('cut-volts').get_value()
        self.builder.get_object('material').set_active(0)
        try:
            with open(self.materialsFile, 'r') as f_in:
                for line in f_in:
                    if not line.startswith('#'):
                        if line.startswith('[') and line.strip().endswith(']') and not 'VERSION' in line:
                            self.materialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
                            if name != 'Default':
                                iter = self.builder.get_object('materials').append()
                                self.builder.get_object('materials').set(iter, 0, name, 1, p_height, 2, p_delay, 3, pj_height, 4, pj_delay, 5, c_height, 6, c_speed, 7, c_amps, 8, c_volts)
                            name = line.strip().lstrip('[').rstrip(']')
                            p_height = p_delay = pj_height = pj_delay = c_height = c_speed = c_amps = c_volts = 0
                        elif line.startswith('PIERCE_HEIGHT'):
                            p_height = float(line.split('=')[1].strip())
                        elif line.startswith('PIERCE_DELAY'):
                            p_delay = float(line.split('=')[1].strip())
                        elif line.startswith('PUDDLE_JUMP_HEIGHT'):
                            pj_height = float(line.split('=')[1].strip())
                        elif line.startswith('PUDDLE_JUMP_DELAY'):
                            pj_delay = float(line.split('=')[1].strip())
                        elif line.startswith('CUT_HEIGHT'):
                            c_height = float(line.split('=')[1].strip())
                        elif line.startswith('CUT_SPEED'):
                            c_speed = float(line.split('=')[1].strip())
                        elif line.startswith('CUT_AMPS'):
                            c_amps = float(line.split('=')[1].strip())
                        elif line.startswith('CUT_VOLTS'):
                            c_volts = float(line.split('=')[1].strip())
                self.materialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
                if name != 'Default':
                    iter = self.builder.get_object('materials').append()
                    self.builder.get_object('materials').set(iter, 0, name, 1, p_height, 2, p_delay, 3, pj_height, 4, pj_delay, 5, c_height, 6, c_speed, 7, c_amps, 8, c_volts)
        except:
            print '*** materials file,', self.materialsFile, 'is invalid'

    def on_save_clicked(self,widget,data=None):
        self.save_settings()
        self.materialsList[0][1] = self.builder.get_object('pierce-height').get_value()
        self.materialsList[0][2] = self.builder.get_object('pierce-delay').get_value()
        self.materialsList[0][3] = self.builder.get_object('puddle-jump-height').get_value()
        self.materialsList[0][4] = self.builder.get_object('puddle-jump-delay').get_value()
        self.materialsList[0][5] = self.builder.get_object('cut-height').get_value()
        self.materialsList[0][6] = self.builder.get_object('cut-feed-rate').get_value()
        self.materialsList[0][7] = self.builder.get_object('cut-amps').get_value()
        self.materialsList[0][8] = self.builder.get_object('cut-volts').get_value()
        self.builder.get_object('material').set_active(0)

    def on_reload_clicked(self,widget,data=None):
        self.materialsUpdate = True
        self.load_settings()
        self.materialsList = []
        for row in range(len(self.builder.get_object('materials')) - 1, 0, -1):
            self.builder.get_object('materials').remove(self.builder.get_object('materials')[row].iter) 
        self.get_materials()
        self.materialsUpdate = False

    def on_material_changed(self,widget,data=None):
        if not self.materialsUpdate:
            material = self.builder.get_object('material').get_active()
            self.builder.get_object('pierce-height').set_value(self.materialsList[material][1])
            self.builder.get_object('pierce-delay').set_value(self.materialsList[material][2])
            self.builder.get_object('puddle-jump-height').set_value(self.materialsList[material][3])
            self.builder.get_object('puddle-jump-delay').set_value(self.materialsList[material][4])
            self.builder.get_object('cut-height').set_value(self.materialsList[material][5])
            self.builder.get_object('cut-feed-rate').set_value(self.materialsList[material][6])
            self.builder.get_object('cut-amps').set_value(self.materialsList[material][7])
            self.builder.get_object('cut-volts').set_value(self.materialsList[material][8])

    def on_heightLower_pressed(self, widget):
        self.torch_height -= 0.1
        self.builder.get_object('height-override').set_text('%0.1f V' % (self.torch_height))
        hal.set_p('plasmac.height-override','%f' %(self.torch_height))

    def on_heightRaise_pressed(self, widget):
        self.torch_height += 0.1
        self.builder.get_object('height-override').set_text('%0.1f V' % (self.torch_height))
        hal.set_p('plasmac.height-override','%f' %(self.torch_height))

    def on_heightReset_pressed(self, widget):
        self.torch_height = 0
        self.builder.get_object('height-override').set_text('%0.1f V' % (self.torch_height))
        hal.set_p('plasmac.height-override','%f' %(self.torch_height))

    def on_button1_pressed(self,event):
        self.user_button_pressed(self.iniButtonCode[1])

    def on_button1_released(self,event):
        self.user_button_released(self.iniButtonCode[1])

    def on_button2_pressed(self,event):
        self.user_button_pressed(self.iniButtonCode[2])

    def on_button2_released(self,event):
        self.user_button_released(self.iniButtonCode[2])

    def on_button3_pressed(self,event):
        self.user_button_pressed(self.iniButtonCode[3])

    def on_button3_released(self,event):
        self.user_button_released(self.iniButtonCode[3])

    def on_button4_pressed(self,event):
        self.user_button_pressed(self.iniButtonCode[4])

    def on_button4_released(self,event):
        self.user_button_released(self.iniButtonCode[4])

    def on_button5_pressed(self,event):
        self.user_button_pressed(self.iniButtonCode[5])

    def on_button5_released(self,event):
        self.user_button_released(self.iniButtonCode[5])

    def on_button6_pressed(self,event):
        self.user_button_pressed(self.iniButtonCode[6])

    def on_button6_released(self,event):
        self.user_button_released(self.iniButtonCode[6])

    def user_button_pressed(self, commands):
        if not commands: return
        if commands.lower() == 'dry-run':
            hal.set_p('plasmac.dry-run-start','1')
        elif commands.lower() == 'ohmic-test':
            hal.set_p('plasmac.ohmic-test','1')
        elif commands.lower() == 'probe-test':
            hal.set_p('plasmac.probe-test','1')
        else:
            for command in commands.split('\\'):
                if command.strip()[0] == '%':
                    command = command.strip().strip('%') + '&'
                    Popen(command,stdout=PIPE,stderr=PIPE, shell=True)
                else:
                    if '[' in command:
                        newCommand = subCommand = ''
                        for char in command:
                            if char == '[':
                                subCommand += char
                            elif char == ']':
                                subCommand += ' '
                            elif subCommand.startswith('[') and char != ' ':
                                subCommand += char
                            elif subCommand.startswith('[') and char == ' ':
                                f1, f2 = subCommand.split()
                                newCommand += self.i.find(f1[1:],f2)
                                newCommand += ' '
                                subCommand = ''
                            else:
                                newCommand += char
                        if subCommand.startswith('['):
                            f1, f2 = subCommand.split()
                            newCommand += self.i.find(f1[1:],f2)
                            newCommand += ' '
                        command = newCommand
                    self.s.poll()
                    if not self.s.estop and self.s.enabled and self.s.homed and (self.s.interp_state == linuxcnc.INTERP_IDLE):
                        mode = self.s.task_mode
                        if mode != linuxcnc.MODE_MDI:
                            mode = self.s.task_mode
                            self.c.mode(linuxcnc.MODE_MDI)
                            self.c.wait_complete()
                        self.c.mdi(command)
                        self.s.poll()
                        while self.s.interp_state != linuxcnc.INTERP_IDLE:
                            self.s.poll()
                        self.c.mode(mode)
                        self.c.wait_complete()

    def user_button_released(self, commands):
        if not commands: return
        if commands.lower() == 'dry-run':
            hal.set_p('plasmac.dry-run-start','0')
        elif commands.lower() == 'ohmic-test':
            hal.set_p('plasmac.ohmic-test','0')
        elif commands.lower() == 'probe-test':
            hal.set_p('plasmac.probe-test','0')

    def on_forward_pressed(self, widget):
        speed = self.builder.get_object('paused-motion-speed').get_value()
        hal.set_p('plasmac.paused-motion-speed','%f' %(speed))

    def on_forward_released(self, widget):
        speed = 0
        hal.set_p('plasmac.paused-motion-speed','%f' %(speed))

    def on_reverse_pressed(self, widget):
        speed = self.builder.get_object('paused-motion-speed').get_value() * -1
        hal.set_p('plasmac.paused-motion-speed','%f' %(speed))

    def on_reverse_released(self, widget):
        speed = 0
        hal.set_p('plasmac.paused-motion-speed','%f' %(speed))

    def on_setupFeedRate_value_changed(self, widget):
        self.builder.get_object('probe-feed-rate-adj').configure(self.builder.get_object('probe-feed-rate').get_value(),0,self.builder.get_object('setup-feed-rate').get_value(),1,0,0)
        
    def configure_widgets(self):
        # set_digits = number of digits after decimal
        # configure  = (value, lower limit, upper limit, step size, 0, 0)
        self.builder.get_object('arc-fail-delay').set_digits(1)
        self.builder.get_object('arc-fail-delay-adj').configure(1,0.1,60,0.1,0,0)
        self.builder.get_object('arc-ok-low').set_digits(1)
        self.builder.get_object('arc-ok-low-adj').configure(0,0,200,0.5,0,0)
        self.builder.get_object('arc-ok-high').set_digits(1)
        self.builder.get_object('arc-ok-high-adj').configure(0,0,200,0.5,0,0)
        self.builder.get_object('arc-max-starts').set_digits(0)
        self.builder.get_object('arc-max-starts-adj').configure(3,1,9,1,0,0)
        self.builder.get_object('arc-restart-delay').set_digits(0)
        self.builder.get_object('arc-restart-delay-adj').configure(1,1,60,1,0,0)
        self.builder.get_object('arc-voltage-offset').set_digits(1)
        self.builder.get_object('arc-voltage-offset-adj').configure(0,-100,100,0.1,0,0)
        self.builder.get_object('arc-voltage-scale').set_digits(2)
        self.builder.get_object('arc-voltage-scale-adj').configure(1,0.01,99,0.01,0,0)
        self.builder.get_object('cornerlock-enable').set_active(1)
        self.builder.get_object('cornerlock-threshold').set_digits(0)
        self.builder.get_object('cornerlock-threshold-adj').configure(90,1,99,1,0,0)
        self.builder.get_object('cut-amps').set_digits(0)
        self.builder.get_object('cut-amps-adj').configure(45,0,999,1,0,0)
        self.builder.get_object('cut-volts').set_digits(1)
        self.builder.get_object('cut-volts-adj').configure(122,50,300,0.1,0,0)
        self.builder.get_object('kerfcross-enable').set_active(1)
        self.builder.get_object('kerfcross-threshold').set_digits(1)
        self.builder.get_object('kerfcross-threshold-adj').configure(3,1,10,0.1,0,0)
        self.builder.get_object('max-offset-velocity-in').set_label(str(int(self.thcFeedRate)))
        self.builder.get_object('ohmic-max-attempts').set_digits(0)
        self.builder.get_object('ohmic-max-attempts-adj').configure(0,0,10,1,0,0)
        self.builder.get_object('pid-p-gain').set_digits(0)
        self.builder.get_object('pid-p-gain-adj').configure(25,0,1000,1,0,0)
        self.builder.get_object('pid-i-gain').set_digits(0)
        self.builder.get_object('pid-i-gain-adj').configure(0,0,1000,1,0,0)
        self.builder.get_object('pid-d-gain').set_digits(0)
        self.builder.get_object('pid-d-gain-adj').configure(0,0,1000,1,0,0)
        self.builder.get_object('pierce-delay').set_digits(1)
        self.builder.get_object('pierce-delay-adj').configure(0.5,0,10,0.1,0,0)
        self.builder.get_object('puddle-jump-height').set_digits(0)
        self.builder.get_object('puddle-jump-height-adj').configure(0,0,200,1,0,0)
        self.builder.get_object('puddle-jump-delay').set_digits(2)
        self.builder.get_object('puddle-jump-delay-adj').configure(0,0,9,0.01,0,0)
        self.builder.get_object('thc-enable').set_active(1)
        self.builder.get_object('thc-threshold').set_digits(2)
        self.builder.get_object('thc-threshold-adj').configure(1,0.05,9,0.01,0,0)
        self.builder.get_object('torch-off-delay').set_digits(1)
        self.builder.get_object('torch-off-delay-adj').configure(0,0,9,0.1,0,0)
        self.builder.get_object('torch-pulse-time').set_digits(1)
        self.builder.get_object('torch-pulse-time-adj').configure(.5,.1,5,0.1,0,0)
        self.builder.get_object('use-auto-volts').set_active(1)
        if self.i.find('TRAJ', 'LINEAR_UNITS').lower() == 'mm':
            self.builder.get_object('cut-feed-rate').set_digits(0)
            self.builder.get_object('cut-feed-rate-adj').configure(4000,50,9999,1,0,0)
            self.builder.get_object('cut-height').set_digits(1)
            self.builder.get_object('cut-height-adj').configure(1,0,25.4,0.1,0,0)
            self.builder.get_object('float-switch-travel').set_digits(2)
            self.builder.get_object('float-switch-travel-adj').configure(1.5,0,9,0.01,0,0)
            self.builder.get_object('pierce-height').set_digits(1)
            self.builder.get_object('pierce-height-adj').configure(4,0,25.4,0.1,0,0)
            self.builder.get_object('probe-feed-rate').set_digits(0)
            self.builder.get_object('probe-feed-rate-adj').configure(1000,1,self.thcFeedRate,1,0,0)
            self.builder.get_object('probe-start-height').set_digits(0)
            self.builder.get_object('probe-start-height-adj').configure(0,1,self.maxHeight,1,0,0)
            self.builder.get_object('safe-height').set_digits(0)
            self.builder.get_object('safe-height-adj').configure(20,1,99,1,0,0)
            self.builder.get_object('setup-feed-rate').set_digits(0)
            self.builder.get_object('setup-feed-rate-adj').configure(int(self.thcFeedRate * 0.8),1,self.thcFeedRate,1,0,0)
            self.builder.get_object('skip-ihs-distance').set_digits(0)
            self.builder.get_object('skip-ihs-distance-adj').configure(0,0,999,1,0,0)
        elif self.i.find('TRAJ', 'LINEAR_UNITS').lower() == 'inch':
            self.builder.get_object('cut-feed-rate').set_digits(1)
            self.builder.get_object('cut-feed-rate-adj').configure(160,2,400,0.1,0,0)
            self.builder.get_object('cut-height').set_digits(2)
            self.builder.get_object('cut-height-adj').configure(0.04,0,1,0.01,0,0)
            self.builder.get_object('float-switch-travel').set_digits(3)
            self.builder.get_object('float-switch-travel-adj').configure(0.06,0,1,0.001,0,0)
            self.builder.get_object('pierce-height').set_digits(2)
            self.builder.get_object('pierce-height-adj').configure(0.16,0,1,0.01,0,0)
            self.builder.get_object('probe-feed-rate').set_digits(1)
            self.builder.get_object('probe-feed-rate-adj').configure(40,.1,self.thcFeedRate,0.1,0,0)
            self.builder.get_object('probe-start-height').set_digits(2)
            self.builder.get_object('probe-start-height-adj').configure(19,.1,self.maxHeight,0.01,0,0)
            self.builder.get_object('safe-height').set_digits(2)
            self.builder.get_object('safe-height-adj').configure(0.75,0.04,4,0.01,0,0)
            self.builder.get_object('setup-feed-rate').set_digits(1)
            self.builder.get_object('setup-feed-rate-adj').configure(int(self.thcFeedRate * 0.8),.1,self.thcFeedRate,.1,0,0)
            self.builder.get_object('skip-ihs-distance').set_digits(1)
            self.builder.get_object('skip-ihs-distance-adj').configure(0,0,99,.1,0,0)
        else:
            print '*** incorrect [TRAJ]LINEAR_UNITS in ini file'

    def periodic(self):
        self.s.poll()
#        if hal.get_value('halui.program.is-idle'):
#            self.builder.get_object('pausedMotionSpeedAdj').set_value(0)
        mode = hal.get_value('plasmac.mode')
        units = hal.get_value('halui.machine.units-per-mm')
        maxPidP = self.thcFeedRate / units * 0.1
        isIdleHomed = True
        isIdleOn = True
        if hal.get_value('halui.program.is-idle') and hal.get_value('halui.machine.is-on'):
            if hal.get_value('plasmac.arc-ok-out'):
                isIdleOn = False
            for joint in range(0,int(self.i.find('KINS','JOINTS'))):
                    if not self.s.homed[joint]:
                        isIdleHomed = False
                        break
        else:
            isIdleHomed = False
            isIdleOn = False 
        for n in range(1,6):
            if self.iniButtonCode[n] in ['ohmic-test']:
                if isIdleOn or hal.get_value('halui.program.is-paused'):
                    self.builder.get_object('button' + str(n)).set_sensitive(True)
                else:
                    self.builder.get_object('button' + str(n)).set_sensitive(False)
            elif not self.iniButtonCode[n] in ['ohmic-test'] and not self.iniButtonCode[n].startswith('%'):
                if isIdleHomed:
                    self.builder.get_object('button' + str(n)).set_sensitive(True)
                    if self.iniButtonCode[n] == 'dry-run' and not self.s.file:
                        self.builder.get_object('button' + str(n)).set_sensitive(False)
                else:
                    self.builder.get_object('button' + str(n)).set_sensitive(False)
        if hal.get_value('halui.program.is-running'):
            self.builder.get_object('height-frame').set_sensitive(True)
        else:
            self.builder.get_object('height-frame').set_sensitive(False)
        if hal.get_value('halui.machine.is-on') and not hal.get_value('halui.program.is-running'):
            self.builder.get_object('torch-pulse-start').set_sensitive(True)
        else:
            self.builder.get_object('torch-pulse-start').set_sensitive(False)
        if hal.get_value('halui.program.is-paused') or hal.get_value('plasmac.paused-motion-speed'):
            self.builder.get_object('forward').set_sensitive(True)
            self.builder.get_object('reverse').set_sensitive(True)
        else:
            self.builder.get_object('forward').set_sensitive(False)
            self.builder.get_object('reverse').set_sensitive(False)
        if mode != self.oldMode:
            if mode == 0:
                self.builder.get_object('arc-ok-high').show()
                self.builder.get_object('arc-ok-high-label').set_text('OK High Volts')
                self.builder.get_object('arc-ok-low').show()
                self.builder.get_object('arc-ok-low-label').set_text('OK Low Volts')
                self.builder.get_object('arc-voltage').show()
                self.builder.get_object('arc-voltage-label').set_text('Arc Voltage')
                self.builder.get_object('arc-voltage-scale').show()
                self.builder.get_object('arc-voltage-scale-label').set_text('Voltage Scale')
                self.builder.get_object('arc-voltage-offset').show()
                self.builder.get_object('arc-voltage-offset-label').set_text('Voltage Offset')
                self.builder.get_object('auto-box').show()
                self.builder.get_object('height-frame').show()
                self.builder.get_object('kerf-box').show()
                self.builder.get_object('kerf-label').show()
                self.builder.get_object('kerf-frame').set_shadow_type(gtk.SHADOW_OUT)
                self.builder.get_object('pid-p-gain-adj').configure(self.builder.get_object('pid-p-gain-adj').get_value(),1,maxPidP,1,0,0)
                self.builder.get_object('pid-p-label').set_text('Speed (PID P)')
                self.builder.get_object('pid-i-gain').show()
                self.builder.get_object('pid-i-label').set_text('PID I GAIN')
                self.builder.get_object('pid-d-gain').show()
                self.builder.get_object('pid-d-label').set_text('PID D GAIN')
                self.builder.get_object('threshold-box').show()
                self.builder.get_object('volts-box').show()
            elif mode == 1:
                self.builder.get_object('arc-ok-high').hide()
                self.builder.get_object('arc-ok-high-label').set_text('')
                self.builder.get_object('arc-ok-low').hide()
                self.builder.get_object('arc-ok-low-label').set_text('')
                self.builder.get_object('arc-voltage').show()
                self.builder.get_object('arc-voltage-label').set_text('Arc Voltage')
                self.builder.get_object('arc-voltage-scale').show()
                self.builder.get_object('arc-voltage-scale-label').set_text('Voltage Scale')
                self.builder.get_object('arc-voltage-offset').show()
                self.builder.get_object('arc-voltage-offset-label').set_text('Voltage Offset')
                self.builder.get_object('auto-box').show()
                self.builder.get_object('height-frame').show()
                self.builder.get_object('kerf-box').show()
                self.builder.get_object('kerf-label').show()
                self.builder.get_object('kerf-frame').set_shadow_type(gtk.SHADOW_OUT)
                self.builder.get_object('pid-p-gain-adj').configure(self.builder.get_object('pid-p-gain-adj').get_value(),1,maxPidP,1,0,0)
                self.builder.get_object('pid-p-label').set_text('Speed (PID P)')
                self.builder.get_object('pid-i-gain').show()
                self.builder.get_object('pid-i-label').set_text('PID I GAIN')
                self.builder.get_object('pid-d-gain').show()
                self.builder.get_object('pid-d-label').set_text('PID D GAIN')
                self.builder.get_object('threshold-box').show()
                self.builder.get_object('volts-box').show()
            elif mode == 2:
                self.builder.get_object('arc-ok-high').hide()
                self.builder.get_object('arc-ok-high-label').set_text('')
                self.builder.get_object('arc-ok-low').hide()
                self.builder.get_object('arc-ok-low-label').set_text('')
                self.builder.get_object('arc-voltage').hide()
                self.builder.get_object('arc-voltage-label').set_text('')
                self.builder.get_object('arc-voltage-scale').hide()
                self.builder.get_object('arc-voltage-scale-label').set_text('')
                self.builder.get_object('arc-voltage-offset').hide()
                self.builder.get_object('arc-voltage-offset-label').set_text('')
                self.builder.get_object('auto-box').hide()
                self.builder.get_object('height-frame').hide()
                self.builder.get_object('kerf-box').hide()
                self.builder.get_object('kerf-label').hide()
                self.builder.get_object('kerf-frame').set_shadow_type(gtk.SHADOW_NONE)
                self.builder.get_object('pid-p-gain-adj').configure(self.builder.get_object('pid-p-gain-adj').get_value(),1,100,1,0,0)
                self.builder.get_object('pid-p-label').set_text('Speed (%)')
                self.builder.get_object('pid-i-gain').hide()
                self.builder.get_object('pid-i-label').set_text('')
                self.builder.get_object('pid-d-gain').hide()
                self.builder.get_object('pid-d-label').set_text('')
                self.builder.get_object('threshold-box').hide()
                self.builder.get_object('volts-box').hide()
            else:
                pass
            self.oldMode = mode
        self.builder.get_object('config').set_sensitive(not hal.get_value('plasmac_panel.config-disable'))
        return True

    def load_settings(self):
        for item in widget_defaults(select_widgets(self.builder.get_objects(), hal_only=False,output_only = True)):
            if item != 'height-override':
                self.configDict[item] = '0'
        convertFile = False
        if os.path.exists(self.configFile):
            try:
                tmpDict = {}
                with open(self.configFile, 'r') as f_in:
                    for line in f_in:
                        if not line.startswith('#') and not line.startswith('[') and not line.startswith('\n'):
                            if 'version' in line or 'signature' in line:
                                convertFile = True
                            else:
                                (keyTmp, value) = line.strip().replace(" ", "").split('=')
                                if value == 'True':value = True
                                if value == 'False':value = False
                                key = ''
                                for item in keyTmp:
                                    if item.isupper():
                                        if item == 'C':
                                            key += 'c'
                                        else:
                                            key += '-%s' % (item.lower())
                                            convertFile = True
                                    else:
                                        key += item
                                if key in self.configDict:
                                    self.configDict[key] = value
                                    tmpDict[key] = value
            except:
                print '*** plasmac configuration file,', self.configFile, 'is invalid ***'
            for item in self.configDict:
                if isinstance(self.builder.get_object(item), gladevcp.hal_widgets.HAL_SpinButton):
                    if item in tmpDict:
                        self.builder.get_object(item).set_value(float(self.configDict.get(item)))
                    else:
                        self.builder.get_object(item).set_value(0)
                        print '***', item, 'missing from', self.configFile
                elif isinstance(self.builder.get_object(item), gladevcp.hal_widgets.HAL_CheckButton):
                    if item in tmpDict:
                        self.builder.get_object(item).set_active(int(self.configDict.get(item)))
                    else:
                        self.builder.get_object(item).set_active(False)
                        print '***', item, 'missing from', self.configFile
                elif item == 'torch-pulse-time' or item == 'paused-motion-speed':
                    if item in tmpDict:
                        self.builder.get_object(item).set_value(float(self.configDict.get(item)))
                    else:
                        self.builder.get_object(item).set_value(0)
                        print '***', item, 'missing from', self.configFile
            if convertFile:
                print '*** converting', self.configFile, 'to new format'
                self.save_settings()
        else:
            self.save_settings()
            print '*** creating new plasmac configuration file,', self.configFile

    def save_settings(self):
        try:
            with open(self.configFile, 'w') as f_out:
                f_out.write('#plasmac configuration file, format is:\n#name = value\n\n')
                for key in sorted(self.configDict.iterkeys()):
                    if isinstance(self.builder.get_object(key), gladevcp.hal_widgets.HAL_SpinButton):
                        value = self.builder.get_object(key).get_value()
                        f_out.write(key + '=' + str(value) + '\n')
                    elif isinstance(self.builder.get_object(key), gladevcp.hal_widgets.HAL_CheckButton):
                        value = self.builder.get_object(key).get_active()
                        f_out.write(key + '=' + str(value) + '\n')
                    elif key == 'torch-pulse-time' or key == 'paused-motion-speed':
                        value = self.builder.get_object(key).get_value()
                        f_out.write(key + '=' + str(value) + '\n')
        except:
            print '*** error opening', self.configFile

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.i = linuxcnc.ini(os.environ['INI_FILE_NAME'])
        self.s = linuxcnc.stat();
        self.c = linuxcnc.command()
        gtk.settings_get_default().set_property('gtk-theme-name', self.i.find('PLASMAC', 'THEME'))
        font = self.i.find('PLASMAC', 'FONT') or 'sans 10'
        gtk.settings_get_default().set_property('gtk-font-name', font)
        configDisable = self.i.find('PLASMAC', 'CONFIG_DISABLE') or '0'
        hal.set_p('plasmac_panel.config-disable',configDisable)
        self.thcFeedRate = (float(self.i.find('AXIS_Z', 'MAX_VELOCITY')) * \
                              float(self.i.find('AXIS_Z', 'OFFSET_AV_RATIO'))) * 60
        hal.set_p('plasmac.thc-feed-rate','%f' % (self.thcFeedRate))
        self.configFile = self.i.find('EMC', 'MACHINE').lower() + '.cfg'
        self.materialsFile = self.i.find('EMC', 'MACHINE').lower() + '.mat'
        self.materialsList = []
        self.configDict = {}
        hal.set_p('plasmac.mode','%d' % (int(self.i.find('PLASMAC','MODE') or '0')))
        self.oldMode = 9
        self.materialsUpdate = False
        self.maxHeight = hal.get_value('ini.z.max_limit')
        self.configure_widgets()
        self.builder.get_object('probe-feed-rate-adj').set_upper(self.builder.get_object('setup-feed-rate').get_value())
        self.torch_height = 0
        self.builder.get_object('height-override').set_text('%0.1f V' % (self.torch_height))
        hal.set_p('plasmac.height-override','%f' % (self.torch_height))
        self.load_settings()
        self.check_materials_file()
        self.get_materials()
        self.iniButtonName = ['Names']
        self.iniButtonCode = ['Codes']
        for button in range(1,7):
            bname = self.i.find('PLASMAC', 'BUTTON_' + str(button) + '_NAME') or '0'
            self.iniButtonName.append(bname)
            self.iniButtonCode.append(self.i.find('PLASMAC', 'BUTTON_' + str(button) + '_CODE'))
            if bname != '0':
                bname = bname.split('\\')
                if len(bname) > 1:
                    blabel = bname[0] + '\n' + bname[1]
                else:
                    blabel = bname[0]
                self.builder.get_object('button' + str(button)).set_label(blabel)
                self.builder.get_object('button' + str(button)).children()[0].set_justify(gtk.JUSTIFY_CENTER)
        gobject.timeout_add(100, self.periodic)

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
