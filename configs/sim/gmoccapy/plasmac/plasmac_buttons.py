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
import subprocess as sp
import gtk
import linuxcnc
import gobject
import gladevcp

class linuxcncInterface(object):

    def __init__(self):
        self.linuxcncIniFile = linuxcnc.ini(os.environ['INI_FILE_NAME'])
        self.stat = linuxcnc.stat();
        self.comd = linuxcnc.command()

class HandlerClass:

    def wait_for_completion(self):
        while self.lcnc.comd.wait_complete() == -1:
            pass

    def on_xToHome_pressed(self,event):
        print 'XXXXXX'
        self.goto_home('X')

    def on_yToHome_pressed(self,event):
        self.goto_home('Y')

    def on_zToHome_pressed(self,event):
        self.goto_home('Z')

    def goto_home(self,axis):
        idle = sp.Popen(['halcmd getp halui.program.is-idle'], stdout=sp.PIPE, shell=True).communicate()[0].strip()
        print 'IDLE =',idle
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
        self.lcnc = linuxcncInterface()
        self.prefFile = self.lcnc.linuxcncIniFile.find('EMC', 'MACHINE') + '.pref'
        self.set_theme()

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
