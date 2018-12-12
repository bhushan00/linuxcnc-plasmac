#!/usr/bin/env python

'''
plasmac_panel.py
Copyright (C) 2018  Phillip A Carter

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
import subprocess as sp
import gtk
import linuxcnc
import gobject
import hal
from   gladevcp.persistence import widget_defaults,select_widgets
import gladevcp

#debug = 0

class linuxcncInterface(object):

    def send_command(self,command, wait=True):
        if self.s.interp_state == linuxcnc.INTERP_IDLE:
            if self.s.task_mode != linuxcnc.MODE_MDI:
                self.c.mode(linuxcnc.MODE_MDI)
                self.c.wait_complete()
            self.c.mdi(command)
            if wait:
                self.c.wait_complete()

    def __init__(self):
        self.linuxcncIniFile = linuxcnc.ini(os.environ['INI_FILE_NAME'])
        self.stat = linuxcnc.stat();
        self.comd = linuxcnc.command()

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
        p_height = self.builder.get_object('pierceHeight').get_value()
        p_delay = self.builder.get_object('pierceDelay').get_value()
        pj_height = self.builder.get_object('puddleJumpHeight').get_value()
        pj_delay = self.builder.get_object('puddleJumpDelay').get_value()
        c_height = self.builder.get_object('cutHeight').get_value()
        c_speed = self.builder.get_object('cutFeedRate').get_value()
        c_amps = self.builder.get_object('cutAmps').get_value()
        c_volts = self.builder.get_object('cutVolts').get_value()
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
        self.materialsList[0][1] = self.builder.get_object('pierceHeight').get_value()
        self.materialsList[0][2] = self.builder.get_object('pierceDelay').get_value()
        self.materialsList[0][3] = self.builder.get_object('puddleJumpHeight').get_value()
        self.materialsList[0][4] = self.builder.get_object('puddleJumpDelay').get_value()
        self.materialsList[0][5] = self.builder.get_object('cutHeight').get_value()
        self.materialsList[0][6] = self.builder.get_object('cutFeedRate').get_value()
        self.materialsList[0][7] = self.builder.get_object('cutAmps').get_value()
        self.materialsList[0][8] = self.builder.get_object('cutVolts').get_value()
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
            self.builder.get_object('pierceHeight').set_value(self.materialsList[material][1])
            self.builder.get_object('pierceDelay').set_value(self.materialsList[material][2])
            self.builder.get_object('puddleJumpHeight').set_value(self.materialsList[material][3])
            self.builder.get_object('puddleJumpDelay').set_value(self.materialsList[material][4])
            self.builder.get_object('cutHeight').set_value(self.materialsList[material][5])
            self.builder.get_object('cutFeedRate').set_value(self.materialsList[material][6])
            self.builder.get_object('cutAmps').set_value(self.materialsList[material][7])
            self.builder.get_object('cutVolts').set_value(self.materialsList[material][8])

    def wait_for_completion(self):
        while self.lcnc.comd.wait_complete() == -1:
            pass

    def on_xToHome_clicked(self,event):
        self.goto_home('X')

    def on_yToHome_clicked(self,event):
        self.goto_home('Y')

    def on_zToHome_clicked(self,event):
        self.goto_home('Z')

    def goto_home(self,axis):
        idle = sp.Popen(['halcmd getp halui.program.is-idle'], stdout=sp.PIPE, shell=True).communicate()[0].strip()
        if idle == 'TRUE':
            home = self.lcnc.linuxcncIniFile.find('JOINT_' + str(self.lcnc.linuxcncIniFile.find('TRAJ', 'COORDINATES').upper().index(axis)), 'HOME')
            mode = sp.Popen(['halcmd getp halui.mode.is-mdi'], stdout=sp.PIPE, shell=True).communicate()[0].strip()
            if mode == 'FALSE':
                self.lcnc.comd.mode(linuxcnc.MODE_MDI)
                self.wait_for_completion()
            self.lcnc.comd.mdi('G53 G0 ' + axis + home)
            self.wait_for_completion()
            if mode == 'FALSE':
                self.lcnc.comd.mode(linuxcnc.MODE_MANUAL)
                self.wait_for_completion()

    def on_setupFeedRate_value_changed(self, widget):
        self.builder.get_object('probeFeedRateAdj').configure(self.builder.get_object('probeFeedRate').get_value(),0,self.builder.get_object('setupFeedRate').get_value(),1,0,0)
        
    def configure_widgets(self):
        # set_digits = number of digits after decimal
        # configure  = (value, lower limit, upper limit, step size, 0, 0)
        self.builder.get_object('arcFailDelay').set_digits(1)
        self.builder.get_object('arcFailDelayAdj').configure(1,0.1,60,0.1,0,0)
        self.builder.get_object('arcOkLow').set_digits(1)
        self.builder.get_object('arcOkLowAdj').configure(0,0,200,0.5,0,0)
        self.builder.get_object('arcOkHigh').set_digits(1)
        self.builder.get_object('arcOkHighAdj').configure(0,0,200,0.5,0,0)
        self.builder.get_object('arcMaxStarts').set_digits(0)
        self.builder.get_object('arcMaxStartsAdj').configure(3,1,9,1,0,0)
        self.builder.get_object('arcRestartDelay').set_digits(0)
        self.builder.get_object('arcRestartDelayAdj').configure(1,1,60,1,0,0)
        self.builder.get_object('arcVoltageOffset').set_digits(1)
        self.builder.get_object('arcVoltageOffsetAdj').configure(0,-100,100,0.1,0,0)
        self.builder.get_object('arcVoltageScale').set_digits(2)
        self.builder.get_object('arcVoltageScaleAdj').configure(1,0.01,99,0.01,0,0)
        self.builder.get_object('cornerlockEnable').set_active(1)
        self.builder.get_object('cornerlockThreshold').set_digits(0)
        self.builder.get_object('cornerlockThresholdAdj').configure(90,1,99,1,0,0)
        self.builder.get_object('cutAmps').set_digits(0)
        self.builder.get_object('cutAmpsAdj').configure(45,0,999,1,0,0)
        self.builder.get_object('cutVolts').set_digits(1)
        self.builder.get_object('cutVoltsAdj').configure(122,50,300,0.1,0,0)
        self.builder.get_object('kerfCrossEnable').set_active(1)
        self.builder.get_object('kerfCrossThreshold').set_digits(1)
        self.builder.get_object('kerfCrossThresholdAdj').configure(3,1,10,0.1,0,0)
        self.builder.get_object('maxOffsetVelocityIn').set_label(str(int(self.thcFeedRate)))
        self.builder.get_object('pidPGain').set_digits(0)
        self.builder.get_object('pidPGainAdj').configure(25,0,1000,1,0,0)
        self.builder.get_object('pidIGain').set_digits(0)
        self.builder.get_object('pidIGainAdj').configure(0,0,1000,1,0,0)
        self.builder.get_object('pidDGain').set_digits(0)
        self.builder.get_object('pidDGainAdj').configure(0,0,1000,1,0,0)
        self.builder.get_object('pierceDelay').set_digits(1)
        self.builder.get_object('pierceDelayAdj').configure(0.5,0,10,0.1,0,0)
        self.builder.get_object('puddleJumpHeight').set_digits(0)
        self.builder.get_object('puddleJumpHeightAdj').configure(0,0,200,1,0,0)
        self.builder.get_object('puddleJumpDelay').set_digits(2)
        self.builder.get_object('puddleJumpDelayAdj').configure(0,0,9,0.01,0,0)
        self.builder.get_object('thcEnable').set_active(1)
        self.builder.get_object('thcThreshold').set_digits(2)
        self.builder.get_object('thcThresholdAdj').configure(1,0.05,9,0.01,0,0)
        self.builder.get_object('torchOffDelay').set_digits(1)
        self.builder.get_object('torchOffDelayAdj').configure(0,0,9,0.1,0,0)
        self.builder.get_object('useAutoVolts').set_active(1)
        if self.lcnc.linuxcncIniFile.find('TRAJ', 'LINEAR_UNITS').lower() == 'mm':
            self.builder.get_object('cutFeedRate').set_digits(0)
            self.builder.get_object('cutFeedRateAdj').configure(4000,50,9999,1,0,0)
            self.builder.get_object('cutHeight').set_digits(1)
            self.builder.get_object('cutHeightAdj').configure(1,0,25.4,0.1,0,0)
            self.builder.get_object('floatSwitchTravel').set_digits(2)
            self.builder.get_object('floatSwitchTravelAdj').configure(1.5,0,9,0.01,0,0)
            self.builder.get_object('pierceHeight').set_digits(1)
            self.builder.get_object('pierceHeightAdj').configure(4,0,25.4,0.1,0,0)
            self.builder.get_object('probeFeedRate').set_digits(0)
            self.builder.get_object('probeFeedRateAdj').configure(1000,1,self.thcFeedRate,1,0,0)
            self.builder.get_object('safeHeight').set_digits(0)
            self.builder.get_object('safeHeightAdj').configure(20,1,99,1,0,0)
            self.builder.get_object('setupFeedRate').set_digits(0)
            self.builder.get_object('setupFeedRateAdj').configure(int(self.thcFeedRate * 0.8),1,self.thcFeedRate,1,0,0)
            self.builder.get_object('skipIhsDistance').set_digits(0)
            self.builder.get_object('skipIhsDistanceAdj').configure(0,0,999,1,0,0)
        elif self.lcnc.linuxcncIniFile.find('TRAJ', 'LINEAR_UNITS').lower() == 'inch':
            self.builder.get_object('cutFeedRate').set_digits(1)
            self.builder.get_object('cutFeedRateAdj').configure(160,2,400,0.1,0,0)
            self.builder.get_object('cutHeight').set_digits(2)
            self.builder.get_object('cutHeightAdj').configure(0.04,0,1,0.01,0,0)
            self.builder.get_object('floatSwitchTravel').set_digits(3)
            self.builder.get_object('floatSwitchTravelAdj').configure(0.06,0,1,0.001,0,0)
            self.builder.get_object('pierceHeight').set_digits(2)
            self.builder.get_object('pierceHeightAdj').configure(0.16,0,1,0.01,0,0)
            self.builder.get_object('probeFeedRate').set_digits(1)
            self.builder.get_object('probeFeedRateAdj').configure(40,.1,self.thcFeedRate,.1,0,0)
            self.builder.get_object('safeHeight').set_digits(2)
            self.builder.get_object('safeHeightAdj').configure(0.75,0.04,4,0.01,0,0)
            self.builder.get_object('setupFeedRate').set_digits(1)
            self.builder.get_object('setupFeedRateAdj').configure(int(self.thcFeedRate * 0.8),.1,self.thcFeedRate,.1,0,0)
            self.builder.get_object('skipIhsDistance').set_digits(1)
            self.builder.get_object('skipIhsDistanceAdj').configure(0,0,99,.1,0,0)
        else:
            print '*** incorrect [TRAJ]LINEAR_UNITS in ini file'

    def mode_check(self):
        mode = int((sp.Popen(['halcmd getp plasmac.mode'], stdout=sp.PIPE, shell=True)).communicate()[0].strip())
        units = float(sp.Popen(['halcmd getp halui.machine.units-per-mm'], stdout=sp.PIPE, shell=True).communicate()[0].strip())
        maxPidP = self.thcFeedRate / units * 0.1
        if mode != self.oldMode:
            if mode == 0:
                self.builder.get_object('arcOkHigh').show()
                self.builder.get_object('arcOkHighLabel').set_text('OK High Volts')
                self.builder.get_object('arcOkLow').show()
                self.builder.get_object('arcOkLowLabel').set_text('OK Low Volts')
                self.builder.get_object('arcVoltage').show()
                self.builder.get_object('arcVoltageLabel').set_text('Arc Voltage')
                self.builder.get_object('arcVoltageScale').show()
                self.builder.get_object('arcVoltageScaleLabel').set_text('Voltage Scale')
                self.builder.get_object('arcVoltageOffset').show()
                self.builder.get_object('arcVoltageOffsetLabel').set_text('Voltage Offset')
                self.builder.get_object('autoBox').show()
                self.builder.get_object('heightFrame').show()
                self.builder.get_object('kerfBox').show()
                self.builder.get_object('kerfLabel').show()
                self.builder.get_object('kerfFrame').set_shadow_type(gtk.SHADOW_OUT)
                self.builder.get_object('pidPGainAdj').configure(self.builder.get_object('pidPGainAdj').get_value(),1,maxPidP,1,0,0)
                self.builder.get_object('pidPLabel').set_text('Speed (PID P)')
                self.builder.get_object('pidIGain').show()
                self.builder.get_object('pidILabel').set_text('PID I GAIN')
                self.builder.get_object('pidDGain').show()
                self.builder.get_object('pidDLabel').set_text('PID D GAIN')
                self.builder.get_object('thresholdBox').show()
                self.builder.get_object('voltsBox').show()
            elif mode == 1:
                self.builder.get_object('arcOkHigh').hide()
                self.builder.get_object('arcOkHighLabel').set_text('')
                self.builder.get_object('arcOkLow').hide()
                self.builder.get_object('arcOkLowLabel').set_text('')
                self.builder.get_object('arcVoltage').show()
                self.builder.get_object('arcVoltageLabel').set_text('Arc Voltage')
                self.builder.get_object('arcVoltageScale').show()
                self.builder.get_object('arcVoltageScaleLabel').set_text('Voltage Scale')
                self.builder.get_object('arcVoltageOffset').show()
                self.builder.get_object('arcVoltageOffsetLabel').set_text('Voltage Offset')
                self.builder.get_object('autoBox').show()
                self.builder.get_object('heightFrame').show()
                self.builder.get_object('kerfBox').show()
                self.builder.get_object('kerfLabel').show()
                self.builder.get_object('kerfFrame').set_shadow_type(gtk.SHADOW_OUT)
                self.builder.get_object('pidPGainAdj').configure(self.builder.get_object('pidPGainAdj').get_value(),1,maxPidP,1,0,0)
                self.builder.get_object('pidPLabel').set_text('Speed (PID P)')
                self.builder.get_object('pidIGain').show()
                self.builder.get_object('pidILabel').set_text('PID I GAIN')
                self.builder.get_object('pidDGain').show()
                self.builder.get_object('pidDLabel').set_text('PID D GAIN')
                self.builder.get_object('thresholdBox').show()
                self.builder.get_object('voltsBox').show()
            elif mode == 2:
                self.builder.get_object('arcOkHigh').hide()
                self.builder.get_object('arcOkHighLabel').set_text('')
                self.builder.get_object('arcOkLow').hide()
                self.builder.get_object('arcOkLowLabel').set_text('')
                self.builder.get_object('arcVoltage').hide()
                self.builder.get_object('arcVoltageLabel').set_text('')
                self.builder.get_object('arcVoltageScale').hide()
                self.builder.get_object('arcVoltageScaleLabel').set_text('')
                self.builder.get_object('arcVoltageOffset').hide()
                self.builder.get_object('arcVoltageOffsetLabel').set_text('')
                self.builder.get_object('autoBox').hide()
                self.builder.get_object('heightFrame').hide()
                self.builder.get_object('kerfBox').hide()
                self.builder.get_object('kerfLabel').hide()
                self.builder.get_object('kerfFrame').set_shadow_type(gtk.SHADOW_NONE)
                self.builder.get_object('pidPGainAdj').configure(self.builder.get_object('pidPGainAdj').get_value(),1,100,1,0,0)
                self.builder.get_object('pidPLabel').set_text('Speed (%)')
                self.builder.get_object('pidIGain').hide()
                self.builder.get_object('pidILabel').set_text('')
                self.builder.get_object('pidDGain').hide()
                self.builder.get_object('pidDLabel').set_text('')
                self.builder.get_object('thresholdBox').hide()
                self.builder.get_object('voltsBox').hide()
            else:
                pass
            self.oldMode = mode
        return True

    def load_settings(self):
        for item in widget_defaults(select_widgets(self.builder.get_objects(), hal_only=False,output_only = True)):
            if item != 'heightOverride':
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
                                (key, value) = line.strip().replace(" ", "").split('=')
                                if value == 'True':value = True
                                if value == 'False':value = False
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
                        self.builder.get_object(item).set_active(self.configDict.get(item))
                    else:
                        self.builder.get_object(item).set_active(False)
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
                for key in self.configDict:
                    if isinstance(self.builder.get_object(key), gladevcp.hal_widgets.HAL_SpinButton):
                        value = self.builder.get_object(key).get_value()
                    elif isinstance(self.builder.get_object(key), gladevcp.hal_widgets.HAL_CheckButton):
                        value = self.builder.get_object(key).get_active()
                    f_out.write(key + '=' + str(value) + '\n')
        except:
            print '*** error opening', self.configFile

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.lcnc = linuxcncInterface()
# disable reverse run button until reverse run is merged into master #####
        self.builder.get_object('reverseRun').set_sensitive(False)
        gtk.settings_get_default().set_property('gtk-theme-name', self.lcnc.linuxcncIniFile.find('PLASMAC', 'THEME'))
        font = self.lcnc.linuxcncIniFile.find('PLASMAC', 'FONT') or 'sans 10'
        gtk.settings_get_default().set_property('gtk-font-name', font)
        configEnable = self.lcnc.linuxcncIniFile.find('PLASMAC', 'CONFIG_ENABLE') or '1'
        sp.Popen(['halcmd setp gladevcp.configEnable ' + configEnable], shell=True)
        self.thcFeedRate = (float(self.lcnc.linuxcncIniFile.find('AXIS_Z', 'MAX_VELOCITY')) * \
                              float(self.lcnc.linuxcncIniFile.find('AXIS_Z', 'OFFSET_AV_RATIO'))) * 60
        sp.Popen('halcmd setp plasmac.thc-feed-rate %f' % self.thcFeedRate, shell=True)
        self.configFile = self.lcnc.linuxcncIniFile.find('PLASMAC', 'CONFIG_FILE') or \
                            self.lcnc.linuxcncIniFile.find('EMC', 'MACHINE').lower() + '.cfg'
        self.materialsFile = self.lcnc.linuxcncIniFile.find('PLASMAC', 'MATERIAL_FILE') or self.lcnc.linuxcncIniFile.find('EMC', 'MACHINE').lower() + '.mat'
        self.materialsList = []
        self.configDict = {}
        self.oldMode = 9
        self.materialsUpdate = False
        self.configure_widgets()
        self.builder.get_object('probeFeedRateAdj').set_upper(self.builder.get_object('setupFeedRate').get_value())
        self.load_settings()
        self.check_materials_file()
        self.get_materials()
        gobject.timeout_add(100, self.mode_check)

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
