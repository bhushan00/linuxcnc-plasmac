#!/usr/bin/env python

'''
configurator.py

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

import pygtk
pygtk.require('2.0')
import gtk
import os
import sys
import shutil

class configurator:

    def __init__(self):
        self.W = gtk.Window()
        self.W.set_title('PlasmaC Configurator')
        self.W.connect('delete_event', self.on_window_delete_event)
        self.W.set_position(gtk.WIN_POS_CENTER)
        configureType = self.start_dialog()
        if configureType == 1:
            self.upgrade = True
            if not self.dialog_ok_cancel('Prerequisites',
                                         '\nThis configurator will upgrade an existing plasmac configuration\n'\
                                         'with updated application files.\n\n'\
                                         'Existing machine INI file and HAL file will not be changed\n','Continue','Exit'):
                quit()
        elif configureType == 2:
            self.upgrade = False
            if not self.dialog_ok_cancel('Prerequisites',
                                         '\nBefore using this configurator you should already have a\n'\
                                         'working configuration for the configurator to copy data from.\n\n'\
                                         'If you don\'t have a working configuration then you need\n'\
                                         'to exit the configurator and create one.\n','Continue','Exit'):
                quit()
        else:
            quit()
        self.create_widgets()
        self.iniFile.connect('button_press_event', self.on_inifile_press_event)
        self.create.connect('clicked', self.on_create_clicked)
        self.cancel.connect('clicked', self.on_cancel_clicked)
        self.configPath = os.path.expanduser('~') + '/linuxcnc/configs'
        self.copyPath = os.path.dirname(sys.argv[0])
        self.orgIniFile = ''
        self.newIniPath = ''
        if not self.upgrade:
            self.nameFile.connect_after('focus-out-event', self.on_namefile_focus_out_event)
            self.halFile.connect('button_press_event', self.on_halfile_press_event)
            self.mode0.connect('toggled', self.on_mode0_toggled)
            self.mode1.connect('toggled', self.on_mode1_toggled)
            self.mode2.connect('toggled', self.on_mode2_toggled)
            self.mode = 0
            self.newIniFile = ''
            self.orgHalFile = ''
            self.plasmacIniFile = self.copyPath + '/metric_plasmac.ini'
            self.inPlace = False

    def start_dialog(self):
        dialog = gtk.Dialog('SELECT',
                            self.W,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            ('New',2,
                             'Upgrade',1,
                             'Exit',0))
        label = gtk.Label('Is this a new configuration or an upgrade?')
        dialog.vbox.add(label)
        label.show()
        response = dialog.run()
        dialog.destroy()
        return response

    def dialog_ok_cancel(self,title,text,name1,name2):
        dialog = gtk.Dialog(title,
                            self.W,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (name1, 1,
                            name2, 0)
                           )
        label = gtk.Label(text)
        dialog.vbox.add(label)
        label.show()
        response = dialog.run()
        dialog.destroy()
        return response

    def dialog_ok(self,title,error):
        dialog = gtk.Dialog(title,
                    self.W,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label(error)
        dialog.vbox.add(label)
        label.show()
        response = dialog.run()
        dialog.destroy()
        return response

    def on_window_delete_event(self,window,event):
        gtk.main_quit()

    def on_mode0_toggled(self,button):
        if button.get_active():
            self.mode = 0
            self.modeLabel.set_text('Use arc voltage for both arc-OK and THC')
            self.arcVoltVBox.show()
            self.arcOkVBox.hide()
            self.moveUpVBox.hide()
            self.moveDownVBox.hide()

    def on_mode1_toggled(self,button):
        if button.get_active():
            self.mode = 1
            self.modeLabel.set_text('Use arc ok for arc-OK and arc voltage for both arc-OK and THC')
            self.arcVoltVBox.show()
            self.arcOkVBox.show()
            self.moveUpVBox.hide()
            self.moveDownVBox.hide()

    def on_mode2_toggled(self,button):
        if button.get_active():
            self.mode = 2
            self.modeLabel.set_text('Use arc ok for arc-OK and up/down signals for THC')
            self.arcVoltVBox.hide()
            self.arcOkVBox.show()
            self.moveUpVBox.show()
            self.moveDownVBox.show()

    def on_namefile_focus_out_event(self,widget,event):
        self.configName = self.nameFile.get_text().replace(' ','_')
        self.newIniFile = '%s/%s/%s.ini' %(self.configPath,self.configName,self.configName)
        self.newIniPath = os.path.dirname(self.newIniFile)

    def on_inifile_press_event(self,button,event):
        self.dlg = gtk.FileChooserDialog('Open..', None, gtk.FILE_CHOOSER_ACTION_OPEN,
          (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        if not self.upgrade and os.path.dirname(self.halFile.get_text()):
            self.dlg.set_current_folder(os.path.dirname(self.halFile.get_text()))
        else:
            self.dlg.set_current_folder(self.configPath)
        response = self.dlg.run()
        if response == gtk.RESPONSE_OK:
            self.iniFile.set_text(self.dlg.get_filename())
            self.orgIniFile = self.dlg.get_filename()
        else:
            self.iniFile.set_text('')
            self.orgIniFile = ''
        self.dlg.destroy()

    def on_halfile_press_event(self,button,event):
        self.dlg = gtk.FileChooserDialog('Save..', None, gtk.FILE_CHOOSER_ACTION_OPEN,
          (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        if os.path.dirname(self.iniFile.get_text()):
            self.dlg.set_current_folder(os.path.dirname(self.iniFile.get_text()))
        else:
            self.dlg.set_current_folder(self.configPath)
        response = self.dlg.run()
        if response == gtk.RESPONSE_OK:
            self.halFile.set_text(self.dlg.get_filename())
            self.orgHalFile = self.dlg.get_filename()
        else:
            self.halFile.set_text('')
            self.orgHalFile = ''
        self.dlg.destroy()


    def on_cancel_clicked(self,button):
        gtk.main_quit()

    def on_create_clicked(self,button):
        if self.upgrade:
            if not self.iniFile.get_text():
                self.dialog_ok('ERROR','INI file is required')
                return
        else:
            if not self.nameFile.get_text():
                self.dialog_ok('ERROR','Machine name is required')
                return
            if not self.iniFile.get_text():
                self.dialog_ok('ERROR','INI file is required')
                return
            if not self.halFile.get_text():
                self.dialog_ok('ERROR','HAL file is required')
                return
            if self.mode == 0 or self.mode == 1:
                if not self.arcVoltPin.get_text():
                    self.dialog_ok('ERROR','Arc voltage is required for Mode %d' %(self.mode))
                    return
            if self.mode == 1 or self.mode == 2:
                if not self.arcOkPin.get_text():
                    self.dialog_ok('ERROR','Arc OK is required for Mode %d' %(self.mode))
                    return
            if not self.ohmicInPin.get_text() and not self.floatPin.get_text():
                self.dialog_ok('ERROR','At least one of ohmic probe or float switch is required')
                return
            if self.ohmicInPin.get_text() and not self.ohmicOutPin.get_text():
                self.dialog_ok('ERROR','Ohmic enable is required if ohmic probe is specified')
                return
            if not self.torchPin.get_text():
                self.dialog_ok('ERROR','Torch on is required')
                return
            if self.mode == 2:
                if not self.moveUpPin.get_text():
                    self.dialog_ok('ERROR','Move up is required for Mode %d' %(self.mode))
                    return
                if not self.moveDownPin.get_text():
                    self.dialog_ok('ERROR','Move down is required for Mode %d' %(self.mode))
                    return
        # test if path exists
        if not self.upgrade:
            if not os.path.exists(self.newIniPath):
                os.makedirs(self.newIniPath)
            else:
                if not self.dialog_ok_cancel('CONFIGURATION EXISTS',\
                                             '\nA configuration already exists in %s\n'\
                                             %(self.newIniPath),'Overwrite','Back'):
#                                             '\nOK to overwrite existing config\n'\
#                                             '\nBack to return to entry window'\
                    return
        # copy plasmac application files to configuration directory
        for copyFile in self.get_files_to_copy():
            if self.upgrade:
                shutil.copy('%s/%s' %(self.copyPath,copyFile), '%s' %(os.path.dirname(self.orgIniFile)))
            else:
                shutil.copy('%s/%s' %(self.copyPath,copyFile), '%s' %(self.newIniPath))
        # make new plasmac.hal without redundancies
        inFile = open('%s/plasmac.hal' %(self.copyPath),'r')
        if self.upgrade:
            outFile = open('%s/plasmac.hal' %(os.path.dirname(self.orgIniFile)),'w')
        else:
            outFile = open('%s/plasmac.hal' %(self.newIniPath),'w')
        for line in inFile:
            if line.startswith('#************'):
                break
            else:
                outFile.write(line)
        outFile.close()
        inFile.close()
        if self.upgrade:
            self.dialog_ok('SUCCESS','\nUpgrade is complete.\n')
            return
        # copy original INI and HAL files for input and backup
        self.readIniFile = self.newIniPath + '/_original.' + os.path.basename(self.orgIniFile)
        self.readHalFile = self.newIniPath + '/_original.' + os.path.basename(self.orgHalFile)
        shutil.copy('%s' %(self.orgIniFile), '%s' %(self.readIniFile))
        shutil.copy('%s' %(self.orgHalFile), '%s' %(self.readHalFile))
        # get some info from [TRAJ] section of INI file copy
        inIni = open(self.readIniFile,'r')
        while 1:
            line = inIni.readline()
            if '[TRAJ]' in line:
                break
            if not line:
                self.dialog_ok('ERROR','Cannot find [TRAJ] section in INI file')
                return
        result = 0
        while 1:
            line = inIni.readline()
            if 'LINEAR_UNITS' in line:
                result += 1
                a,b = line.strip().replace(' ','').split('=')
                if b.lower() == 'mm':
                    self.plasmacIniFile =  self.copyPath + '/metric_plasmac.ini'
                else:
                    self.plasmacIniFile =  self.copyPath + '/imperial_plasmac.ini'
            elif 'COORDINATES' in line:
                result += 10
                a,b = line.strip().replace(' ','').split('=')
                self.zJoint = b.lower().index('z')
                self.numJoints = len(b.strip())
            if line.startswith('[') or not line:
                if result == 11:
                    break
                else:
                    if result == 1:
                        self.dialog_ok('ERROR','Could not find COORDINATES in [TRAJ] section of INI file')
                    else:
                        self.dialog_ok('ERROR','Could not find LINEAR_UNITS in [TRAJ] section of INI file')
                    return
        inIni.close()
        # get some info from [JOINT_n] section of INI file copy
        inIni = open(self.orgIniFile,'r')
        self.zVel = self.zAcc = 0
        while 1:
            line = inIni.readline()
            if '[JOINT_%d]' %(self.zJoint) in line:
                break
            if not line:
                self.dialog_ok('ERROR','Cannot find [JOINT_%s] section in INI file' %(self.zJoint))
                break
        result = 0
        while 1:
            line = inIni.readline()
            if 'MAX_VELOCITY' in line:
                result += 1
                a,b = line.strip().replace(' ','').split('=')
                self.zVel = b
            elif 'MAX_ACCELERATION' in line:
                result += 10
                a,b = line.strip().replace(' ','').split('=')
                self.zAcc = b
            if line.startswith('[') or not line:
                if result == 11:
                    break
                else:
                    if result == 1:
                        self.dialog_ok('ERROR','Could not find MAX_ACCELERATION in [JOINT_%d] section of INI file' %(self.zJoint))
                    else:
                        self.dialog_ok('ERROR','Could not find MAX_VELOCITY in [JOINT_%d] section of INI file' %(self.zJoint))
                    return
        inIni.close()
        #write new hal file with spindle.0.on commented out
        newHalFile = open('%s/%s.hal' %(self.newIniPath,self.configName),'w')
        inHal = open(self.readHalFile,'r')
        for line in inHal:
            if 'spindle.0.on' in line:
                newHalFile.write('# ' + line)
            else:
                newHalFile.write(line)
        newHalFile.close()
        inHal.close()
        # write a connections.hal file for plasmac connections to the machine
        with open('%s/%s/%s_connections.hal' %(self.configPath,self.configName,self.configName), 'w') as f_out:
            f_out.write('# Keep your plasmac i/o connections here to prevent them from\n'\
                        '# being overwritten by updates or pncconf/stepconf changes\n\n'\
                        '# Other customisations may be placed here as well\n\n'\
                        '# the next line needs to be the joint associated with the Z axis\n')
            f_out.write('net plasmac:axis-position joint.%d.pos-fb => plasmac.axis-z-position\n' %(self.zJoint))
            if self.arcVoltPin.get_text() and (self.mode == 0 or self.mode == 1):
                f_out.write('net plasmac:arc-voltage-in %s => plasmac.arc-voltage-in\n' %(self.arcVoltPin.get_text()))
            if self.arcOkPin.get_text() and (self.mode == 1 or self.mode == 2):
                f_out.write('net plasmac:arc-ok-in %s => plasmac.arc-ok-in\n' %(self.arcOkPin.get_text()))
            if self.floatPin.get_text():
                f_out.write('net plasmac:float-switch %s => debounce.0.0.in\n' %(self.floatPin.get_text()))
            elif not self.floatPin.get_text():
                f_out.write('# net plasmac:float-switch {YOUR FLOAT SWITCH PIN} => debounce.0.0.in\n')
            if self.breakPin.get_text():
                f_out.write('net plasmac:breakaway %s => debounce.0.1.in\n' %(self.breakPin.get_text()))
            elif not self.breakPin.get_text():
                f_out.write('# net plasmac:breakaway {YOUR BREAKAWAY PIN} => debounce.0.1.in\n')
            if self.ohmicInPin.get_text():
                f_out.write('net plasmac:ohmic-probe %s => debounce.0.2.in\n' %(self.ohmicInPin.get_text()))
            elif not self.ohmicInPin.get_text():
                f_out.write('# net plasmac:ohmic-probe {YOUR OHMIC PROBE PIN} => debounce.0.2.in\n')
            if self.ohmicOutPin.get_text():
                f_out.write('net plasmac:ohmic-enable plasmac.ohmic-enable  => %s\n' %(self.ohmicOutPin.get_text()))
            elif not self.ohmicOutPin.get_text():
                f_out.write('# net plasmac:ohmic-enable plasmac.ohmic-enable  => {YOUR OHMIC ENABLE PIN}\n')
            if self.torchPin.get_text():
                f_out.write('net plasmac:torch-on => %s\n' %(self.torchPin.get_text()))
            if self.moveUpPin.get_text() and self.mode == 2:
                f_out.write('net plasmac:move-up %s => plasmac.move-up\n' %(self.moveUpPin.get_text()))
            if self.moveDownPin.get_text() and self.mode == 2:
                f_out.write('net plasmac:move-down %s => plasmac.move-down\n' %(self.moveDownPin.get_text()))
        # create a postgui.hal file if not already present
        if not os.path.exists('%s/%s/postgui.hal' %(self.configPath,self.configName)):
            with open('%s/%s/postgui.hal' %(self.configPath,self.configName), 'w') as f_out:
                f_out.write('# Keep your post GUI customisations here to prevent them from\n'\
                            '# being overwritten by updates or pncconf/stepconf changes\n\n')
        # create a new INI file from the INI file copy and the plasmac INI file
        plasmacIni = open(self.plasmacIniFile,'r')
        outIni = open(self.newIniFile,'w')
        while 1:
            line = plasmacIni.readline()
            if line.startswith('# see notes'):
                pass
            elif line.startswith('[APPLICATIONS]') or \
                 line.startswith('DELAY') or \
                 line.startswith('APP'):
                outIni.write('# ' + line)
            elif not '[HAL]' in line:
                if line.startswith('MODE'):
                    outIni.write('MODE = %s\n' %(self.mode))
                else:
                    outIni.write(line)
            else:
                break
        # add the [HAL] section
        outIni.write('[HAL]\n'\
                     '# required\n'
                     'TWOPASS = ON\n'\
                     '# the base machine\n'\
                     'HALFILE = %s.hal\n'\
                     '# the plasmac machine conections\n'\
                     'HALFILE = %s_connections.hal\n'\
                     '# the plasmac component connections\n'\
                     'HALFILE = plasmac.hal\n'\
                     '# use this for customisation after GUI has loaded\n'\
                     'POSTGUI_HALFILE = postgui.hal\n'\
                     '# required\n'\
                     'HALUI = halui\n'\
                     '\n' %(self.configName,self.configName))
        # add the tabs to the display section
        inIni = open(self.readIniFile, 'r')
        while 1:        
            line = inIni.readline()
            if '[DISPLAY]' in line:
                outIni.write(line)
                break
        while 1:
            line = inIni.readline()
            if not line.startswith('['):
                outIni.write(line)
            else:
                inIni.close()
                break
        while 1:        
            line = plasmacIni.readline()
            if line.startswith('EMBED'):
                outIni.write('# required\n' + line)
                break
        while 1:
            line = plasmacIni.readline()
            if not line.startswith('['):
                outIni.write(line)
            else:
                break
        inIni.close()
        plasmacIni.close()
        done = ['[APPLICATIONS]',\
                '[PLASMAC]',\
                '[FILTER]',\
                '[RS274NGC]',\
                '[HAL]',\
                '[DISPLAY]']
        # iterate through INI file copy to get all missing sections
        inIni = open(self.readIniFile, 'r')
        validSection = True
        offsetAxis = False
        newName = False
        while 1:
            line = inIni.readline()
            if line.startswith('['):
                if line.strip() in done:
                    validSection = False
                else:
                    done.append(line.strip())
                    validSection = True
                if line.strip() == '[EMC]' and validSection:
                    newName = True
                elif line.strip() == '[AXIS_Z]' and validSection:
                    offsetAxis = True
                else:
                    newName = False
                    offsetAxis = False
            if validSection:
                if newName:
                    if line.startswith('MACHINE'):
                        outIni.write('MACHINE = %s\n' %(self.configName))
                    else:
                        outIni.write(line)
                elif offsetAxis:
                    if line.startswith('MAX_VELOCITY'):
                        outIni.write('# set to double the value in the corresponding joint\n'\
                                     'MAX_VELOCITY = %s\n' %(float(self.zVel) * 2))
                    elif line.startswith('MAX_ACCELERATION'):
                        outIni.write('# set to double the value in the corresponding joint\n'\
                                     'MAX_ACCELERATION = %s\n'\
                                     '# shares the above two equally between the joint and the offset\n'\
                                     'OFFSET_AV_RATIO = 0.5\n' %(float(self.zAcc) * 2))
                    else:
                        outIni.write(line)
                else:
                    outIni.write(line)
            if not line:
                break
        outIni.close()
        inIni.close()
        self.dialog_ok('SUCCESS',\
                       '\nConfiguration is complete.\n\n'\
                       'You can run this configuration from a console with:\n\n'\
                       'Full installation:\n'\
                       'linuxcnc  '\
                       '/home/\'USERNAME\'/linuxcnc/configs/{0}/{0}.ini\n\n'\
                       'Run In Place installation:\n'\
                       '/home/\'USERNAME\'/\'GIT REPO\'/scripts/linuxcnc  '\
                       '/home/\'USERNAME\'/linuxcnc/configs/{0}/{0}.ini\n'.format(self.configName))

    def create_widgets(self):
        self.VB = gtk.VBox()
        if not self.upgrade:
            self.modeVBox = gtk.VBox()
            self.modeHBox = gtk.HBox(homogeneous=True)
            self.mode0 = gtk.RadioButton(group=None, label='Mode: 0')
            self.modeHBox.pack_start(self.mode0)
            self.mode1 = gtk.RadioButton(group=self.mode0, label='Mode: 1')
            self.modeHBox.pack_start(self.mode1)
            self.mode2 = gtk.RadioButton(group=self.mode0, label='Mode: 2')
            self.modeHBox.pack_start(self.mode2)
            self.modeLabel = gtk.Label('Use arc voltage for both arc-OK and THC')
            self.modeLabel.set_alignment(0,0)
            modeBlank = gtk.Label('')
            self.modeVBox.pack_start(self.modeHBox)
            self.modeVBox.pack_start(self.modeLabel)
            self.modeVBox.pack_start(modeBlank)
            self.VB.pack_start(self.modeVBox,expand=False)
            self.nameVBox = gtk.VBox()
            nameLabel = gtk.Label('Machine Name:')
            nameLabel.set_alignment(0,0)
            self.nameFile = gtk.Entry()
            self.nameFile.set_width_chars(60)
            nameBlank = gtk.Label('')
            self.nameVBox.pack_start(nameLabel)
            self.nameVBox.pack_start(self.nameFile)
            self.nameVBox.pack_start(nameBlank)
            self.VB.pack_start(self.nameVBox,expand=False)
        self.iniVBox = gtk.VBox()
        if self.upgrade:
            self.iniLabel = gtk.Label('INI file of configuration to upgrade:')
        else:
            self.iniLabel = gtk.Label('INI file in existing working config:')
        self.iniLabel.set_alignment(0,0)
        self.iniFile = gtk.Entry()
        self.iniFile.set_width_chars(60)
        self.iniBlank = gtk.Label('')
        self.iniVBox.pack_start(self.iniLabel)
        self.iniVBox.pack_start(self.iniFile)
        self.iniVBox.pack_start(self.iniBlank)
        self.VB.pack_start(self.iniVBox,expand=False)
        if not self.upgrade:
            self.halVBox = gtk.VBox()
            halLabel = gtk.Label('HAL file in existing working config:')
            halLabel.set_alignment(0,0)
            self.halFile = gtk.Entry()
            self.halFile.set_width_chars(60)
            halBlank = gtk.Label('')
            self.halVBox.pack_start(halLabel)
            self.halVBox.pack_start(self.halFile)
            self.halVBox.pack_start(halBlank)
            self.VB.pack_start(self.halVBox,expand=False)
            self.arcVoltVBox = gtk.VBox()
            self.arcVoltLabel = gtk.Label('Arc Voltage HAL pin:')
            self.arcVoltLabel.set_alignment(0,0)
            self.arcVoltPin = gtk.Entry()
            self.arcVoltPin.set_width_chars(60)
            arcVoltBlank = gtk.Label('')
            self.arcVoltVBox.pack_start(self.arcVoltLabel)
            self.arcVoltVBox.pack_start(self.arcVoltPin)
            self.arcVoltVBox.pack_start(arcVoltBlank)
            self.VB.pack_start(self.arcVoltVBox,expand=False)
            self.arcOkVBox = gtk.VBox()
            self.arcOkLabel = gtk.Label('Arc OK HAL pin:')
            self.arcOkLabel.set_alignment(0,0)
            self.arcOkPin = gtk.Entry()
            self.arcOkPin.set_width_chars(60)
            arcOkBlank = gtk.Label('')
            self.arcOkVBox.pack_start(self.arcOkLabel)
            self.arcOkVBox.pack_start(self.arcOkPin)
            self.arcOkVBox.pack_start(arcOkBlank)
            self.VB.pack_start(self.arcOkVBox,expand=False)
            self.ohmicInVBox = gtk.VBox()
            ohmicInLabel = gtk.Label('Ohmic Probe HAL pin (optional):')
            ohmicInLabel.set_alignment(0,0)
            self.ohmicInPin = gtk.Entry()
            self.ohmicInPin.set_width_chars(60)
            ohmicInBlank = gtk.Label('')
            self.ohmicInVBox.pack_start(ohmicInLabel)
            self.ohmicInVBox.pack_start(self.ohmicInPin)
            self.ohmicInVBox.pack_start(ohmicInBlank)
            self.VB.pack_start(self.ohmicInVBox,expand=False)
            self.ohmicOutVBox = gtk.VBox()
            ohmicOutLabel = gtk.Label('Ohmic Probe Enable HAL pin (optional):')
            ohmicOutLabel.set_alignment(0,0)
            self.ohmicOutPin = gtk.Entry()
            self.ohmicOutPin.set_width_chars(60)
            ohmicOutBlank = gtk.Label('')
            self.ohmicOutVBox.pack_start(ohmicOutLabel)
            self.ohmicOutVBox.pack_start(self.ohmicOutPin)
            self.ohmicOutVBox.pack_start(ohmicOutBlank)
            self.VB.pack_start(self.ohmicOutVBox,expand=False)
            self.floatVBox = gtk.VBox()
            floatLabel = gtk.Label('Float Switch HAL pin (optional):')
            floatLabel.set_alignment(0,0)
            self.floatPin = gtk.Entry()
            self.floatPin.set_width_chars(60)
            floatBlank = gtk.Label('')
            self.floatVBox.pack_start(floatLabel)
            self.floatVBox.pack_start(self.floatPin)
            self.floatVBox.pack_start(floatBlank)
            self.VB.pack_start(self.floatVBox,expand=False)
            self.breakVBox = gtk.VBox()
            breakLabel = gtk.Label('Breakaway Switch HAL pin (optional):')
            breakLabel.set_alignment(0,0)
            self.breakPin = gtk.Entry()
            self.breakPin.set_width_chars(60)
            breakBlank = gtk.Label('')
            self.breakVBox.pack_start(breakLabel)
            self.breakVBox.pack_start(self.breakPin)
            self.breakVBox.pack_start(breakBlank)
            self.VB.pack_start(self.breakVBox,expand=False)
            self.torchVBox = gtk.VBox()
            torchLabel = gtk.Label('Torch On HAL pin:')
            torchLabel.set_alignment(0,0)
            self.torchPin = gtk.Entry()
            self.torchPin.set_width_chars(60)
            torchBlank = gtk.Label('')
            self.torchVBox.pack_start(torchLabel)
            self.torchVBox.pack_start(self.torchPin)
            self.torchVBox.pack_start(torchBlank)
            self.VB.pack_start(self.torchVBox,expand=False)
            self.moveUpVBox = gtk.VBox()
            self.moveUpLabel = gtk.Label('Move Up HAL pin:')
            self.moveUpLabel.set_alignment(0,0)
            self.moveUpPin = gtk.Entry()
            self.moveUpPin.set_width_chars(60)
            moveUpBlank = gtk.Label('')
            self.moveUpVBox.pack_start(self.moveUpLabel)
            self.moveUpVBox.pack_start(self.moveUpPin)
            self.moveUpVBox.pack_start(moveUpBlank)
            self.VB.pack_start(self.moveUpVBox,expand=False)
            self.moveDownVBox = gtk.VBox()
            self.moveDownLabel = gtk.Label('Move Down HAL pin:')
            self.moveDownLabel.set_alignment(0,0)
            self.moveDownPin = gtk.Entry()
            self.moveDownPin.set_width_chars(60)
            moveDownBlank = gtk.Label('')
            self.moveDownVBox.pack_start(self.moveDownLabel)
            self.moveDownVBox.pack_start(self.moveDownPin)
            self.moveDownVBox.pack_start(moveDownBlank)
            self.VB.pack_start(self.moveDownVBox,expand=False)
        BB = gtk.HButtonBox()
        if self.upgrade:
            self.create = gtk.Button('Upgrade')
        else:
            self.create = gtk.Button('Create')
        self.cancel = gtk.Button('Exit')
        BB.pack_start(self.create, True, True, 0)
        BB.pack_start(self.cancel, True, True, 0)
        BB.set_border_width(5)
        self.VB.pack_start(BB,expand=False)
        self.W.add(self.VB)
        self.W.show_all()
        if not self.upgrade:
            self.modeLabel.set_text('Use arc voltage for both arc-OK and THC')
            self.arcVoltVBox.show()
            self.arcOkVBox.hide()
            self.moveUpVBox.hide()
            self.moveDownVBox.hide()
        else:
            self.W.set_title('PlasmaC Upgrader')

    def get_files_to_copy(self):
        return ['imperial_startup.ngc',\
                'M190',\
                'materialverter.py',\
                'metric_startup.ngc',\
                'plasmac_buttons.glade',\
                'plasmac_buttons.hal',\
                'plasmac_buttons.py',\
                'plasmac_config.glade',\
                'plasmac_config.hal',\
                'plasmac_config.py',\
                'plasmac_control.glade',\
                'plasmac_control.hal',\
                'plasmac_control.py',\
                'plasmac_gcode.py',\
                'plasmac_monitor.glade',\
                'plasmac_monitor.hal',\
                'plasmac_monitor.py',\
                'plasmac_run.glade',\
                'plasmac_run.hal',\
                'plasmac_run.py',\
                'plasmac_stats.glade',\
                'plasmac_stats.hal',\
                'plasmac_stats.py',\
                'README.md',\
                'tool.tbl'\
                ]

if __name__ == '__main__':
    try:
        a = configurator()
        gtk.main()
    except KeyboardInterrupt:
        pass
