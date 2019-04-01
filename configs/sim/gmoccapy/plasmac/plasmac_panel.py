#!/usr/bin/env python

'''
plasmac_panel.py
Copyright (C) 2019  Phillip A Carter

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
import hal, hal_glib
from   gladevcp.persistence import widget_defaults,select_widgets
import gladevcp

class linuxcncInterface(object):

    def __init__(self):
        self.linuxcncIniFile = linuxcnc.ini(os.environ['INI_FILE_NAME'])

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
        self.builder.get_object('use-auto-volts').set_active(1)
        if self.lcnc.linuxcncIniFile.find('TRAJ', 'LINEAR_UNITS').lower() == 'mm':
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
            self.builder.get_object('safe-height').set_digits(0)
            self.builder.get_object('safe-height-adj').configure(20,1,99,1,0,0)
            self.builder.get_object('setup-feed-rate').set_digits(0)
            self.builder.get_object('setup-feed-rate-adj').configure(int(self.thcFeedRate * 0.8),1,self.thcFeedRate,1,0,0)
            self.builder.get_object('skip-ihs-distance').set_digits(0)
            self.builder.get_object('skip-ihs-distance-adj').configure(0,0,999,1,0,0)
        elif self.lcnc.linuxcncIniFile.find('TRAJ', 'LINEAR_UNITS').lower() == 'inch':
            self.builder.get_object('cut-feed-rate').set_digits(1)
            self.builder.get_object('cut-feed-rate-adj').configure(160,2,400,0.1,0,0)
            self.builder.get_object('cut-height').set_digits(2)
            self.builder.get_object('cut-height-adj').configure(0.04,0,1,0.01,0,0)
            self.builder.get_object('float-switch-travel').set_digits(3)
            self.builder.get_object('float-switch-travel-adj').configure(0.06,0,1,0.001,0,0)
            self.builder.get_object('pierce-height').set_digits(2)
            self.builder.get_object('pierce-height-adj').configure(0.16,0,1,0.01,0,0)
            self.builder.get_object('probe-feed-rate').set_digits(1)
            self.builder.get_object('probe-feed-rate-adj').configure(40,.1,self.thcFeedRate,.1,0,0)
            self.builder.get_object('safe-height').set_digits(2)
            self.builder.get_object('safe-height-adj').configure(0.75,0.04,4,0.01,0,0)
            self.builder.get_object('setup-feed-rate').set_digits(1)
            self.builder.get_object('setup-feed-rate-adj').configure(int(self.thcFeedRate * 0.8),.1,self.thcFeedRate,.1,0,0)
            self.builder.get_object('skip-ihs-distance').set_digits(1)
            self.builder.get_object('skip-ihs-distance-adj').configure(0,0,99,.1,0,0)
        else:
            print '*** incorrect [TRAJ]LINEAR_UNITS in ini file'

    def periodic(self):
        mode = hal.get_value('plasmac.mode')
        units = hal.get_value('halui.machine.units-per-mm')
        maxPidP = self.thcFeedRate / units * 0.1
        if self.builder.get_object('material').get_active() != self.materialNum:
            hal.set_p('plasmac_panel.material-ext', '%d' % (self.builder.get_object('material').get_active()))
            self.materialNum = self.builder.get_object('material').get_active()
        elif hal.get_value('plasmac_panel.material-ext') != self.materialNum:
            self.builder.get_object('material').set_active(hal.get_value('plasmac_panel.material-ext'))
            self.materialNum = hal.get_value('plasmac_panel.material-ext')
        if self.builder.get_object('thc-enable').get_active() != self.thcEnable:
            hal.set_p('plasmac_panel.thc-enable-ext', '%d' % (self.builder.get_object('thc-enable').get_active()))
            self.thcEnable = self.builder.get_object('thc-enable').get_active()
        elif hal.get_value('plasmac_panel.thc-enable-ext') != self.thcEnable:
            self.builder.get_object('thc-enable').set_active(hal.get_value('plasmac_panel.thc-enable-ext'))
            self.thcEnable = hal.get_value('plasmac_panel.thc-enable-ext')
        if self.builder.get_object('use-auto-volts').get_active() != self.useAutoVolts:
            hal.set_p('plasmac_panel.use-auto-volts-ext', '%d' % (self.builder.get_object('use-auto-volts').get_active()))
            self.useAutoVolts = self.builder.get_object('use-auto-volts').get_active()
        elif hal.get_value('plasmac_panel.use-auto-volts-ext') != self.useAutoVolts:
            self.builder.get_object('use-auto-volts').set_active(hal.get_value('plasmac_panel.use-auto-volts-ext'))
            self.useAutoVolts = hal.get_value('plasmac_panel.use-auto-volts-ext')
        if round(self.builder.get_object('pierce-height').get_value() - self.pierceHeight, 4):
            hal.set_p('plasmac_panel.pierce-height-ext', str(self.builder.get_object('pierce-height').get_value()))
            self.pierceHeight = (self.builder.get_object('pierce-height').get_value())
        elif round(hal.get_value('plasmac_panel.pierce-height-ext') - self.pierceHeight, 4):
            self.builder.get_object('pierce-height').set_value(hal.get_value('plasmac_panel.pierce-height-ext'))
            self.pierceHeight = hal.get_value('plasmac_panel.pierce-height-ext')
        if round(self.builder.get_object('pierce-delay').get_value() - self.pierceDelay, 4):
            hal.set_p('plasmac_panel.pierce-delay-ext', '%f' % (self.builder.get_object('pierce-delay').get_value()))
            self.pierceDelay = self.builder.get_object('pierce-delay').get_value()
        elif round(hal.get_value('plasmac_panel.pierce-delay-ext') - self.pierceDelay, 4):
            self.builder.get_object('pierce-delay').set_value(hal.get_value('plasmac_panel.pierce-delay-ext'))
            self.pierceDelay = hal.get_value('plasmac_panel.pierce-delay-ext')
        if round(self.builder.get_object('cut-height').get_value() - self.cutHeight, 4):
            hal.set_p('plasmac_panel.cut-height-ext', '%f' % (self.builder.get_object('cut-height').get_value()))
            self.cutHeight = self.builder.get_object('cut-height').get_value()
        elif round(hal.get_value('plasmac_panel.cut-height-ext') - self.cutHeight, 4):
            self.builder.get_object('cut-height').set_value(hal.get_value('plasmac_panel.cut-height-ext'))
            self.cutHeight = hal.get_value('plasmac_panel.cut-height-ext')
        if round(self.builder.get_object('cut-feed-rate').get_value() - self.cutFeedRate, 4):
            hal.set_p('plasmac_panel.cut-feed-rate-ext', '%f' % (self.builder.get_object('cut-feed-rate').get_value()))
            self.cutFeedRate = self.builder.get_object('cut-feed-rate').get_value()
        elif round(hal.get_value('plasmac_panel.cut-feed-rate-ext') - self.cutFeedRate, 4):
            self.builder.get_object('cut-feed-rate').set_value(hal.get_value('plasmac_panel.cut-feed-rate-ext'))
            self.cutFeedRate = hal.get_value('plasmac_panel.cut-feed-rate-ext')
        if round(self.builder.get_object('cut-amps').get_value() - self.cutAmps, 4):
            hal.set_p('plasmac_panel.cut-amps-ext', '%f' % (self.builder.get_object('cut-amps').get_value()))
            self.cutAmps = self.builder.get_object('cut-amps').get_value()
        elif round(hal.get_value('plasmac_panel.cut-amps-ext') - self.cutAmps, 4):
            self.builder.get_object('cut-amps').set_value(hal.get_value('plasmac_panel.cut-amps-ext'))
            self.cutAmps = hal.get_value('plasmac_panel.cut-amps-ext')
        if round(self.builder.get_object('cut-volts').get_value() - self.cutVolts, 4):
            hal.set_p('plasmac_panel.cut-volts-ext', '%f' % (self.builder.get_object('cut-volts').get_value()))
            self.cutVolts = self.builder.get_object('cut-volts').get_value()
        elif round(hal.get_value('plasmac_panel.cut-volts-ext') - self.cutVolts, 4):
            self.builder.get_object('cut-volts').set_value(hal.get_value('plasmac_panel.cut-volts-ext'))
            self.cutVolts = hal.get_value('plasmac_panel.cut-volts-ext')
        if round(self.builder.get_object('puddle-jump-height').get_value() - self.puddleJumpHeight, 4):
            hal.set_p('plasmac_panel.puddle-jump-height-ext', '%f' % (self.builder.get_object('puddle-jump-height').get_value()))
            self.puddleJumpHeight = self.builder.get_object('puddle-jump-height').get_value()
        elif round(hal.get_value('plasmac_panel.puddle-jump-height-ext') - self.puddleJumpHeight, 4):
            self.builder.get_object('puddle-jump-height').set_value(hal.get_value('plasmac_panel.puddle-jump-height-ext'))
            self.puddleJumpHeight = hal.get_value('plasmac_panel.puddle-jump-height-ext')
        if round(self.builder.get_object('puddle-jump-delay').get_value() - self.puddleJumpDelay, 4):
            hal.set_p('plasmac_panel.puddle-jump-delay-ext', '%f' % (self.builder.get_object('puddle-jump-delay').get_value()))
            self.puddleJumpDelay = self.builder.get_object('puddle-jump-delay').get_value()
        elif round(hal.get_value('plasmac_panel.puddle-jump-delay-ext') - self.puddleJumpDelay, 4):
            self.builder.get_object('puddle-jump-delay').set_value(hal.get_value('plasmac_panel.puddle-jump-delay-ext'))
            self.puddleJumpDelay = hal.get_value('plasmac_panel.puddle-jump-delay-ext')
        if mode != self.oldMode:
            if mode == 0:
                self.builder.get_object('arc-ok-high').show()
                self.builder.get_object('arc-ok-high-label').set_text('OK High Volts')
                self.builder.get_object('arc-ok-low').show()
                self.builder.get_object('arc-ok-low-label').set_text('OK Low Volts')
                self.builder.get_object('arc-voltage-scale').show()
                self.builder.get_object('arc-voltage-scale-label').set_text('Voltage Scale')
                self.builder.get_object('arc-voltage-offset').show()
                self.builder.get_object('arc-voltage-offset-label').set_text('Voltage Offset')
                self.builder.get_object('auto-box').show()
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
                self.builder.get_object('arc-voltage-scale').show()
                self.builder.get_object('arc-voltage-scale-label').set_text('Voltage -scale')
                self.builder.get_object('arc-voltage-offset').show()
                self.builder.get_object('arc-voltage-offset-label').set_text('Voltage -offset')
                self.builder.get_object('auto-box').show()
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
                self.builder.get_object('arc-voltage-scale').hide()
                self.builder.get_object('arc-voltage-scale-label').set_text('')
                self.builder.get_object('arc-voltage-offset').hide()
                self.builder.get_object('arc-voltage-offset-label').set_text('')
                self.builder.get_object('auto-box').hide()
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

    def set_theme(self):
        theme = gtk.settings_get_default().get_property('gtk-theme-name')
        if os.path.exists(self.prefFile):
            try:
                with open(self.prefFile, 'r') as f_in:
                    for line in f_in:
                        if 'gtk_theme' in line and not 'Follow System Theme' in line:
                            (item, theme) = line.strip().replace(" ", "").split('=')
            except:
                print '*** configuration file,', self.prefFile, 'is invalid ***'
        gtk.settings_get_default().set_property('gtk-theme-name', theme)

    def load_settings(self):
        for item in widget_defaults(select_widgets(self.builder.get_objects(), hal_only=False,output_only = True)):
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
                elif item == 'torchPulseTime':
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
        hal.set_p('plasmac_panel.material-ext','%d' % (self.builder.get_object('material').get_active()))
        self.materialNum = self.builder.get_object('material').get_active()
        hal.set_p('plasmac_panel.thc-enable-ext','%d' % (self.builder.get_object('thc-enable').get_active()))
        self.thcEnable = self.builder.get_object('thc-enable').get_active()
        hal.set_p('plasmac_panel.use-auto-volts-ext','%d' % (self.builder.get_object('use-auto-volts').get_active()))
        self.useAutoVolts = self.builder.get_object('use-auto-volts').get_active()
        hal.set_p('plasmac_panel.pierce-height-ext','%f' % (self.builder.get_object('pierce-height').get_value()))
        self.pierceHeight = self.builder.get_object('pierce-height').get_value()
        hal.set_p('plasmac_panel.pierce-delay-ext','%f' % (self.builder.get_object('pierce-delay').get_value()))
        self.pierceDelay = self.builder.get_object('pierce-delay').get_value()
        hal.set_p('plasmac_panel.cut-height-ext','%f' % (self.builder.get_object('cut-height').get_value()))
        self.cutHeight = self.builder.get_object('cut-height').get_value()
        hal.set_p('plasmac_panel.cut-feed-rate-ext','%f' % (self.builder.get_object('cut-feed-rate').get_value()))
        self.cutFeedRate = self.builder.get_object('cut-feed-rate').get_value()
        hal.set_p('plasmac_panel.cut-amps-ext','%f' % (self.builder.get_object('cut-amps').get_value()))
        self.cutAmps = self.builder.get_object('cut-amps').get_value()
        hal.set_p('plasmac_panel.cut-volts-ext','%f' % (self.builder.get_object('cut-volts').get_value()))
        self.cutVolts = self.builder.get_object('cut-volts').get_value()
        hal.set_p('plasmac_panel.puddle-jump-height-ext','%f' % (self.builder.get_object('puddle-jump-height').get_value()))
        self.puddleJumpHeight = self.builder.get_object('puddle-jump-height').get_value()
        hal.set_p('plasmac_panel.puddle-jump-delay-ext','%f' % (self.builder.get_object('puddle-jump-delay').get_value()))
        self.puddleJumpDelay = self.builder.get_object('puddle-jump-delay').get_value()

    def save_settings(self):
        try:
            with open(self.configFile, 'w') as f_out:
                f_out.write('#plasmac configuration file, format is:\n#name = value\n\n')
                #for key in self.configDict:
                for key in sorted(self.configDict.iterkeys()):
                    if isinstance(self.builder.get_object(key), gladevcp.hal_widgets.HAL_SpinButton):
                        value = self.builder.get_object(key).get_value()
                        f_out.write(key + '=' + str(value) + '\n')
                    elif isinstance(self.builder.get_object(key), gladevcp.hal_widgets.HAL_CheckButton):
                        value = self.builder.get_object(key).get_active()
                        f_out.write(key + '=' + str(value) + '\n')
                    elif key == 'torchPulseTime':
                        value = self.builder.get_object(key).get_value()
                        f_out.write(key + '=' + str(value) + '\n')
        except:
            print '*** error opening', self.configFile

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.lcnc = linuxcncInterface()
        hal_glib.GPin(halcomp.newpin('config-disable', hal.HAL_BIT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('material-ext', hal.HAL_S32, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('thc-enable-ext', hal.HAL_BIT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('use-auto-volts-ext', hal.HAL_BIT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('pierce-height-ext', hal.HAL_FLOAT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('pierce-delay-ext', hal.HAL_FLOAT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('cut-height-ext', hal.HAL_FLOAT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('cut-feed-rate-ext', hal.HAL_FLOAT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('cut-amps-ext', hal.HAL_FLOAT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('cut-volts-ext', hal.HAL_FLOAT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('puddle-jump-height-ext', hal.HAL_FLOAT, hal.HAL_IN))
        hal_glib.GPin(halcomp.newpin('puddle-jump-delay-ext', hal.HAL_FLOAT, hal.HAL_IN))
        configDisable = self.lcnc.linuxcncIniFile.find('PLASMAC', 'CONFIG_DISABLE') or '0'
        hal.set_p('plasmac_panel.config-disable',configDisable)
        self.thcFeedRate = (float(self.lcnc.linuxcncIniFile.find('AXIS_Z', 'MAX_VELOCITY')) * \
                              float(self.lcnc.linuxcncIniFile.find('AXIS_Z', 'OFFSET_AV_RATIO'))) * 60
        hal.set_p('plasmac.thc-feed-rate','%f' % (self.thcFeedRate))
        self.configFile = self.lcnc.linuxcncIniFile.find('EMC', 'MACHINE').lower() + '.cfg'
        self.prefFile = self.lcnc.linuxcncIniFile.find('EMC', 'MACHINE') + '.pref'
        self.materialsFile = self.lcnc.linuxcncIniFile.find('EMC', 'MACHINE').lower() + '.mat'
        self.materialsList = []
        self.configDict = {}
        self.oldMode = 9
        self.materialsUpdate = False
        self.configure_widgets()
        self.builder.get_object('probe-feed-rate-adj').set_upper(self.builder.get_object('setup-feed-rate').get_value())
        self.check_materials_file()
        self.get_materials()
        self.load_settings()
        self.set_theme()
        gobject.timeout_add(100, self.periodic)

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
