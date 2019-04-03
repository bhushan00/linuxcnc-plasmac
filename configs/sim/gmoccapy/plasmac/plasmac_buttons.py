#!/usr/bin/env python

'''
plasmac_buttons.py
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
import hal
import gladevcp
from subprocess import Popen,PIPE

class HandlerClass:

    def wait_for_completion(self):
        while self.lcnc.comd.wait_complete() == -1:
            pass

    def on_user_button_1_clicked(self,event):
        self.user_button_action(self.iniButtonCode[1])

    def on_user_button_2_clicked(self,event):
        self.user_button_action(self.iniButtonCode[2])

    def on_user_button_3_clicked(self,event):
        self.user_button_action(self.iniButtonCode[3])

    def user_button_action(self, commands):
        if not commands: return
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

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.i = linuxcnc.ini(os.environ['INI_FILE_NAME'])
        self.s = linuxcnc.stat();
        self.c = linuxcnc.command()
        self.prefFile = self.i.find('EMC', 'MACHINE') + '.pref'
        self.iniButtonName = ['Names']
        self.iniButtonCode = ['Codes']
        for button in range(1,4):
            bname = self.i.find('PLASMAC', 'BUTTON_' + str(button) + '_NAME') or '0'
            self.iniButtonName.append(bname)
            self.iniButtonCode.append(self.i.find('PLASMAC', 'BUTTON_' + str(button) + '_CODE'))
            if bname != '0':
                bname = bname.split('\\')
                if len(bname) > 1:
                    blabel = bname[0] + '\n' + bname[1]
                else:
                    blabel = bname[0]
                self.builder.get_object('user-button-' + str(button)).set_label(blabel)
                self.builder.get_object('user-button-' + str(button)).children()[0].set_justify(gtk.JUSTIFY_CENTER)
        self.set_theme()

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
