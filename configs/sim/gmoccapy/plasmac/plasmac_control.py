#!/usr/bin/env python

'''
plasmac_scales.py
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

    def configure_widgets(self):
        pass
        # set_digits = number of digits after decimal
        # configure  = (value, lower limit, upper limit, step size, 0, 0)
        #self.builder.get_object('torchPulseTime').set_digits(1)
        #self.builder.get_object('torchPulseTimeAdj').configure(.5,.1,5,0.1,0,0)

    def periodic(self):
        self.lcnc.stat.poll()
        if self.feed_override != self.lcnc.stat.feedrate:
            self.builder.get_object('feedOverride').set_active(int(self.lcnc.stat.feedrate * 100))
            self.feed_override = int(self.lcnc.stat.feedrate * 100)
        if self.rapid_override != self.lcnc.stat.rapidrate:
            self.builder.get_object('rapidOverride').set_active(int(self.lcnc.stat.rapidrate * 100))
            self.feed_override = int(self.lcnc.stat.rapidrate * 100)
        idle = sp.Popen(['halcmd getp halui.program.is-idle'], stdout=sp.PIPE, shell=True).communicate()[0].strip()
        if idle == 'TRUE':
            self.builder.get_object('pausedMotionSpeedAdj').set_value(0)
        machine = sp.Popen(['halcmd getp halui.machine.is-on'], stdout=sp.PIPE, shell=True).communicate()[0].strip()
        if idle == 'TRUE' and machine == 'TRUE':
            self.builder.get_object('torchPulseStart').set_sensitive(True)
        else:
            self.builder.get_object('torchPulseStart').set_sensitive(False)

        mode = int((sp.Popen(['halcmd getp plasmac.mode'], stdout=sp.PIPE, shell=True)).communicate()[0].strip())
        if mode != self.oldMode:
            if mode == 0:
                self.builder.get_object('heightFrame').show()
            elif mode == 1:
                self.builder.get_object('heightFrame').show()
            elif mode == 2:
                self.builder.get_object('heightFrame').hide()
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

    def on_feedOverride_changed(self, widget):
        tmp1, tmp2 = widget.get_active_text().split()
        speed = float(tmp1) * 0.01
        self.feed_override = speed
        self.lcnc.comd.feedrate(speed)

    def on_rapidOverride_changed(self, widget):
        tmp1, tmp2 = widget.get_active_text().split()
        speed = float(tmp1) * 0.01
        self.rapid_override = speed
        self.lcnc.comd.rapidrate(speed)

    def on_feedDefault_pressed(self, widget):
        self.builder.get_object('feedOverride').set_active(100)

    def on_rapidDefault_pressed(self, widget):
        self.builder.get_object('rapidOverride').set_active(100)

    def on_heightLower_pressed(self, widget):
        self.torch_height -= 0.1
        self.builder.get_object('heightOverride').set_text('%0.1f V' % (self.torch_height))
        sp.Popen(['halcmd setp plasmac.height-override %f' % self.torch_height], shell=True)

    def on_heightRaise_pressed(self, widget):
        self.torch_height += 0.1
        self.builder.get_object('heightOverride').set_text('%0.1f V' % (self.torch_height))
        sp.Popen(['halcmd setp plasmac.height-override %f' % self.torch_height], shell=True)

    def on_heightReset_pressed(self, widget):
        self.torch_height = 0
        self.builder.get_object('heightOverride').set_text('%0.1f V' % (self.torch_height))
        sp.Popen(['halcmd setp plasmac.height-override %f' % self.torch_height], shell=True)

    def on_forward_pressed(self, widget):
        tmp1, tmp2 = self.builder.get_object('pausedMotionSpeed').get_active_text().split()
        speed = float(tmp1) * 0.01
        sp.Popen(['halcmd setp plasmac.paused-motion-speed %f' % speed], shell=True)

    def on_forward_released(self, widget):
        speed = 0
        sp.Popen(['halcmd setp plasmac.paused-motion-speed %f' % speed], shell=True)

    def on_reverse_pressed(self, widget):
        tmp1, tmp2 = self.builder.get_object('pausedMotionSpeed').get_active_text().split()
        speed = float(tmp1) * -0.01
        sp.Popen(['halcmd setp plasmac.paused-motion-speed %f' % speed], shell=True)

    def on_reverse_released(self, widget):
        speed = 0
        sp.Popen(['halcmd setp plasmac.paused-motion-speed %f' % speed], shell=True)

    def configure_comboboxes(self, name, lo, hi, step, default):
        if name == 'torchPulseTime':
            end = 'Sec'
        else:
            end = '%'
        self.myList = []
        for me in range(int(lo/step), int(hi/step) + 1):
            self.myList.append(str(me * step))
            iter = self.builder.get_object(name + 's').append()
            self.builder.get_object(name + 's').set(iter, 0, '%s %s' % (str(me * step), end), 1, me * step)
        self.builder.get_object(name).set_active(self.myList.index(default))
        self.name = self.myList.index(default)

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.lcnc = linuxcncInterface()
        self.prefFile = self.lcnc.linuxcncIniFile.find('EMC', 'MACHINE') + '.pref'
        self.set_theme()
        self.maxFeed = int(float(self.lcnc.linuxcncIniFile.find("DISPLAY", "MAX_FEED_OVERRIDE") or '1') * 100)
        self.maxRapid = int(float(self.lcnc.linuxcncIniFile.find("DISPLAY", "MAX_RAPID_OVERRIDE") or '1') * 100)
        self.oldMode = 9
        self.configure_widgets()
        self.feed_override = 0
        self.rapid_override = 0
        self.torch_height = 0
        self.builder.get_object('heightOverride').set_text('%0.1f V' % (self.torch_height))
        sp.Popen(['halcmd setp plasmac.height-override %f' % self.torch_height], shell=True)
        self.configure_comboboxes('feedOverride', 0, self.maxFeed, 1, '100')
        self.feed_override = 1
        self.configure_comboboxes('rapidOverride', 0, self.maxRapid, 1, '100')
        self.rapid_override = 1
        self.configure_comboboxes('pausedMotionSpeed', 0, 100, 5, '50')
        self.configure_comboboxes('torchPulseTime', 0, 10, 0.1, '1.0')
        gobject.timeout_add(100, self.periodic)


def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
