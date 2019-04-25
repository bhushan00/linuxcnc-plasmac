#!/usr/bin/env python

'''
plasmac_monitor.py
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
import hal_glib
from gladevcp.persistence import IniFile
from gladevcp.persistence import widget_defaults
from gladevcp.persistence import select_widgets
from gmoccapy import getiniinfo
#from gmoccapy import preferences

class HandlerClass:

    def periodic(self):
        #mode = hal.get_value('plasmac.mode')
        #if mode != self.oldMode:
            #if mode == 0:
                #self.builder.get_object('arc-voltage').show()
                #self.builder.get_object('arc-voltage-label').show()
            #elif mode == 1:
                #self.builder.get_object('arc-voltage').show()
                #self.builder.get_object('arc-voltage-label').show()
            #elif mode == 2:
                #self.builder.get_object('arc-voltage').hide()
                #self.builder.get_object('arc-voltage-label').hide()
            #else:
                #pass
            #self.oldMode = mode
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

    def state_changed(self,halpin):
        if halpin.get() != self.CUTTING and self.oldState == self.CUTTING:
            print 'STATE:',halpin.get()
#        if halpin.get() == self.FINISH:
            self.CUT_DISTANCE = self.CUT_DISTANCE + hal.get_value('plasmac.cut-length')
            self.CUT_TIME = self.CUT_TIME + hal.get_value('plasmac.cut-time')
            m, s = divmod(self.CUT_TIME, 60)
            h, m = divmod(m, 60)
            print 'STATE:',halpin.get(),',   DIST:',self.CUT_DISTANCE,'TIME: %d:%02d:%02d' %(h,m,s)
            self.builder.get_object('cut-distance').set_label('%0.2f' %(self.CUT_DISTANCE))
            self.builder.get_object('cut-time').set_label('%d:%02d:%02d' %(h,m,s))
        self.oldState = halpin.get()

    def pierce_count_changed(self,halpin):
        if hal.get_value('plasmac_stats.state') >= self.TORCH_ON:
            self.PIERCE_COUNT += 1
            self.builder.get_object('pierce-count').set_label('%d' %(self.PIERCE_COUNT))

    def on_stats_box_destroy(self, obj, data = None):
        print 'BOX SAVE STATE'
        self.ini.save_state(self)

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.i = linuxcnc.ini(os.environ['INI_FILE_NAME'])
        self.prefFile = self.i.find('EMC', 'MACHINE') + '.pref'
        self.set_theme()

        self.plasmacStatePin = hal_glib.GPin(halcomp.newpin('state', hal.HAL_S32, hal.HAL_IN))
        self.plasmacPierceCount = hal_glib.GPin(halcomp.newpin('pierce-count', hal.HAL_S32, hal.HAL_IN))
        self.plasmacStatePin.connect('value-changed', self.state_changed)
        self.plasmacPierceCount.connect('value-changed', self.pierce_count_changed)

        self.oldState = 0
        self.cutDistance = 0
        # plasmac states
        self.IDLE          =  0
        self.PROBE_HEIGHT  =  1
        self.PROBE_DOWN    =  2
        self.PROBE_UP      =  3
        self.ZERO_HEIGHT   =  4
        self.PIERCE_HEIGHT =  5
        self.TORCH_ON      =  6
        self.ARC_OK        =  7
        self.PIERCE_DELAY  =  8
        self.PUDDLE_JUMP   =  9
        self.CUT_HEGHT     = 10
        self.CUTTING       = 11
        self.SAFE_HEIGHT   = 12
        self.MAX_HEIGHT    = 13
        self.FINISH        = 14
        self.TORCH_PULSE   = 15
        self.PAUSED_MOTION = 16
        self.OHMIC_TEST    = 17
        self.PROBE_TEST    = 18
        self.defaults = { IniFile.vars : { 
                                           "PIERCE_COUNT" : 0,
                                           "CUT_TIME"     : 0.0,
                                           "CUT_DISTANCE" : 0.0,
                                           "RAPID_TIME"   : 0,
                                           "PROBE_TIME"   : 0,
                                         },
                        }
        get_ini_info = getiniinfo.GetIniInfo()
        self.ini_filename = __name__ + ".var"
        self.ini = IniFile(self.ini_filename, self.defaults, self.builder)
        self.ini.restore_state(self)
        m, s = divmod(self.CUT_TIME, 60)
        h, m = divmod(m, 60)
        self.builder.get_object('cut-distance').set_label('%0.2f' %(self.CUT_DISTANCE))
        self.builder.get_object('cut-time').set_label('%d:%02d:%02d' %(h,m,s))


        gobject.timeout_add(100, self.periodic)

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
