#!/usr/bin/env python

'''
plasmac_run.py
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

    def check_tool_file(self):
        version = '[VERSION 1]'
        tempToolDict = {}
        if os.path.exists(self.toolFile):
            if not version in open(self.toolFile).read():
                print '*** upgrading tool file if we needed to ...'
                # well, it should if we ever need it and we write the code :-)
                #with open(self.toolFile, 'r') as f_in:
                #    for line in f_in:
                #        if not line.strip().startswith('#') and len(line.strip()):
                #            read in old version
                #            convert to new version
                #            write new version
        else: # create a new tool file if it doesn't exist
            with open(self.toolFile, 'w') as f_out:
                f_out.write(\
                    '#plasmac tool file\n'\
                    '#the next line is required for version checking\n'\
                    + version + '\n\n'\
                    '#example only, may be deleted\n'\
                    '#[TOOL_NUMBER_1]    = \n'\
                    '#NAME               = \n'\
                    '#KERF_WIDTH         = \n'\
                    '#THC                = (0 = off, 1 = on)\n'\
                    '#PIERCE_HEIGHT      = \n'\
                    '#PIERCE_DELAY       = \n'\
                    '#PUDDLE_JUMP_HEIGHT = (optional, set to 0 or delete if not required)\n'\
                    '#PUDDLE_JUMP_DELAY  = (optional, set to 0 or delete if not required)\n'\
                    '#CUT_HEIGHT         = \n'\
                    '#CUT_SPEED          = \n'\
                    '#CUT_AMPS           = (optional, only used for operator information)\n'\
                    '#CUT_VOLTS          = (modes 0 & 1 only, if not using auto voltage sampling)\n'\
                    '\n')
            print '*** new material file,', self.toolFile, 'created'

    def get_tools(self):
        t_number = 0
        t_name = 'Default'
        k_width = self.builder.get_object('kerf-width').get_value()
        thc_enable = self.builder.get_object('thc-enable').get_active()
        p_height = self.builder.get_object('pierce-height').get_value()
        p_delay = self.builder.get_object('pierce-delay').get_value()
        pj_height = self.builder.get_object('puddle-jump-height').get_value()
        pj_delay = self.builder.get_object('puddle-jump-delay').get_value()
        c_height = self.builder.get_object('cut-height').get_value()
        c_speed = self.builder.get_object('cut-feed-rate').get_value()
        c_amps = self.builder.get_object('cut-amps').get_value()
        c_volts = self.builder.get_object('cut-volts').get_value()
        try:
            with open(self.toolFile, 'r') as f_in:
                for line in f_in:
                    if not line.startswith('#'):
                        if line.startswith('[TOOL_NUMBER_') and line.strip().endswith(']'):
                            self.toolFileDict[t_number] = [t_name, k_width, thc_enable, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts]
                            a,b,c = line.split('_')
                            t_number = int(c.replace(']',''))
                            t_name = 'none'
                            k_width = thc_enable = p_height = p_delay = pj_height = pj_delay = c_height = c_speed = c_amps = c_volts =  0
                        elif line.startswith('NAME'):
                            t_name = line.split('=')[1].strip()
                        elif line.startswith('KERF_WIDTH'):
                            k_width = float(line.split('=')[1].strip())
                            self.toolKerfMap[t_number] = k_width
                        elif line.startswith('THC'):
                            thc_enable = int(line.split('=')[1].strip())
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
                self.toolFileDict[t_number] = [t_name, k_width, thc_enable, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts]
        except:
            print '*** materials file,', self.materialsFile, 'is invalid'
        self.toolList = []
        for tool in self.toolKerfMap.keys():
            self.toolList.append(tool)
        if sorted(self.toolFileDict,reverse=True)[0] > 99999:
            self.builder.get_object('tool-number-adj').configure(0,0,99999,1,0,0)
            print '*** largest tool number is 99999 ***'
        else:
            self.builder.get_object('tool-number-adj').configure(0,0,sorted(self.toolFileDict,reverse=True)[0],1,0,0)

    def on_save_clicked(self,widget,data=None):
        self.save_settings()
        self.toolFileDict[0][0] = self.builder.get_object('tool-name').get_text()
        self.toolFileDict[0][1] = self.builder.get_object('kerf-width').get_value()
        self.toolFileDict[0][2] = self.builder.get_object('thc-enable').get_active()
        self.toolFileDict[0][3] = self.builder.get_object('pierce-height').get_value()
        self.toolFileDict[0][4] = self.builder.get_object('pierce-delay').get_value()
        self.toolFileDict[0][5] = self.builder.get_object('puddle-jump-height').get_value()
        self.toolFileDict[0][6] = self.builder.get_object('puddle-jump-delay').get_value()
        self.toolFileDict[0][7] = self.builder.get_object('cut-height').get_value()
        self.toolFileDict[0][8] = self.builder.get_object('cut-feed-rate').get_value()
        self.toolFileDict[0][9] = self.builder.get_object('cut-amps').get_value()
        self.toolFileDict[0][10] = self.builder.get_object('cut-volts').get_value()

    def on_reload_clicked(self,widget,data=None):
        self.toolUpdate = True
        self.load_settings()
        self.toolFileDict = {}
        self.toolKerfMap = {0: 0.0}
        self.get_tools()
        self.toolUpdate = False

    def on_tool_number_value_changed(self,widget):
        tool = int(self.builder.get_object('tool-number').get_value())
        if tool in self.toolKerfMap.keys():
            self.builder.get_object('tool-name').set_text(self.toolFileDict[tool][0])
            self.builder.get_object('kerf-width').set_value(self.toolFileDict[tool][1])
            self.builder.get_object('thc-enable').set_active(self.toolFileDict[tool][2])
            self.builder.get_object('pierce-height').set_value(self.toolFileDict[tool][3])
            self.builder.get_object('pierce-delay').set_value(self.toolFileDict[tool][4])
            self.builder.get_object('puddle-jump-height').set_value(self.toolFileDict[tool][5])
            self.builder.get_object('puddle-jump-delay').set_value(self.toolFileDict[tool][6])
            self.builder.get_object('cut-height').set_value(self.toolFileDict[tool][7])
            self.builder.get_object('cut-feed-rate').set_value(self.toolFileDict[tool][8])
            self.builder.get_object('cut-amps').set_value(self.toolFileDict[tool][9])
            self.builder.get_object('cut-volts').set_value(self.toolFileDict[tool][10])
            hal.set_p('plasmac_run.tool-change-number',str(tool))
        else:
            if tool < self.oldTool:
                self.builder.get_object('tool-number').set_value(self.toolList[self.toolList.index(self.oldTool) - 1])
            else:
                self.builder.get_object('tool-number').set_value(self.toolList[self.toolList.index(self.oldTool) + 1])
        self.oldTool = tool

    def tool_change_number_changed(self,halpin):
        tool = halpin.get()
        if tool in self.toolKerfMap.keys():
            self.builder.get_object('tool-number').set_value(tool)
            hal.set_p('plasmac_run.tool-change-diameter',str(self.toolKerfMap[tool]))
        else:
            hal.set_p('plasmac_run.tool-change-diameter','-2')


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
        self.builder.get_object('tool-number').set_digits(0)
        self.builder.get_object('tool-number-adj').configure(0,0,99999,1,0,0)
        self.builder.get_object('use-auto-volts').set_active(1)
        if self.i.find('TRAJ', 'LINEAR_UNITS').lower() == 'mm':
            self.builder.get_object('kerf-width').set_digits(2)
            self.builder.get_object('kerf-width-adj').configure(0.5,0,5,0.01,0,0)
            self.builder.get_object('cut-feed-rate').set_digits(0)
            self.builder.get_object('cut-feed-rate-adj').configure(4000,0,9999,1,0,0)
            self.builder.get_object('cut-height').set_digits(2)
            self.builder.get_object('cut-height-adj').configure(1,0,25,0.01,0,0)
            self.builder.get_object('pierce-height').set_digits(2)
            self.builder.get_object('pierce-height-adj').configure(4,0,25,0.01,0,0)
        elif self.i.find('TRAJ', 'LINEAR_UNITS').lower() == 'inch':
            self.builder.get_object('kerf-width').set_digits(3)
            self.builder.get_object('kerf-width-adj').configure(0.02,0,0.25,1,0,0)
            self.builder.get_object('cut-feed-rate').set_digits(1)
            self.builder.get_object('cut-feed-rate-adj').configure(160,0,400,0.1,0,0)
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
                if item == 'tool-number' or item == 'kerf-width':
                    self.builder.get_object(item).set_value(0)
                elif isinstance(self.builder.get_object(item), gladevcp.hal_widgets.HAL_SpinButton):
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
                for key in sorted(self.configDict.iterkeys()):
                    if key == 'tool-number' or key == 'kerf-width':
                        pass
                    elif isinstance(self.builder.get_object(key), gladevcp.hal_widgets.HAL_SpinButton):
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
        self.c = linuxcnc.command()
        self.s = linuxcnc.stat()
        self.toolNumberPin = hal_glib.GPin(halcomp.newpin('tool-change-number', hal.HAL_S32, hal.HAL_IN))
        self.toolNumberPin.connect('value-changed', self.tool_change_number_changed)
        self.toolDiameterPin = hal_glib.GPin(halcomp.newpin('tool-change-diameter', hal.HAL_FLOAT, hal.HAL_IN))
        self.thcFeedRate = (float(self.i.find('AXIS_Z', 'MAX_VELOCITY')) * \
                              float(self.i.find('AXIS_Z', 'OFFSET_AV_RATIO'))) * 60
        hal.set_p('plasmac.thc-feed-rate','%f' % (self.thcFeedRate))
        self.configFile = self.i.find('EMC', 'MACHINE').lower() + '_run.cfg'
        self.prefFile = self.i.find('EMC', 'MACHINE') + '.pref'
        self.toolFile = self.i.find('EMC', 'MACHINE').lower() + '_tool.tbl'
        self.toolFileDict = {}
        self.toolKerfMap = {0: 0.0}
        self.toolDict = {}
        self.configDict = {}
        hal.set_p('plasmac.mode','%d' % (int(self.i.find('PLASMAC','MODE') or '0')))
        self.oldMode = 9
        self.oldTool = -1
        self.toolUpdate = False
        self.configure_widgets()
        self.load_settings()
        self.check_tool_file()
        self.get_tools()
        self.set_theme()
        gobject.timeout_add(100, self.periodic)

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
