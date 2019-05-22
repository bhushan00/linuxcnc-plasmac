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
            if not self.dialog_ok_cancel(\
                    'Prerequisites',
                    '\nThis configurator will upgrade an existing plasmac configuration\n'\
                    'with updated application files.\n\n'\
                    'Existing machine INI file and HAL file will not be changed\n',
                    'Continue','Exit'):
                quit()
        elif configureType == 2:
            self.upgrade = False
            if not self.dialog_ok_cancel(
                    'Prerequisites',
                    '\nBefore using this configurator you should already have a\n'\
                    'working configuration for the configurator to copy data from.\n\n'\
                    'If you don\'t have a working configuration then you need\n'\
                    'to exit the configurator and create one.\n',
                    'Continue','Exit'):
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
        self.machineName = self.nameFile.get_text().replace(' ','_')
        self.newIniPath = '{0}/{1}'.format(self.configPath,self.machineName.lower())
        self.newIniFile = '{0}/{1}.ini'.format(self.newIniPath,self.machineName.lower())

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
        if self.upgrade:
            self.machineName = os.path.basename(self.dlg.get_filename()).split('.')[0]
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
        if not self.check_entries(): return
        display = self.get_display()
        if display == None: return
        if not self.check_new_path(): return
        if self.upgrade:
            version = self.check_version()
            if not version:
                self.upgrade_connections_hal()
                self.upgrade_plasmac_hal()
                self.upgrade_ini_file()
            if not self.copy_files(): return
            self.dialog_ok('SUCCESS','\nUpgrade is complete.\n')
            return
        else:
            if not self.create_plasmac_hal_file(): return
        if not self.copy_ini_and_hal_files(): return
        if not self.get_traj_info(self.readIniFile,display): return
        if not self.get_joint_info(self.readIniFile): return
        if not self.write_new_hal_file(): return
        if not self.write_connections_hal_file(): return
        if not self.write_postgui_hal_file(): return
        if not self.write_newini_file(): return
        if not self.copy_files(display): return
        self.print_success()

    def check_entries(self):
        # check if entries are valid
        if self.upgrade:
            if not self.iniFile.get_text():
                self.dialog_ok('ERROR','INI file is required')
                return False
        else:
            if not self.nameFile.get_text():
                self.dialog_ok('ERROR','Machine name is required')
                return False
            if not self.iniFile.get_text():
                self.dialog_ok('ERROR','INI file is required')
                return False
            if not self.halFile.get_text():
                self.dialog_ok('ERROR','HAL file is required')
                return False
            if self.mode == 0 or self.mode == 1:
                if not self.arcVoltPin.get_text():
                    self.dialog_ok('ERROR','Arc voltage is required for Mode {:d}'.format(self.mode))
                    return False
            if self.mode == 1 or self.mode == 2:
                if not self.arcOkPin.get_text():
                    self.dialog_ok('ERROR','Arc OK is required for Mode {:d}'.format(self.mode))
                    return False
            if not self.ohmicInPin.get_text() and not self.floatPin.get_text():
                self.dialog_ok('ERROR','At least one of ohmic probe or float switch is required')
                return False
            if self.ohmicInPin.get_text() and not self.ohmicOutPin.get_text():
                self.dialog_ok('ERROR','Ohmic enable is required if ohmic probe is specified')
                return False
            if not self.torchPin.get_text():
                self.dialog_ok('ERROR','Torch on is required')
                return False
            if self.mode == 2:
                if not self.moveUpPin.get_text():
                    self.dialog_ok('ERROR','Move up is required for Mode {:d}'.format(self.mode))
                    return False
                if not self.moveDownPin.get_text():
                    self.dialog_ok('ERROR','Move down is required for Mode {:d}'.format(self.mode))
                    return False
        return True

    def get_display(self):
        # get the display GUI
        inFile = open('{0}'.format(self.orgIniFile), 'r')
        while 1:
            line = inFile.readline()
            print '1',line
            if line.startswith('[DISPLAY]'):
                break
            if not line:
                inFile.close()
                self.dialog_ok('ERROR','Cannot find [DISPLAY] section in INI file')
                return None
        while 1:
            print '2',line
            line = inFile.readline()
            if line.startswith('DISPLAY'):
                if 'axis' in line.lower():
                    inFile.close()
                    return 'axis'
                elif 'gmoccapy' in line.lower():
                    inFile.close()
                    return 'gmoccapy'
                else:
                    inFile.close()
                    self.dialog_ok('ERROR','Cannot find a valid display in INI file')
                    return None
            elif line.startswith('[') or not line:
                inFile.close()
                self.dialog_ok('ERROR','Cannot find \"DISPLAY =\" in INI file')
                return None

    def check_new_path(self):
        # test if path exists
        if not self.upgrade:
            if not os.path.exists(self.newIniPath):
                os.makedirs(self.newIniPath)
            else:
                if not self.dialog_ok_cancel('CONFIGURATION EXISTS',\
                                             '\nA configuration already exists in {0}\n'\
                                             .format(self.newIniPath),'Overwrite','Back'):
                    return False
        return True

    def copy_files(self,display):
        # copy plasmac application files to configuration directory
        for copyFile in self.get_files_to_copy(display):
            if self.upgrade:
                shutil.copy('{0}/{1}'.format(self.copyPath,copyFile), os.path.dirname(self.orgIniFile))
            else:
                shutil.copy('{0}/{1}'.format(self.copyPath,copyFile), self.newIniPath)
        return True

    def check_version(self):
        # see if this was a version before using {MACHINE}_connections.hal
        if os.path.exists('{0}/{1}_connections.hal'.format(os.path.dirname(self.orgIniFile),self.machineName.lower())):
            return 1
        else:
            return 0

    def upgrade_connections_hal(self):
        # create a {MACHINE}_connections.hal for an upgrade
        inFile = open('{0}/plasmac.hal'.format(os.path.dirname(self.orgIniFile)), 'r')
        outFile = open('{0}/{1}_connections.hal'.format(os.path.dirname(self.orgIniFile),self.machineName.lower()), 'w')
        outFile.write(\
            '# Keep your plasmac i/o connections here to prevent them from\n'\
            '# being overwritten by updates or pncconf/stepconf changes\n\n'\
            '# Other customisations may be placed here as well\n\n')
        for line in inFile:
            if ' '.join(line.split()).startswith('loadrt debounce'):
                outFile.write(\
                    '#***** DEBOUNCE FOR THE FLOAT SWITCH *****\n'\
                    '# the lower the delay here the better\n'\
                    + line)
            elif ' '.join(line.split()).startswith('setp debounce.0.delay'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('addf debounce.0'):
                outFile.write(line + '\n')
            elif ' '.join(line.split()).startswith('net plasmac:axis-position '):
                outFile.write(\
                    '# the next line needs to be the joint associated with the Z axis\n'\
                     + line + '\n')
            elif ' '.join(line.split()).startswith('net plasmac:arc-voltage-in '):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:arc-ok-in '):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:float-switch '):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:breakaway '):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:ohmic-probe '):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:ohmic-enable '):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:torch-on ') and not 'plasmac.torch-on' in line:
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:move-down '):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:move-up '):
                outFile.write(line)
        inFile.close()
        outFile.close()

    def upgrade_plasmac_hal(self):
        # create a plasmac.hal for an upgrade
        shutil.copy('{0}/plasmac.hal'.format(os.path.dirname(self.orgIniFile)),\
                    '{0}/plasmac.hal.old'.format(os.path.dirname(self.orgIniFile)))
        inFile = open('{0}/plasmac.hal.old'.format(os.path.dirname(self.orgIniFile)), 'r')
        outFile = open('{0}/plasmac.hal'.format(os.path.dirname(self.orgIniFile)), 'w')
        outFile.write(\
            '# do not change the contents of this file as it will be overwiten by updates\n'\
            '# make custom changes in {0}_connections.hal\n\n'\
            .format(self.machineName.lower()))
        for line in inFile:
            if ' '.join(line.split()).startswith('net plasmac:axis-x-position'):
                outFile.write('#inputs\n' + line)
            elif ' '.join(line.split()).startswith('net plasmac:axis-y-position'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:breakaway-switch-out'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:current-velocity'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:feed-override'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:float-switch-out'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:offset-current'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:ohmic-probe-out'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:program.is-idle'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:program.is-paused'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:program.is-running'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:spindle-is-on'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:units-per-mm'):
                outFile.write(line + '\n')
            elif ' '.join(line.split()).startswith('net plasmac:adaptive-feed'):
                outFile.write('#outputs\n' + line)
            elif ' '.join(line.split()).startswith('net plasmac:feed-hold'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:offset-counts'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:offset-enable'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:offset-scale'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:program-pause'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:program-resume'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:program-run'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:program-stop'):
                outFile.write(line)
            elif ' '.join(line.split()).startswith('net plasmac:torch-on') and 'plasmac.torch-on' in line:
                outFile.write(line)
        inFile.close()
        outFile.close()

    def upgrade_ini_file(self):
        # create a new ini file for an upgrade
        shutil.copy(self.orgIniFile,'{0}.old'.format(self.orgIniFile))
        inFile = open('{0}.old'.format(self.orgIniFile), 'r')
        outFile = open('{0}'.format(self.orgIniFile), 'w')
        for line in inFile:
            if ' '.join(line.strip().split()) == 'HALFILE = plasmac.hal':
                outFile.write(\
                    'HALFILE = plasmac.hal\n'\
                    '# the plasmac machine connections\n'\
                    'HALFILE = {0}_connections.hal\n'\
                    .format(self.machineName.lower()))
            else:
                outFile.write(line)
        inFile.close()
        outFile.close()

    def create_plasmac_hal_file(self):
        # make new plasmac.hal without redundancies
        inFile = open('{0}/plasmac.hal'.format(self.copyPath),'r')
        if self.upgrade:
            outFile = open('{0}/plasmac.hal'.format(os.path.dirname(self.orgIniFile)),'w')
        else:
            outFile = open('{0}/plasmac.hal'.format(self.newIniPath),'w')
        for line in inFile:
            if line.startswith('# make custom'):
                outFile.write('# make custom changes in {0}_connections.hal\n'.format(self.machineName.lower()))
            elif line.startswith('# see comment'):
                pass
            elif line.startswith('#************') and line.strip().endswith('************#'):
                break
            else:
                outFile.write(line)
        outFile.close()
        inFile.close()
        return True

    def copy_ini_and_hal_files(self):
        # copy original INI and HAL files for input and backup
        if os.path.dirname(self.orgIniFile) == self.newIniPath and \
           os.path.basename(self.orgIniFile).startswith('_original_'):
            self.readIniFile = self.orgIniFile
        else:
            self.readIniFile = '{0}/_original_{1}'.format(self.newIniPath,os.path.basename(self.orgIniFile))
            shutil.copy(self.orgIniFile,self.readIniFile)

        if os.path.dirname(self.orgHalFile) == self.newIniPath and \
           os.path.basename(self.orgHalFile).startswith('_original_'):
            self.readHalFile = self.orgHalFile
        else:
            self.readHalFile = '{0}/_original_{1}'.format(self.newIniPath,os.path.basename(self.orgHalFile))
            shutil.copy(self.orgHalFile,self.readHalFile)
        return True

    def get_traj_info(self,readFile,display):
        # get some info from [TRAJ] section of INI file copy
        inIni = open(readFile,'r')
        while 1:
            line = inIni.readline()
            if '[TRAJ]' in line:
                break
            if not line:
                inIni.close()
                self.dialog_ok('ERROR','Cannot find [TRAJ] section in INI file')
                return False
        result = 0
        while 1:
            line = inIni.readline()
            if 'LINEAR_UNITS' in line:
                result += 1
                a,b = line.strip().replace(' ','').split('=')
                if b.lower() == 'mm':
                    self.plasmacIniFile = '{0}/{1}/metric_plasmac.ini'.format(self.copyPath,display)
                else:
                    self.plasmacIniFile = '{0}/{1}/imperial_plasmac.ini'.format(self.copyPath,display)
            elif 'COORDINATES' in line:
                result += 10
                a,b = line.strip().replace(' ','').split('=')
                self.zJoint = b.lower().index('z')
                self.numJoints = len(b.strip())
            if line.startswith('[') or not line:
                if result == 11:
                    break
                else:
                    inIni.close()
                    if result == 1:
                        self.dialog_ok('ERROR','Could not find COORDINATES in [TRAJ] section of INI file')
                    else:
                        self.dialog_ok('ERROR','Could not find LINEAR_UNITS in [TRAJ] section of INI file')
                    return False
        inIni.close()
        return True

    def get_joint_info(self,readFile):
        # get some info from [JOINT_n] section of INI file copy
        inIni = open(readFile,'r')
        self.zVel = self.zAcc = 0
        while 1:
            line = inIni.readline()
            if '[JOINT_{:d}]'.format(self.zJoint) in line:
                break
            if not line:
                inIni.close()
                self.dialog_ok('ERROR','Cannot find [JOINT_{d}] section in INI file'.format(self.zJoint))
                return False
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
                    inIni.close()
                    if result == 1:
                        self.dialog_ok('ERROR','Could not find MAX_ACCELERATION in [JOINT_{:d}] section of INI file'.format(self.zJoint))
                    else:
                        self.dialog_ok('ERROR','Could not find MAX_VELOCITY in [JOINT_{:d}] section of INI file'.format(self.zJoint))
                    return False
        inIni.close()
        return True

    def write_new_hal_file(self):
        #write new hal file with spindle.0.on commented out
        newHalFile = open('{0}/{1}.hal'.format(self.newIniPath,self.machineName.lower()),'w')
        inHal = open(self.readHalFile,'r')
        for line in inHal:
            if 'spindle.0.on' in line:
                newHalFile.write('# ' + line)
            else:
                newHalFile.write(line)
        newHalFile.close()
        inHal.close()
        return True

    def write_connections_hal_file(self):
        # write a connections.hal file for plasmac connections to the machine
        with open('{0}/{1}_connections.hal'.format(self.newIniPath,self.machineName.lower()), 'w') as f_out:
            f_out.write(\
                '# Keep your plasmac i/o connections here to prevent them from\n'\
                '# being overwritten by updates or pncconf/stepconf changes\n\n'\
                '# Other customisations may be placed here as well\n\n'\
                '#***** debounce for the float switch *****\n'\
                '# the lower the delay here the better\n'\
                'loadrt  debounce                cfg=3\n'\
                'setp    debounce.0.delay        5\n'\
                'addf    debounce.0              servo-thread\n\n'\
                '# the next line needs to be the joint associated with the Z axis\n')
            f_out.write('net plasmac:axis-position joint.{:d}.pos-fb => plasmac.axis-z-position\n'.format(self.zJoint))
            if self.arcVoltPin.get_text() and (self.mode == 0 or self.mode == 1):
                f_out.write('net plasmac:arc-voltage-in {0} => plasmac.arc-voltage-in\n'.format(self.arcVoltPin.get_text()))
            if self.arcOkPin.get_text() and (self.mode == 1 or self.mode == 2):
                f_out.write('net plasmac:arc-ok-in {0} => plasmac.arc-ok-in\n'.format(self.arcOkPin.get_text()))
            if self.floatPin.get_text():
                f_out.write('net plasmac:float-switch {0} => debounce.0.0.in\n'.format(self.floatPin.get_text()))
            elif not self.floatPin.get_text():
                f_out.write('# net plasmac:float-switch {YOUR FLOAT SWITCH PIN} => debounce.0.0.in\n')
            if self.breakPin.get_text():
                f_out.write('net plasmac:breakaway {0} => debounce.0.1.in\n'.format(self.breakPin.get_text()))
            elif not self.breakPin.get_text():
                f_out.write('# net plasmac:breakaway {YOUR BREAKAWAY PIN} => debounce.0.1.in\n')
            if self.ohmicInPin.get_text():
                f_out.write('net plasmac:ohmic-probe {0} => debounce.0.2.in\n'.format(self.ohmicInPin.get_text()))
            elif not self.ohmicInPin.get_text():
                f_out.write('# net plasmac:ohmic-probe {YOUR OHMIC PROBE PIN} => debounce.0.2.in\n')
            if self.ohmicOutPin.get_text():
                f_out.write('net plasmac:ohmic-enable plasmac.ohmic-enable  => {0}\n'.format(self.ohmicOutPin.get_text()))
            elif not self.ohmicOutPin.get_text():
                f_out.write('# net plasmac:ohmic-enable plasmac.ohmic-enable  => {YOUR OHMIC ENABLE PIN}\n')
            if self.torchPin.get_text():
                f_out.write('net plasmac:torch-on => {0}\n'.format(self.torchPin.get_text()))
            if self.moveUpPin.get_text() and self.mode == 2:
                f_out.write('net plasmac:move-up {0} => plasmac.move-up\n'.format(self.moveUpPin.get_text()))
            if self.moveDownPin.get_text() and self.mode == 2:
                f_out.write('net plasmac:move-down {0} => plasmac.move-down\n'.format(self.moveDownPin.get_text()))
        return True

    def write_postgui_hal_file(self):
        # create a postgui.hal file if not already present
        if not os.path.exists('{0}/postgui.hal'.format(self.newIniPath)):
            with open('{0}/postgui.hal'.format(self.newIniPath), 'w') as f_out:
                f_out.write(\
                    '# Keep your post GUI customisations here to prevent them from\n'\
                    '# being overwritten by updates or pncconf/stepconf changes\n\n')
        return True

    def write_newini_file(self):
        # create a new INI file from the INI file copy and the plasmac INI file
        plasmacIni = open(self.plasmacIniFile,'r')
        outIni = open(self.newIniFile,'w')
        # comment out the test panel
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
                    outIni.write('MODE = {0}\n'.format(self.mode))
                else:
                    outIni.write(line)
            else:
                break
        # add the [HAL] section
        outIni.write(\
            '[HAL]\n'\
            '# required\n'
            'TWOPASS = ON\n'\
            '# the base machine\n'\
            'HALFILE = {0}.hal\n'\
            '# the plasmac component connections\n'\
            'HALFILE = plasmac.hal\n'\
            '# the plasmac machine connections\n'\
            'HALFILE = {0}_connections.hal\n'\
            '# use this for customisation after GUI has loaded\n'\
            'POSTGUI_HALFILE = postgui.hal\n'\
            '# required\n'\
            'HALUI = halui\n'\
            '\n'\
            .format(self.machineName.lower()))
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
                        outIni.write('MACHINE = {0}\n'.format(self.machineName))
                    else:
                        outIni.write(line)
                elif offsetAxis:
                    if line.startswith('MAX_VELOCITY'):
                        outIni.write(
                            '# set to double the value in the corresponding joint\n'\
                            'MAX_VELOCITY = {0}\n'\
                            .format(float(self.zVel) * 2))
                    elif line.startswith('MAX_ACCELERATION'):
                        outIni.write(\
                            '# set to double the value in the corresponding joint\n'\
                            'MAX_ACCELERATION = {0}\n'\
                            '# shares the above two equally between the joint and the offset\n'\
                            'OFFSET_AV_RATIO = 0.5\n'\
                            .format(float(self.zAcc) * 2))
                    else:
                        outIni.write(line)
                else:
                    outIni.write(line)
            if not line:
                break
        outIni.close()
        inIni.close()
        return True

    def print_success(self):
        self.dialog_ok(\
            'SUCCESS',\
            '\nConfiguration is complete.\n\n'\
            'You can run this configuration from a console as follows.\n\n'\
            'Full installation:\n'\
            'linuxcnc  '\
            '/home/{1}/linuxcnc/configs/{0}/{0}.ini\n\n'\
            'Run In Place installation:\n'\
            '/home/{1}/{2}/scripts/linuxcnc  '\
            '/home/{1}/linuxcnc/configs/{0}/{0}.ini\n'\
            .format(self.machineName.lower(),'{USER}','{GIT_REPO}'))

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
            self.nameFile.set_tooltip_markup(\
                'The <b>name</b> of the new or existing machine.\n'\
                'If not existing, this creates a directory ~/linuxcnc/configs/<b>name</b>.\n'\
                '<b>name</b>.ini and <b>name</b>.hal are then written to this directory '\
                'and all other required files are copied to it.\n'\
                '<b>name</b> is converted to lowercase and spaces are converted to underscores.')
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

    def get_files_to_copy(self,display):
        if display == 'axis':
            return ['imperial_startup.ngc',\
                    'M190',\
                    'materialverter.py',\
                    'metric_startup.ngc',\
                    'plasmac_axis.py',\
                    'plasmac_config.glade',\
                    'plasmac_config.hal',\
                    'plasmac_config.py',\
                    'plasmac_gcode.py',\
                    'plasmac_run.glade',\
                    'plasmac_run.hal',\
                    'plasmac_run.py',\
                    'plasmac_stats.glade',\
                    'plasmac_stats.hal',\
                    'plasmac_stats.py',\
                    'README.md',\
                    'tool.tbl'\
                    ]
        elif display == 'gmoccapy':
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
        else:
            return None

if __name__ == '__main__':
    try:
        a = configurator()
        gtk.main()
    except KeyboardInterrupt:
        pass
