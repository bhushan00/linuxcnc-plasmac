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
#plasmac materials file\
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
#plasmac material file\
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
        self.builder.get_object('pid-p-gain').set_digits(0)
        self.builder.get_object('pid-p-gain-adj').configure(25,0,1000,1,0,0)
        self.builder.get_object('pierce-delay').set_digits(1)
        self.builder.get_object('pierce-delay-adj').configure(0.5,0,10,0.1,0,0)
        self.builder.get_object('puddle-jump-height').set_digits(0)
        self.builder.get_object('puddle-jump-height-adj').configure(0,0,200,1,0,0)
        self.builder.get_object('puddle-jump-delay').set_digits(2)
        self.builder.get_object('puddle-jump-delay-adj').configure(0,0,9,0.01,0,0)
        self.builder.get_object('thc-enable').set_active(1)
        self.builder.get_object('thc-threshold').set_digits(2)
        self.builder.get_object('thc-threshold-adj').configure(1,0.05,9,0.01,0,0)
        self.builder.get_object('use-auto-volts').set_active(1)
        if self.i.find('TRAJ', 'LINEAR_UNITS').lower() == 'mm':
            self.builder.get_object('cut-feed-rate').set_digits(0)
            self.builder.get_object('cut-feed-rate-adj').configure(4000,50,9999,1,0,0)
            self.builder.get_object('cut-height').set_digits(2)
            self.builder.get_object('cut-height-adj').configure(1,0,25,0.01,0,0)
            self.builder.get_object('pierce-height').set_digits(2)
            self.builder.get_object('pierce-height-adj').configure(4,0,25,0.01,0,0)
        elif self.i.find('TRAJ', 'LINEAR_UNITS').lower() == 'inch':
            self.builder.get_object('cut-feed-rate').set_digits(1)
            self.builder.get_object('cut-feed-rate-adj').configure(160,2,400,0.1,0,0)
            self.builder.get_object('cut-height').set_digits(3)
            self.builder.get_object('cut-height-adj').configure(0.04,0,1,0.001,0,0)
            self.builder.get_object('pierce-height').set_digits(3)
            self.builder.get_object('pierce-height-adj').configure(0.16,0,1,0.001,0,0)
        else:
            print '*** incorrect [TRAJ]LINEAR_UNITS in ini file'

    def periodic(self):
        mode = hal.get_value('plasmac.mode')
        units = hal.get_value('halui.machine.units-per-mm')
        maxPidP = self.thcFeedRate / units * 0.1
        if mode != self.oldMode:
            if mode == 0:
                self.builder.get_object('auto-box').show()
                self.builder.get_object('kerf-box').show()
                self.builder.get_object('kerf-label').show()
                self.builder.get_object('kerf-frame').set_shadow_type(gtk.SHADOW_OUT)
                self.builder.get_object('pid-p-gain-adj').configure(self.builder.get_object('pid-p-gain-adj').get_value(),1,maxPidP,1,0,0)
                self.builder.get_object('pid-p-label').set_text('Speed (PID P)')
                self.builder.get_object('threshold-box').show()
                self.builder.get_object('volts-box').show()
            elif mode == 1:
                self.builder.get_object('auto-box').show()
                self.builder.get_object('kerf-box').show()
                self.builder.get_object('kerf-label').show()
                self.builder.get_object('kerf-frame').set_shadow_type(gtk.SHADOW_OUT)
                self.builder.get_object('pid-p-gain-adj').configure(self.builder.get_object('pid-p-gain-adj').get_value(),1,maxPidP,1,0,0)
                self.builder.get_object('pid-p-label').set_text('Speed (PID P)')
                self.builder.get_object('threshold-box').show()
                self.builder.get_object('volts-box').show()
            elif mode == 2:
                self.builder.get_object('auto-box').hide()
                self.builder.get_object('kerf-box').hide()
                self.builder.get_object('kerf-label').hide()
                self.builder.get_object('kerf-frame').set_shadow_type(gtk.SHADOW_NONE)
                self.builder.get_object('pid-p-gain-adj').configure(self.builder.get_object('pid-p-gain-adj').get_value(),1,100,1,0,0)
                self.builder.get_object('pid-p-label').set_text('Speed (%)')
                self.builder.get_object('threshold-box').hide()
                self.builder.get_object('volts-box').hide()
            else:
                pass
            self.oldMode = mode
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
        self.i = linuxcnc.ini(os.environ['INI_FILE_NAME'])
        self.thcFeedRate = (float(self.i.find('AXIS_Z', 'MAX_VELOCITY')) * \
                              float(self.i.find('AXIS_Z', 'OFFSET_AV_RATIO'))) * 60
        hal.set_p('plasmac.thc-feed-rate','%f' % (self.thcFeedRate))
        self.configFile = self.i.find('EMC', 'MACHINE').lower() + '_run.cfg'
        self.prefFile = self.i.find('EMC', 'MACHINE') + '.pref'
        self.materialsFile = self.i.find('EMC', 'MACHINE').lower() + '.mat'
        self.materialsList = []
        self.configDict = {}
        hal.set_p('plasmac.mode','%d' % (int(self.i.find('PLASMAC','MODE') or '0')))
        self.oldMode = 9
        self.materialsUpdate = False
        self.configure_widgets()
        self.check_materials_file()
        self.get_materials()
        self.load_settings()
        self.set_theme()
        gobject.timeout_add(100, self.periodic)

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
