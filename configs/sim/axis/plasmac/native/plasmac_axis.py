'''
plasmac_axis.py
Copyright (C) 2018 2019  Phillip A Carter

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


w = root_window.tk.call

################################################################################
# set the window size
# change pad_width and pad_height to suit your setup
# then uncomment the next 11 lines

pad_width=0
pad_height=0
#maxgeo=w('wm','maxsize','.')
#if type(maxgeo) == tuple:
#    fullsize=str(maxgeo[0]),str(maxgeo[1])
#else:
#    fullsize=maxgeo.split(' ')[0],maxgeo.split(' ')[1]
#width=str(int(fullsize[0])-pad_width)
#height=str(int(fullsize[1])-pad_height)
#x=str(pad_width/2)
#y=str(pad_height/2)
#print '\nAxis window is', width, 'x', height, 'and starts at', x, 'x', y, '\n'
#w('wm','geometry','.',width + 'x' + height + '+' + x + '+' + y)



################################################################################
# disable the 'do you want to close' dialog

w('wm','protocol','.','WM_DELETE_WINDOW','destroy .')



################################################################################
# set the default font, gcode font and help balloons

font = inifile.find("PLASMAC","FONT") or 'sans 10'
fname, fsize = font.split()
w('font','configure','TkDefaultFont','-family', fname, '-size', fsize)
w('.pane.bottom.t.text','configure','-height','10','-font', font, '-foreground','blue')
w('DynamicHelp::configure','-borderwidth','5','-topbackground','yellow','-bg','yellow')



################################################################################
# change dro screen

w('.pane.top.right.fnumbers.text','configure','-foreground','green','-background','black')



################################################################################
# widget setup

# some names to save fingers
ftop = '.pane.top'
ftabs = ftop + '.tabs'
fmanual = ftabs + '.fmanual'
faxes = fmanual + '.axes'
fjoints = fmanual + '.joints'
fjogf = fmanual + '.jogf'
ftorch = fmanual + '.torch'
foverride = fmanual + '.override'
fpausedmotion = fmanual + '.pausedmotion'
fmdi = ftabs + '.fmdi'
ft = '.pane.bottom.t'
fcommon = '.pane.bottom.t.common'
fmonitor = '.pane.bottom.t.common.monitor'
fbuttons = '.pane.bottom.t.common.buttons'
frun = '.plasmac.frun'
fconfig = '.plasmac.fconfig'
fmaterial = '.plasmac.frun.material'
fcutparms = '.plasmac.frun.cutparms'
fthc = '.plasmac.frun.thc'
flocks = '.plasmac.frun.locks'
fmotion = '.plasmac.fconfig.motion'
farc = '.plasmac.fconfig.arc'
foffsets = '.plasmac.fconfig.offsets'
fsettings ='.plasmac.fconfig.settings'
fcornerlock = '.plasmac.frun.locks.cornerlock'
fkerflock = '.plasmac.frun.locks.kerflock'

# redo the text in tabs so they resize for the new default font
w(ftop + '.tabs','configure','-arcradius','2','-tabbevelsize','8')
w(ftop + '.tabs','itemconfigure','manual','-text',' Manual - F3 ')
w(ftop + '.tabs','itemconfigure','mdi','-text',' MDI - F5 ')
w(ftop + '.right','configure','-arcradius','2','-tabbevelsize','8')
w(ftop + '.right','itemconfigure','preview','-text',' Preview ')
w(ftop + '.right','itemconfigure','numbers','-text',' DRO ')

# hide some original widgets
w('pack','forget','.toolbar.rule0')
w('pack','forget','.toolbar.rule4')
w('pack','forget','.toolbar.rule8')
w('pack','forget','.toolbar.rule9')
w('grid','forget',fmanual + '.axis')
w('grid','forget',fmanual + '.jogf')
w('grid','forget',fmanual + '.space2')
w('grid','forget',fmanual + '.spindlel')
w('grid','forget',fmanual + '.spindlef')
w('grid','forget',fmanual + '.space2')
w('grid','forget',fmanual + '.coolant')
w('grid','forget',fmanual + '.mist')
w('grid','forget',fmanual + '.flood')
w('grid','forget',ftop + '.spinoverride')

# change layout for some scales
w('pack','forget',ftop + '.jogspeed.l0')
w('pack','forget',ftop + '.jogspeed.l')
w('pack','forget',ftop + '.jogspeed.l1')
w('pack','forget',ftop + '.jogspeed.s')
w('pack','forget',ftop + '.maxvel.l0')
w('pack','forget',ftop + '.maxvel.l')
w('pack','forget',ftop + '.maxvel.l1')
w('pack','forget',ftop + '.maxvel.s')
w('pack',ftop + '.jogspeed.s','-side','right')
w('pack',ftop + '.jogspeed.l1','-side','right')
w('pack',ftop + '.jogspeed.l','-side','right')
w('pack',ftop + '.jogspeed.l0','-side','left')
w('pack',ftop + '.maxvel.s','-side','right')
w('pack',ftop + '.maxvel.l1','-side','right')
w('pack',ftop + '.maxvel.l','-side','right')
w('pack',ftop + '.maxvel.l0','-side','left')

# modify the toolbar
w('label','.toolbar.space1','-width','5')
w('label','.toolbar.space2','-width','5')
w('label','.toolbar.space3','-width','5')
w('label','.toolbar.space4','-width','10')
w('pack','.toolbar.space1','-after','.toolbar.machine_power','-side','left')
w('pack','.toolbar.space2','-after','.toolbar.reload','-side','left')
w('pack','.toolbar.space3','-after','.toolbar.program_stop','-side','left')
w('pack','.toolbar.space4','-after','.toolbar.program_optpause','-side','left')

# set sizes for widgets
swidth = 5  # spinboxes width
lwidth = 11 # labels width
bwidth = 8  # buttons width
cwidth = int(fsize) * 2 #canvas width
cheight = int(fsize) * 2 #canvas height
ledwidth = cwidth - 2 #led width
ledheight = cheight - 2 #led height
ledx = cwidth-ledwidth # led x start
ledy = cheight-ledheight # led y start

# rework the axis/joints frame
w('destroy',faxes)
w('labelframe',faxes,'-text','Axis:','-relief','ridge')
w('destroy',fjoints)
w('labelframe',fjoints,'-text','Joint:','-relief','ridge')
# make axis radiobuttons
for letter in 'xyzabcuvw':
    w('radiobutton',faxes + '.axis' + letter,\
                        '-anchor','w',\
                        '-padx','0',\
                        '-value',letter,\
                        '-variable','ja_rbutton',\
                        '-width','2',\
                        '-text',letter.upper(),\
                        '-command','ja_button_activated',\
                        )
# populate the axes frame
count = 0
letters = 'xyzabcuvw'
first_axis = ''
for row in range(0,2):
    for column in range(0,5):
        if letters[count] in trajcoordinates:
            if first_axis == '':
                first_axis = letters[count]
            w('grid',faxes + '.axis' + letters[count],'-row',row,'-column',column,'-padx','4')
        count += 1
        if count == 9: break
# make joints radiobuttons
for number in range(0,linuxcnc.MAX_JOINTS):
    w('radiobutton',fjoints + '.joint' + str(number),\
                        '-anchor','w',\
                        '-padx','0',\
                        '-value',number,\
                        '-variable','ja_rbutton',\
                        '-width','2',\
                        '-text',number,\
                        '-command','ja_button_activated',\
                        )
# populate joints frame
count = 0
for row in range(0,2):
    for column in range(0,5):
        if count == jointcount: break
        w('grid',fjoints + '.joint' + str(count),'-row',row,'-column',column,'-padx','4')
        count += 1

# rework the jogf frame
w('destroy',fjogf)
w('labelframe',fjogf,'-relief','flat','-bd','0')
w('labelframe',fjogf + '.jog','-text','Jog','-relief','ridge')
w('button',fjogf + '.jog.jogminus','-command','if ![is_continuous] {jog_minus 1}','-height','1','-text','-')
w('bind',fjogf + '.jog.jogminus','<Button-1>','if [is_continuous] {jog_minus}')
w('bind',fjogf + '.jog.jogminus','<ButtonRelease-1>','if [is_continuous] {jog_stop}')
w('button',fjogf + '.jog.jogplus','-command','if ![is_continuous] {jog_plus 1}','-height','1','-text','+')
w('bind',fjogf + '.jog.jogplus','<Button-1>','if [is_continuous] {jog_plus}')
w('bind',fjogf + '.jog.jogplus','<ButtonRelease-1>','if [is_continuous] {jog_stop}')
w('combobox',fjogf + '.jog.jogincr','-editable','0','-textvariable','jogincrement','-value','Continuous','-width','10')
w(fjogf + '.jog.jogincr','list','insert','end','Continuous',0.1000,0.0100,0.0010,0.0001)
w('labelframe',fjogf + '.zerohome','-text','Zero','-relief','ridge')
w('button',fjogf + '.zerohome.home','-command','home_joint','-height','1')
w('setup_widget_accel',fjogf + '.zerohome.home','Home Axis')
w('button',fjogf + '.zerohome.zero','-command','touch_off_system','-height','1')
w('setup_widget_accel',fjogf + '.zerohome.zero','Touch Off')
# unused, just for tcl hierarchy
w('button',fjogf + '.zerohome.tooltouch')
w('checkbutton',fjogf + '.override')
# populate the jog frame
w('grid',fjogf + '.jog.jogminus','-row','0','-column','0','-padx','0 3','-sticky','nsew')
w('grid',fjogf + '.jog.jogplus','-row','0','-column','1','-padx','3 3','-sticky','nsew')
w('grid',fjogf + '.jog.jogincr','-row','0','-column','2','-padx','3 0','-sticky','nsew')
w('grid',fjogf + '.jog','-row','0','-column','0','-sticky','ew')
w('grid',fjogf + '.zerohome.home','-row','0','-column','0','-padx','0 3','-sticky','ew')
w('grid',fjogf + '.zerohome.zero','-row','0','-column','1','-padx','3 0','-sticky','ew')
w('grid',fjogf + '.zerohome','-row','1','-column','0','-pady','4 0','-sticky','ew')
w('grid',fjogf,'-column','0','-row','1','-padx','4','-pady','2 0','-sticky','ew')
w('grid','columnconfigure',fmanual,'0','-weight','1')
w('grid','columnconfigure',fjogf,'0','-weight','1')
w('grid','columnconfigure',fjogf + '.jog','0 1 2','-weight','1')
w('grid','columnconfigure',fjogf + '.zerohome','0 1','-weight','1')
w('DynamicHelp::add',fjogf + '.jog.jogminus','-text','Jog selected axis\nin negative direction')
w('DynamicHelp::add',fjogf + '.jog.jogplus','-text','Jog selected axis\nin positive direction')
w('DynamicHelp::add',fjogf + '.jog.jogincr','-text','Select jog increment')
if homing_order_defined:
    if ja_name.startswith('A'):
        hbName = 'axes'
    else:
        hbName ='joints'
    widgets.homebutton.configure(text='Home All', command='home_all_joints')
    w('DynamicHelp::add',fjogf + '.zerohome.home','-text','Home all %s [Ctrl-Home]' % hbName)
else:
    w('DynamicHelp::add',fjogf + '.zerohome.home','-text','Home selected %s [Home]' % ja_name.lower())
w('DynamicHelp::add',fjogf + '.zerohome.zero','-text','Touch off selected axis\nto workpiece [Home]')

# torch frame
w('labelframe',ftorch,'-text','Torch:','-relief','ridge')
w('Button',ftorch + '.torch-button','-text','PULSE','-takefocus','0','-width','3')
w('bind',ftorch + '.torch-button','<Button-1>','torch_pulse 1')
w('bind',ftorch + '.torch-button','<ButtonRelease-1>','torch_pulse 0')
w('append','manualgroup',' ' + ftorch + '.torch-button')
w('scale',ftorch + '.torch-pulse-time','-orient','horizontal','-variable','torchPulse','-showvalue','0')
w('label',ftorch + '.torch-time','-textvariable','torchPulse','-width','3','-anchor','e')
w('label',ftorch + '.torch-label','-text','Sec','-anchor','e')
w('pack',ftorch + '.torch-button','-side','left','-pady','2')
w('pack',ftorch + '.torch-pulse-time','-side','left','-fill','x','-expand','1')
w('pack',ftorch + '.torch-label','-side','right')
w('pack',ftorch + '.torch-time','-side','right')
w('grid',ftorch,'-column','0','-row','2','-columnspan','1','-padx','4','-pady','2 0','-sticky','ew')
w('DynamicHelp::add',ftorch + '.torch-button','-text','Pulse torch on for\nselected time')
w('DynamicHelp::add',ftorch + '.torch-pulse-time','-text','Length of torch pulse (seconds)')

# override frame
w('labelframe',foverride,'-text','Height Override:','-relief','ridge')
w('scale',foverride + '.height-override','-orient','horizontal')
w('pack',foverride + '.height-override','-fill','x','-expand','1')
w('grid',foverride,'-column','0','-row','3','-columnspan','1','-padx','4','-pady','2 0','-sticky','ew')
w('DynamicHelp::add',foverride + '.height-override','-text','Adjust torch height dynamically')

# paused motion frame
w('labelframe',fpausedmotion,'-text','Paused Motion Speed:','-relief','ridge')
w('Button',fpausedmotion + '.reverse','-text','Rev','-takefocus','0','-width','3')
w('bind',fpausedmotion + '.reverse','<Button-1>','paused_motion -1')
w('bind',fpausedmotion + '.reverse','<ButtonRelease-1>','paused_motion 0')
w('scale',fpausedmotion + '.paused-motion-speed','-orient','horizontal')
w('Button',fpausedmotion + '.forward','-text','Fwd','-takefocus','0','-width','3')
w('bind',fpausedmotion + '.forward','<Button-1>','paused_motion 1')
w('bind',fpausedmotion + '.forward','<ButtonRelease-1>','paused_motion 0')
w('pack',fpausedmotion + '.reverse','-side','left','-fill','y')
w('pack',fpausedmotion + '.paused-motion-speed','-side','left','-fill','x','-expand','1')
w('pack',fpausedmotion + '.forward','-side','right','-fill','y')
w('grid',fpausedmotion,'-column','0','-row','4','-columnspan','1','-padx','4','-pady','2 0','-sticky','ew')
w('DynamicHelp::add',fpausedmotion + '.reverse','-text','Move while paused\nin reverse direction')
w('DynamicHelp::add',fpausedmotion + '.forward','-text','Move while paused\nin foward direction')
w('DynamicHelp::add',fpausedmotion + '.paused-motion-speed','-text','Paused motion speed (% of feed rate)')

# hide bottom pane until modified
w('pack','forget','.pane.bottom.t.text')
w('pack','forget','.pane.bottom.t.sb')

# common frame
w('labelframe',fcommon,'-text','','-relief','raised')

# monitor frame
w('labelframe',fmonitor,'-text','','-relief','flat')
arcfont = fname + ' ' + str(int(fsize) + 2) + ' bold'
w('label',fmonitor + '.arc-voltage','-anchor','e','-width',swidth,'-fg','blue','-font',arcfont)
w('label',fmonitor + '.aVlab','-text','Arc Voltage')
w('canvas',fmonitor + '.led-float','-width',cwidth,'-height',cheight)
w(fmonitor + '.led-float','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
w('label',fmonitor + '.lFlab','-text','Float Switch')
w('canvas',fmonitor + '.led-torch','-width',cwidth,'-height',cheight)
w(fmonitor + '.led-torch','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','orange','-disabledfill','grey')
w('label',fmonitor + '.lTlab','-text','Torch On')
w('canvas',fmonitor + '.led-breakaway','-width',cwidth,'-height',cheight)
w(fmonitor + '.led-breakaway','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
w('label',fmonitor + '.lBlab','-text','Breakaway')
w('canvas',fmonitor + '.led-arc-ok','-width',cwidth,'-height',cheight)
w(fmonitor + '.led-arc-ok','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','lightgreen','-disabledfill','grey')
w('label',fmonitor + '.lAOlab','-text','Ark OK')
w('canvas',fmonitor + '.led-safe-height','-width',cwidth,'-height',cheight)
w(fmonitor + '.led-safe-height','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
w('label',fmonitor + '.lSHlab','-text','Safe Limited')
w('grid',fmonitor + '.arc-voltage','-row','0','-column','0','-sticky','e')
w('grid',fmonitor + '.aVlab','-row','0','-column','1',)
w('grid',fmonitor + '.led-torch','-row','1','-column','0','-sticky','e')
w('grid',fmonitor + '.lTlab','-row','1','-column','1')
w('grid',fmonitor + '.led-float','-row','2','-column','0','-sticky','e')
w('grid',fmonitor + '.lFlab','-row','2','-column','1')
w('grid',fmonitor + '.led-breakaway','-row','3','-column','0','-sticky','e')
w('grid',fmonitor + '.lBlab','-row','3','-column','1')
w('grid',fmonitor + '.led-arc-ok','-row','4','-column','0','-sticky','e')
w('grid',fmonitor + '.lAOlab','-row','4','-column','1')
w('grid',fmonitor + '.led-safe-height','-row','5','-column','0','-sticky','e')
w('grid',fmonitor + '.lSHlab','-row','5','-column','1')
w('grid','rowconfigure',fmonitor,'0 1 2 3 4 5','-pad','4')
w('DynamicHelp::add',fmonitor + '.arc-voltage','-text','Current arc voltage')
w('DynamicHelp::add',fmonitor + '.led-torch','-text','Torch status indicator')
w('DynamicHelp::add',fmonitor + '.led-float','-text','Float switch status indicator')
w('DynamicHelp::add',fmonitor + '.led-breakaway','-text','Breakaway switch status indicator')
w('DynamicHelp::add',fmonitor + '.led-arc-ok','-text','Arc OK status indicator')
w('DynamicHelp::add',fmonitor + '.led-safe-height','-text','Safe height reduced status indicator')

# buttons frame
w('labelframe',fbuttons,'-relief','flat')
w('button',fbuttons + '.xtohome','-text','X to Home','-command','x_to_home','-width',bwidth)
w('button',fbuttons + '.ytohome','-text','Y to Home','-command','y_to_home','-width',bwidth)
w('button',fbuttons + '.ztohome','-text','Z to Home','-command','z_to_home','-width',bwidth)
w('button',fbuttons + '.dryRun','-text','Dry Run','-width',bwidth)
w('bind',fbuttons + '.dryRun','<Button-1>','dry_run 1')
w('bind',fbuttons + '.dryRun','<ButtonRelease-1>','dry_run 0')
w('grid',fbuttons + '.xtohome','-row','0','-column','0')
w('grid',fbuttons + '.ytohome','-row','1','-column','0')
w('grid',fbuttons + '.ztohome','-row','2','-column','0')
w('grid',fbuttons + '.dryRun','-row','3','-column','0')
w('grid','columnconfigure',fbuttons,0,'-weight','1')
w('DynamicHelp::add',fbuttons + '.xtohome','-text','Send the X axis to the home position')
w('DynamicHelp::add',fbuttons + '.ytohome','-text','Send the Y axis to the home position')
w('DynamicHelp::add',fbuttons + '.ztohome','-text','Send the Z axis to the home position')
w('DynamicHelp::add',fbuttons + '.dryRun','-text','Start a dry run\nFollows all gcode without torch')

# populate bottom frame
w('frame',fcommon + '.spaceframe','-relief','sunken')
w('pack',fmonitor,'-fill','y','-side','left')
w('pack',fcommon + '.spaceframe','-fill','x','-side','left')
w('pack',fbuttons,'-fill','y','-side','left')
w(ft,'configure','-relief','flat')
w(ft + '.text','configure','-borderwidth','2','-relief','sunken')
w('pack',fcommon,'-fill','both','-side','left')
w('pack',ft + '.sb','-fill','y','-side','left','-padx','4')
#w(ft +'.text','configure','-width','20')
w('pack',ft + '.text','-fill','both','-expand','1','-side','left','-padx','0','-pady','0')

# new notebook for plasmac stuff
w('NoteBook','.plasmac','-borderwidth','2','-arcradius','2','-tabbevelsize','8')
w('.plasmac','insert','end','run','-text','Run')
w('.plasmac','insert','end','config','-text','Configure')

# frames for run tab
w('labelframe',fmaterial,'-text','Material','-relief','ridge')
w('labelframe',fcutparms,'-text','Cut Parameters','-relief','ridge')
w('labelframe',fthc,'-text','THC','-relief','ridge')
w('labelframe',flocks,'-text','Locks','-relief','ridge')

# frames for config tab
w('labelframe',fmotion,'-text','Motion','-relief','ridge')
w('labelframe',farc,'-text','Arc','-relief','ridge')
w('labelframe',foffsets,'-text','Offsets','-relief','ridge')
w('labelframe',fsettings,'-text','Settings','-relief','ridge')

# material frame
w('ComboBox',fmaterial + '.materials','-modifycmd','material_changed')
w('DynamicHelp::add',fmaterial + '.materials','-text','select material from materials file')
w('pack',fmaterial + '.materials','-fill','x')
w('DynamicHelp::add',fmaterial + '.materials','-text','Select the material to be cut')

# cut parameters frame
w('spinbox',fcutparms + '.pierce-height')
w('DynamicHelp::add',fcutparms + '.pierce-height','-text','piercing height\nin machine units')
w('label',fcutparms + '.pHlab','-text','Pierce Height')
w('spinbox',fcutparms + '.pierce-delay')
w('label',fcutparms + '.pDlab','-text','Pierce Delay')
w('spinbox',fcutparms + '.cut-height')
w('label',fcutparms + '.cHlab','-text','Cut Height')
w('spinbox',fcutparms + '.cut-feed-rate')
w('label',fcutparms + '.cFRlab','-text','Cut Feed Rate')
w('spinbox',fcutparms + '.puddle-jump-height')
w('label',fcutparms + '.pJHlab','-text','P-J Height')
w('spinbox',fcutparms + '.puddle-jump-delay')
w('label',fcutparms + '.pJDlab','-text','P-J Delay')
w('spinbox',fcutparms + '.cut-amps')
w('label',fcutparms + '.cAlab','-text','Cut Amps')
w('spinbox',fcutparms + '.cut-volts')
w('label',fcutparms + '.cVlab','-text','Cut Volts')
w('grid',fcutparms + '.pierce-height','-row','0','-column','0')
w('grid',fcutparms + '.pHlab','-row','0','-column','1')
w('grid',fcutparms + '.pierce-delay','-row','1','-column','0')
w('grid',fcutparms + '.pDlab','-row','1','-column','1')
w('grid',fcutparms + '.cut-height','-row','2','-column','0')
w('grid',fcutparms + '.cHlab','-row','2','-column','1')
w('grid',fcutparms + '.cut-feed-rate','-row','3','-column','0')
w('grid',fcutparms + '.cFRlab','-row','3','-column','1')
w('grid',fcutparms + '.puddle-jump-height','-row','4','-column','0')
w('grid',fcutparms + '.pJHlab','-row','4','-column','1')
w('grid',fcutparms + '.puddle-jump-delay','-row','5','-column','0')
w('grid',fcutparms + '.pJDlab','-row','5','-column','1')
w('grid',fcutparms + '.cut-amps','-row','6','-column','0')
w('grid',fcutparms + '.cAlab','-row','6','-column','1')
w('grid',fcutparms + '.cut-volts','-row','7','-column','0')
w('grid',fcutparms + '.cVlab','-row','7','-column','1')
w('grid','rowconfigure',fcutparms,'0 1 2 3 4 5 6 7','-pad','2')
w('grid','columnconfigure',fcutparms,'0 1 2 3','-weight','1')
w('DynamicHelp::add',fcutparms + '.pierce-height','-text','Piercing height\n(machine units)')
w('DynamicHelp::add',fcutparms + '.pierce-delay','-text','Piercing time before moving\n(seconds)')
w('DynamicHelp::add',fcutparms + '.cut-height','-text','Cutting height\n(machine units)')
w('DynamicHelp::add',fcutparms + '.cut-feed-rate','-text','Cutting speed\n(machine units per minute)')
w('DynamicHelp::add',fcutparms + '.puddle-jump-height','-text','Puddle jump height\n(% of pierce height)')
w('DynamicHelp::add',fcutparms + '.puddle-jump-delay','-text','Puddle jump wait time\nbefore moving (seconds)')
w('DynamicHelp::add',fcutparms + '.cut-amps','-text','Cut amperage')
w('DynamicHelp::add',fcutparms + '.cut-volts','-text','Cut voltage')

# thc frame
w('checkbutton',fthc + '.thc-enable')
w('label',fthc + '.tElab','-text','Enable')
w('checkbutton',fthc + '.use-auto-volts')
w('label',fthc + '.uAVlab','-text','Use Auto Volts')
w('spinbox',fthc + '.thc-threshold')
w('label',fthc + '.tTlab','-text','Threshold')
w('spinbox',fthc + '.pid-p-gain')
w('label',fthc + '.pPGlab','-text','Speed (PID P)')
w('canvas',fthc + '.led-up','-width',cwidth,'-height',cheight)
w(fthc + '.led-up','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','yellow','-disabledfill','grey')
w('label',fthc + '.lUlab','-text','Move Up')
w('canvas',fthc + '.led-down','-width',cwidth,'-height',cheight)
w(fthc + '.led-down','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','yellow','-disabledfill','grey')
w('label',fthc + '.lDlab','-text','Move Down')
w('grid',fthc + '.thc-enable','-row','0','-column','0')
w('grid',fthc + '.tElab','-row','0','-column','1')
w('grid',fthc + '.use-auto-volts','-row','1','-column','0')
w('grid',fthc + '.uAVlab','-row','1','-column','1')
w('grid',fthc + '.thc-threshold','-row','2','-column','0')
w('grid',fthc + '.tTlab','-row','2','-column','1')
w('grid',fthc + '.pid-p-gain','-row','3','-column','0')
w('grid',fthc + '.pPGlab','-row','3','-column','1')
w('grid',fthc + '.led-up','-row','4','-column','0')
w('grid',fthc + '.lUlab','-row','4','-column','1')
w('grid',fthc + '.led-down','-row','5','-column','0')
w('grid',fthc + '.lDlab','-row','5','-column','1')
w('grid','rowconfigure',fthc,'2 3','-pad','2')
w('grid','columnconfigure',fthc,'0 1 2 3','-weight','1')
w('DynamicHelp::add',fthc + '.thc-enable','-text','Enable torch height control')
w('DynamicHelp::add',fthc + '.use-auto-volts','-text','Use sample voltage from cut\nrather than Cut Volts from above')
w('DynamicHelp::add',fthc + '.thc-threshold','-text','Voltage changes below this value\nwill not cause THC movement')
w('DynamicHelp::add',fthc + '.pid-p-gain','-text','Speed of THC movement')
w('DynamicHelp::add',fthc + '.led-up','-text','Torch is moving up')
w('DynamicHelp::add',fthc + '.led-down','-text','Torch id moving down')

# locks frame
w('labelframe',fcornerlock,'-text','Corner','-relief','sunken')
w('checkbutton',fcornerlock + '.cornerlock-enable')
w('label',fcornerlock + '.cElab','-text','Enable')
w('spinbox',fcornerlock + '.cornerlock-threshold')
w('label',fcornerlock + '.cTlab','-text','Threshold(%)')
w('canvas',fcornerlock + '.led-cornerlock','-width',cwidth,'-height',cheight)
w(fcornerlock + '.led-cornerlock','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
w('label',fcornerlock + '.lClab','-text','Locked(%)')
w('labelframe',fkerflock,'-text','Kerf','-relief','sunken')
w('checkbutton',fkerflock + '.kerfcross-enable')
w('label',fkerflock + '.kElab','-text','Enable')
w('spinbox',fkerflock + '.kerfcross-threshold')
w('label',fkerflock + '.kTlab','-text','Threshold(V)')
w('canvas',fkerflock + '.led-kerfcross','-width',cwidth,'-height',cheight)
w(fkerflock + '.led-kerfcross','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
w('label',fkerflock + '.lKlab','-text','Locked(%)')
w('grid',fcornerlock + '.cornerlock-enable','-row','0','-column','0')
w('grid',fcornerlock + '.cElab','-row','0','-column','1')
w('grid',fcornerlock + '.cornerlock-threshold','-row','1','-column','0')
w('grid',fcornerlock + '.cTlab','-row','1','-column','1')
w('grid',fcornerlock + '.led-cornerlock','-row','2','-column','0')
w('grid',fcornerlock + '.lClab','-row','2','-column','1')
w('grid',fkerflock + '.kerfcross-enable','-row','0','-column','0')
w('grid',fkerflock + '.kElab','-row','0','-column','1')
w('grid',fkerflock + '.kerfcross-threshold','-row','1','-column','0')
w('grid',fkerflock + '.kTlab','-row','1','-column','1')
w('grid',fkerflock + '.led-kerfcross','-row','2','-column','0')
w('grid',fkerflock + '.lKlab','-row','2','-column','1')
w('pack',fcornerlock,'-side','top','-padx','1','-pady','2','-fill','x')
w('pack',fkerflock,'-side','top','-padx','1','-pady','2','-fill','x')
w('grid','rowconfigure',fcornerlock,'1','-pad','2')
w('grid','rowconfigure',fkerflock,'1','-pad','2')
w('grid','columnconfigure',flocks,'0','-weight','1')
w('DynamicHelp::add',fcornerlock + '.cornerlock-enable','-text','Enable corner lock')
w('DynamicHelp::add',fcornerlock + '.cornerlock-threshold','-text','Corner lock is locked below this speed\n(% of feed rate)')
w('DynamicHelp::add',fcornerlock + '.led-cornerlock','-text','Corner lock is locked')
w('DynamicHelp::add',fkerflock + '.kerfcross-enable','-text','Enable kerf cross lock')
w('DynamicHelp::add',fkerflock + '.kerfcross-threshold','-text','Kerf cross lock is locked at changes above this voltage')
w('DynamicHelp::add',fkerflock + '.led-kerfcross','-text','Kerf cross lock is locked')

# motion frame
w('spinbox',fmotion + '.safe-height')
w('label',fmotion + '.sHlab','-text','Safe Height')
w('spinbox',fmotion + '.float-switch-travel')
w('label',fmotion + '.fSTlab','-text','Float Travel')
w('spinbox',fmotion + '.probe-feed-rate')
w('label',fmotion + '.pFRlab','-text','Probe Speed')
w('spinbox',fmotion + '.skip-ihs-distance','-from','0','-to','20')
w('label',fmotion + '.sIDlab','-text','Skip IHS')
w('grid',fmotion + '.safe-height','-row','0','-column','0')
w('grid',fmotion + '.sHlab','-row','0','-column','1')
w('grid',fmotion + '.float-switch-travel','-row','1','-column','0')
w('grid',fmotion + '.fSTlab','-row','1','-column','1')
w('grid',fmotion + '.probe-feed-rate','-row','2','-column','0')
w('grid',fmotion + '.pFRlab','-row','2','-column','1')
w('grid',fmotion + '.skip-ihs-distance','-row','3','-column','0')
w('grid',fmotion + '.sIDlab','-row','3','-column','1')
w('grid','rowconfigure',fmotion,'0 1 2 3','-pad','2')
w('grid','columnconfigure',fmotion,'0 1 2 3','-weight','1')
w('DynamicHelp::add',fmotion + '.safe-height','-text','Safe height above stock for rapid traverse\n(machine units)')
w('DynamicHelp::add',fmotion + '.float-switch-travel','-text','Float switch travel\n(machine units)')
w('DynamicHelp::add',fmotion + '.probe-feed-rate','-text','Probing speed\n(machine units per minute)')
w('DynamicHelp::add',fmotion + '.skip-ihs-distance','-text','Skip probing if start of cut\nis less than this distance\nfrom end of last cut')

# arc frame
w('spinbox',farc + '.arc-fail-delay')
w('label',farc + '.aFDlab','-text','Fail Timeout')
w('spinbox',farc + '.arc-max-starts')
w('label',farc + '.aMSlab','-text','Max. Starts')
w('spinbox',farc + '.restart-delay')
w('label',farc + '.aRDlab','-text','Retry Delay')
w('spinbox',farc + '.torch-off-delay')
w('label',farc + '.tODlab','-text','Off Delay')
w('spinbox',farc + '.arc-voltage-scale')
w('label',farc + '.aVSlab','-text','Voltage Scale')
w('spinbox',farc + '.arc-voltage-offset')
w('label',farc + '.aVOlab','-text','Voltage Offset')
w('spinbox',farc + '.arc-ok-high')
w('label',farc + '.aOHlab','-text','OK High Volts')
w('spinbox',farc + '.arc-ok-low')
w('label',farc + '.aOLlab','-text','OK Low Volts')
w('grid',farc + '.arc-fail-delay','-row','0','-column','0')
w('grid',farc + '.aFDlab','-row','0','-column','1')
w('grid',farc + '.arc-max-starts','-row','1','-column','0')
w('grid',farc + '.aMSlab','-row','1','-column','1')
w('grid',farc + '.restart-delay','-row','2','-column','0')
w('grid',farc + '.aRDlab','-row','2','-column','1')
w('grid',farc + '.torch-off-delay','-row','3','-column','0')
w('grid',farc + '.tODlab','-row','3','-column','1')
w('grid',farc + '.arc-voltage-scale','-row','4','-column','0')
w('grid',farc + '.aVSlab','-row','4','-column','1')
w('grid',farc + '.arc-voltage-offset','-row','5','-column','0')
w('grid',farc + '.aVOlab','-row','5','-column','1')
w('grid',farc + '.arc-ok-high','-row','6','-column','0')
w('grid',farc + '.aOHlab','-row','6','-column','1')
w('grid',farc + '.arc-ok-low','-row','7','-column','0')
w('grid',farc + '.aOLlab','-row','7','-column','1')
w('grid','rowconfigure',farc,'0 1 2 3 4 5 6 7','-pad','2')
w('grid','columnconfigure',farc,'0 1 2 3','-weight','1')
w('DynamicHelp::add',farc + '.arc-fail-delay','-text','Time to wait for arc ok signal\n(seconds)')
w('DynamicHelp::add',farc + '.arc-max-starts','-text','Maximum number of attemps\nto sart the torch')
w('DynamicHelp::add',farc + '.restart-delay','-text','Time to wait between arc start attempts')
w('DynamicHelp::add',farc + '.torch-off-delay','-text','Torch off time delay\n(seconds)')
w('DynamicHelp::add',farc + '.arc-voltage-scale','-text','Scale value to set correct voltage')
w('DynamicHelp::add',farc + '.arc-voltage-offset','-text','Offset value to set correct')
w('DynamicHelp::add',farc + '.arc-ok-high','-text','Maximum voltage for an arc ok signal')
w('DynamicHelp::add',farc + '.arc-ok-low','-text','Minimum voltage for an arc ok signal')

# offsets frame
w('label',foffsets + '.maxspeed','-text','0','-anchor','e','-width',swidth)
w('label',foffsets + '.msplab','-text','Max. Speed')
w('spinbox',foffsets + '.setup-feed-rate')
w('label',foffsets + '.sFRlab','-text','Setup Speed')
w('spinbox',foffsets + '.pid-i-gain')
w('label',foffsets + '.pIGlab','-text','PID I Gain')
w('spinbox',foffsets + '.pid-d-gain','-from','0','-to','20')
w('label',foffsets + '.pDGlab','-text','PID D Gain')
w('grid',foffsets + '.maxspeed','-row','0','-column','0')
w('grid',foffsets + '.msplab','-row','0','-column','1')
w('grid',foffsets + '.setup-feed-rate','-row','1','-column','0')
w('grid',foffsets + '.sFRlab','-row','1','-column','1')
w('grid',foffsets + '.pid-i-gain','-row','2','-column','0')
w('grid',foffsets + '.pIGlab','-row','2','-column','1')
w('grid',foffsets + '.pid-d-gain','-row','3','-column','0')
w('grid',foffsets + '.pDGlab','-row','3','-column','1')
w('grid','rowconfigure',foffsets,'0 1 2 3','-pad','2')
w('grid','columnconfigure',foffsets,'0 1 2 3','-weight','1')
w('DynamicHelp::add',foffsets + '.maxspeed','-text','Maximum allowed speed for Z axis')
w('DynamicHelp::add',foffsets + '.setup-feed-rate','-text','Speed of Z axis for start of cut moves\neg pierce, puddle jump and cut heights')
w('DynamicHelp::add',foffsets + '.pid-i-gain','-text','PID I gain')
w('DynamicHelp::add',foffsets + '.pid-d-gain','-text','PID D gain')

# settings frame
w('button',fsettings + '.save','-text','Save','-command','save_config','-width',bwidth)
w('button',fsettings + '.reload','-text','Reload','-width',bwidth,'-command','reload_config')
w('grid',fsettings + '.save','-row','0','-column','0')
w('grid',fsettings + '.reload','-row','0','-column','1')
w('grid','columnconfigure',fsettings,'0 1','-weight','1','-pad','2')
w('DynamicHelp::add',fsettings + '.save','-text','Save all current settings to file\nthis will also cause current cut\nparameters to be set as default')
w('DynamicHelp::add',fsettings + '.reload','-text','Reload all settings from file')

# populate run tab
w('pack',fmaterial,'-fill','x')
w('pack',fcutparms,'-fill','x')
w('pack',fthc,'-fill','x')
w('pack',flocks,'-fill','x')

# populate config tab
w('pack',fmotion,'-fill','x','-expand','0')
w('pack',farc,'-fill','x','-expand','0')
w('pack',foffsets,'-fill','x','-expand','0')
w('pack',fsettings,'-fill','x','-expand','0')

# move original pane to right
w('grid','.pane','-column','1','-row','1','-sticky','nsew','-rowspan','2')

# place new notebook left of original pane
w('.plasmac','raise','run')
w('grid','.plasmac','-column','0','-row','1','-sticky','nsew','-rowspan','2','-pady','3')
w('grid','columnconfigure','.','0','-weight','0')
w('grid','columnconfigure','.','1','-weight','1')



################################################################################
# some new commands for TCL
def material_changed():
    if not materialsUpdate:
        newmaterial = w(fmaterial + '.materials','getvalue')
        w(fcutparms + '.pierce-height','set',materialsList[newmaterial][1])
        w(fcutparms + '.pierce-delay','set',materialsList[newmaterial][2])
        w(fcutparms + '.puddle-jump-height','set',materialsList[newmaterial][3])
        w(fcutparms + '.puddle-jump-delay','set',materialsList[newmaterial][4])
        w(fcutparms + '.cut-height','set',materialsList[newmaterial][5])
        w(fcutparms + '.cut-feed-rate','set',materialsList[newmaterial][6])
        w(fcutparms + '.cut-amps','set',materialsList[newmaterial][7])
        w(fcutparms + '.cut-volts','set',materialsList[newmaterial][8])

def save_config():
    try:
        with open(configFile, 'w') as f_out:
            f_out.write('#plasmac configuration file, format is:\n#name = value\n\n')
            for key in sorted(configDict.iterkeys()):
                for widget in wCheckbuttons + wSpinboxes + wScalesConfig:
                    if widget.endswith(key):
                        if widget in wCheckbuttons:
                            value = w('set',key)
                            f_out.write(key + ' = ' + str(value) + '\n')
                            break
                        elif widget in wSpinboxes + wScalesConfig:
                            value = w(widget,'get')
                            f_out.write(key + ' = ' + str(value) + '\n')
                            break
    except:
        print '*** error opening', configFile
#    except Exception:
#        traceback.print_exc()
    finally:
        f_out.close()

def reload_config():
    materialsUpdate = True
    load_settings()
    global materialsList
    materialsList = []
    w(fmaterial + '.materials','configure','-values','')
    get_materials()
    materialsUpdate = False

def x_to_home():
    goto_home('X')

def y_to_home():
    goto_home('Y')

def z_to_home():
    goto_home('Z')

def dry_run(value):
    hal.set_p('plasmac.dry-run-start',value)

def torch_pulse(value):
    hal.set_p('plasmac.torch-pulse-start',value)

def paused_motion(direction):
    if w(fpausedmotion + '.forward','cget','-state') == 'normal' or\
       w(fpausedmotion + '.reverse','cget','-state') == 'normal':
        speed = float(w(fpausedmotion + '.paused-motion-speed','get'))
        hal.set_p('plasmac.paused-motion-speed','%f' % (speed * int(direction)))

def goto_home(axis):
    if hal.get_value('halui.program.is-idle'):
        home = inifile.find('JOINT_' + str(inifile.find('TRAJ', 'COORDINATES').upper().index(axis)), 'HOME')
        mode = hal.get_value('halui.mode.is-mdi')
        if not mode:
            c.mode(linuxcnc.MODE_MDI)
        c.mdi('G53 G0 ' + axis + home)

def joint_mode_switch(a,b,c):
    if vars.motion_mode.get() == linuxcnc.TRAJ_MODE_FREE and s.kinematics_type != linuxcnc.KINEMATICS_IDENTITY:
        w('grid','forget',fmanual + '.axes')
        w('grid',fmanual + '.joints','-column','0','-row','0','-padx','4','-pady','0','-sticky','ew')
        widget = getattr(widgets, "joint_%d" % 0)
        widget.focus()
        vars.ja_rbutton.set(0)
    else:
        w('grid','forget',fmanual + '.joints')
        w('grid',fmanual + '.axes','-column','0','-row','0','-padx','4','-pady','0','-sticky','ew')
        widget = getattr(widgets, "axis_%s" % first_axis)
        widget.focus()
        vars.ja_rbutton.set(first_axis)

def ja_button_activated():
    if vars.ja_rbutton.get() in 'xyzabcuvw':
        widget = getattr(widgets, "axis_%s" % vars.ja_rbutton.get())
        widget.focus()
    else:
        widget = getattr(widgets, "joint_%s" % vars.ja_rbutton.get())
        widget.focus()
    commands.axis_activated

# add the commands to TclCommands
TclCommands.material_changed = material_changed
TclCommands.save_config = save_config
TclCommands.reload_config = reload_config
TclCommands.x_to_home = x_to_home
TclCommands.y_to_home = y_to_home
TclCommands.z_to_home = z_to_home
TclCommands.dry_run = dry_run
TclCommands.torch_pulse = torch_pulse
TclCommands.paused_motion = paused_motion
TclCommands.joint_mode_switch = joint_mode_switch
TclCommands.ja_button_activated = ja_button_activated
commands = TclCommands(root_window)



################################################################################
# some python functions

# original in axis.py line 3000
def user_live_update():
    global firstrundone
    if not firstrundone:
        configDisable = inifile.find('PLASMAC', 'CONFIG_DISABLE') or '0'
        hal.set_p('axisui.config-disable',configDisable)
        spaceWidth = w('winfo','width',fmanual)
        spaceWidth -= w('winfo','width',fmonitor)
        spaceWidth -= w('winfo','width',fbuttons)
        w(fcommon + '.spaceframe','configure','-width',spaceWidth)
        firstrundone = 1
    for widget in wSpinboxes + wScalesHal:
        tmp, item = widget.rsplit('.',1)
        if item != 'cut-amps':
            value = float(w(widget,'get'))
            if value != widgetValues[widget]:
                widgetValues[widget] = value
                if item == 'arc-max-starts':
                    hal.set_p('plasmac.%s' % (item),'%d' % (value))
                else:
                    hal.set_p('plasmac.%s' % (item),'%f' % (value))
                if item == 'setup-feed-rate': #limit max probe feed rate to setup feed rate
                    w(fmotion + '.probe-feed-rate','configure','-to',value)
    for widget in wCheckbuttons:
        tmp, item = widget.rsplit('.',1)
        value = int(w('set',item))
        if value != widgetValues[widget]:
            widgetValues[widget] = value
            hal.set_p('plasmac.%s' % (item),'%d' % (value))
    for widget in wLeds:
        tmp, item = widget.rsplit('.',1)
        if comp[item] != widgetValues[widget]:
            widgetValues[widget] = comp[item]
            if comp[item] == 1:
                w(widget,'configure','-state','normal')
            else:
                w(widget,'configure','-state','disabled')
    w(fmonitor + '.arc-voltage','configure','-text','%0.1f' % (comp['arc-voltage']))
    if all_homed() and hal.get_value('halui.program.is-idle'):
        w(fbuttons + '.xtohome','configure','-state','normal')
        w(fbuttons + '.ytohome','configure','-state','normal')
        w(fbuttons + '.ztohome','configure','-state','normal')
        w(fbuttons + '.dryRun','configure','-state','normal')
    else:
        w(fbuttons + '.xtohome','configure','-state','disabled')
        w(fbuttons + '.ytohome','configure','-state','disabled')
        w(fbuttons + '.ztohome','configure','-state','disabled')
        w(fbuttons + '.dryRun','configure','-state','disabled')
    if hal.get_value('halui.machine.is-on') and hal.get_value('halui.program.is-idle'):
        w(ftorch + '.torch-button','configure','-state','normal')
    else:
        w(ftorch + '.torch-button','configure','-state','disabled')
    if hal.get_value('halui.program.is-paused') or hal.get_value('plasmac.paused-motion-speed'):
        w(fpausedmotion + '.reverse','configure','-state','normal')
        w(fpausedmotion + '.forward','configure','-state','normal')
    else:
        w(fpausedmotion + '.reverse','configure','-state','disabled')
        w(fpausedmotion + '.forward','configure','-state','disabled')
    if hal.get_value('axisui.config-disable'):
        w('.plasmac','itemconfigure','config','-state','disabled')
    else:
        w('.plasmac','itemconfigure','config','-state','normal')


def user_hal_pins():
    comp.newpin('arc-voltage', hal.HAL_FLOAT, hal.HAL_IN)
    comp.newpin('led-up', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-down', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-cornerlock', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-kerfcross', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-arc-ok', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-torch', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-float', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-breakaway', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('led-safe-height', hal.HAL_BIT, hal.HAL_IN)
    comp.newpin('config-disable', hal.HAL_BIT, hal.HAL_IN)
    comp.ready()
    hal_data = [[0,'plasmac:arc-voltage-out','plasmac.arc-voltage-out','axisui.arc-voltage'],\
                [1,'plasmac:axis-min-limit','ini.z.min_limit','plasmac.axis-z-min-limit'],\
                [2,'plasmac:axis-max-limit','ini.z.max_limit','plasmac.axis-z-max-limit'],\
                [3,'plasmac:led-up','plasmac.led-up','axisui.led-up'],\
                [4,'plasmac:led-down','plasmac.led-down','axisui.led-down'],\
                [5,'plasmac:cornerlock-is-locked','plasmac.cornerlock-is-locked','axisui.led-cornerlock'],\
                [6,'plasmac:kerfcross-is-locked','plasmac.kerfcross-is-locked','axisui.led-kerfcross'],\
                [7,'plasmac:arc-ok-out','plasmac.arc-ok-out','axisui.led-arc-ok'],\
                [8,'plasmac:safe-height-is-limited','plasmac.safe-height-is-limited','axisui.led-safe-height'],\
                ]
    for line in hal_data:
        if line[0] < 3:
            hal.new_sig(line[1],hal.HAL_FLOAT)
        else:
            hal.new_sig(line[1],hal.HAL_BIT)
        hal.connect(line[2],line[1])
        hal.connect(line[3],line[1])
    hal.connect('axisui.led-float','plasmac:float-switch-out')
    hal.connect('axisui.led-breakaway','plasmac:breakaway-switch-out')
    hal.connect('axisui.led-torch','plasmac:torch-on')

def configure_widgets():
    w(ftorch + '.torch-pulse-time','configure','-from','0','-to','3','-resolution','0.1')
    w(foverride + '.height-override','configure','-from','-10','-to','10','-resolution','0.1') #0
    w(fpausedmotion + '.paused-motion-speed','configure','-from','.01','-to','1','-resolution','0.01') #0
    w(fcutparms + '.pierce-delay','configure','-from','0','-to','10','-increment','0.1','-format','%0.1f') #0.1
    w(fcutparms + '.puddle-jump-height','configure','-from','0','-to','200','-increment','1','-format','%0.0f') #0
    w(fcutparms + '.puddle-jump-delay','configure','-from','0','-to','9','-increment','0.01','-format','%0.2f') #0
    w(fcutparms + '.cut-amps','configure','-from','0','-to','999','-increment','1','-format','%0.0f') #45
    w(fcutparms + '.cut-volts','configure','-from','50','-to','300','-increment','0.1','-format','%0.1f') #122
    w(fthc + '.use-auto-volts','select')
    w(fthc + '.thc-enable','select')
    w(fthc + '.thc-threshold','configure','-from','0.05','-to','9','-increment','0.01','-format','%0.2f') #1
    w(fcornerlock + '.cornerlock-enable','select')
    w(fcornerlock + '.cornerlock-threshold','configure','-from','1','-to','99','-increment','1','-format','%0.0f') #90
    w(fkerflock + '.kerfcross-enable','select')
    w(fkerflock + '.kerfcross-threshold','configure','-from','1','-to','10','-increment','0.1','-format','%0.1f') #3
    w(farc + '.torch-off-delay','configure','-from','0','-to','9','-increment','0.1','-format','%0.1f') #0
    w(farc + '.arc-fail-delay','configure','-from','0','-to','60','-increment','0.1','-format','%0.1f') #1
    w(farc + '.arc-ok-low','configure','-from','0','-to','200','-increment','0.5','-format','%0.1f') #0
    w(farc + '.arc-ok-high','configure','-from','50','-to','200','-increment','0.5','-format','%0.1f') #50
    w(farc + '.arc-max-starts','configure','-from','1','-to','9','-increment','1','-format','%0.0f') #3
    w(farc + '.restart-delay','configure','-from','1','-to','60','-increment','1','-format','%0.0f') #1
    w(farc + '.arc-voltage-offset','configure','-from','-100','-to','100','-increment','0.1','-format','%0.1f') #0
    w(farc + '.arc-voltage-scale','configure','-from','0.01','-to','99','-increment','0.01','-format','%0.2f') #1
    w(foffsets + '.maxspeed','configure','-text',str(int(thcFeedRate)))
    w(foffsets + '.pid-i-gain','configure','-from','0','-to','1000','-increment','1','-format','%0.0f') #0
    w(foffsets + '.pid-d-gain','configure','-from','0','-to','1000','-increment','1','-format','%0.0f') #0
    if inifile.find('TRAJ','LINEAR_UNITS').lower() == 'mm':
        w(fcutparms + '.cut-feed-rate','configure','-from','50','-to','9999','-increment','1','-format','%0.0f') #4000
        w(fcutparms + '.cut-height','configure','-from','0','-to','25.4','-increment','0.1','-format','%0.1f') #1
        w(fcutparms + '.pierce-height','configure','-from','0','-to','25.4','-increment','0.1','-format','%0.1f') #4
        w(fmotion + '.float-switch-travel','configure','-from','0','-to','20','-increment','0.01','-format','%0.2f') #1.5
        w(fmotion + '.probe-feed-rate','configure','-from','1','-to',thcFeedRate,'-increment','1','-format','%0.0f') #300
        w(fmotion + '.safe-height','configure','-from','1','-to','99','-increment','1','-format','%0.0f') #20
        w(fmotion + '.skip-ihs-distance','configure','-from','0','-to','999','-increment','1','-format','%0.0f') #0
        w(foffsets + '.setup-feed-rate','configure','-from','1','-to',thcFeedRate,'-increment','1','-format','%0.0f') #int(thcFeedRate * 0.8)
    elif inifile.find('TRAJ','LINEAR_UNITS').lower() == 'inch':
        w(fcutparms + '.cut-feed-rate','configure','-from','2','-to','400','-increment','0.1','-format','%0.1f') #160
        w(fcutparms + '.cut-height','configure','-from','0','-to','1','-increment','0.01','-format','%0.2f') #0.04
        w(fcutparms + '.pierce-height','configure','-from','0','-to','1','-increment','0.01','-format','%0.2f') #0.16
        w(fmotion + '.float-switch-travel','configure','-from','0','-to','0.75','-increment','0.001','-format','%0.3f') #0.06
        w(fmotion + '.probe-feed-rate','configure','-from','0.1','-to',thcFeedRate,'-increment','0.1','-format','%0.1f') #12
        w(fmotion + '.safe-height','configure','-from','0.04','-to','4','-increment','0.01','-format','%0.2f') #0.75
        w(fmotion + '.skip-ihs-distance','configure','-from','0','-to','99','-increment','0.1','-format','%0.1f') #0
        w(foffsets + '.setup-feed-rate','configure','-from','0.1','-to',thcFeedRate,'-increment','0.1','-format','%0.1f') #int(thcFeedRate * 0.8)
    else:
        print '*** incorrect [TRAJ]LINEAR_UNITS in ini file'

def load_settings():
    for widget in wCheckbuttons + wSpinboxes + wScalesConfig:
        tmp, item = widget.rsplit('.',1)
        if item != 'height-override':
            configDict[item] = '0'
    convertFile = False
    if os.path.exists(configFile):
        try:
            tmpDict = {}
            with open(configFile, 'r') as f_in:
                for line in f_in:
                    if not line.startswith('#') and not line.startswith('[') and not line.startswith('\n'):
                        if 'version' in line or 'signature' in line:
                            convertFile = True
                        else:
                            (key, value) = line.strip().replace(" ", "").split('=')
                            if value == 'True':value = True
                            if value == 'False':value = False
                            if key in configDict:
                                configDict[key] = value
                                tmpDict[key] = value
        except:
            print '*** plasmac configuration file,', configFile, 'is invalid ***'
        finally:
            f_in.close()
        for widget in wCheckbuttons + wSpinboxes + wScalesConfig:
            tmp, item = widget.rsplit('.',1)
            if widget in wCheckbuttons:
                if item in tmpDict:
                    if configDict.get(item) == '1':
                        w(widget,'select')
                        hal.set_p('plasmac.%s' % (item),'1')
                    else:
                        w(widget,'deselect')
                        hal.set_p('plasmac.%s' % (item),'0')
                else:
                    w(widget,'deselect')
                    hal.set_p('plasmac.%s' % (item),'0')
                    print '***', item, 'missing from', configFile
            elif widget in wSpinboxes + wScalesConfig:
                if item in tmpDict:
                    if item == 'setup-feed-rate' and float(configDict.get(item)) > thcFeedRate:
                        configDict[item] = thcFeedRate
                    w(widget,'set',configDict.get(item))
                    if item == 'arc-max-starts':
                        hal.set_p('plasmac.%s' % (item),'%d' % (float(configDict.get(item))))
                    elif item != 'cut-amps' and item != 'paused-motion-speed':
                        hal.set_p('plasmac.%s' % (item),'%f' % (float(configDict.get(item))))
                else:
                    w(widget,'set','0')
                    print '***', item, 'missing from', configFile
        if convertFile:
            print '*** converting', configFile, 'to new format'
            save_config()
    else:
        save_config()
        print '*** creating new plasmac configuration file,', configFile

def check_materials_file():
    version = '[VERSION 1]'
    header ='\
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
\n'
    tempMaterialsList = []
    if os.path.exists(materialsFile):
        if not version in open(materialsFile).read():
            print '*** upgrading material file...'
            with open(materialsFile, 'r') as f_in:
                for line in f_in:
                    if not line.strip().startswith('#') and len(line.strip()):
                        name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts = line.split(',')
                        name = name.strip()
                        tempMaterialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
            with open(materialsFile, 'w') as f_out:
                f_out.write(header)
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
        with open(materialsFile, 'w') as f_out:
            f_out.write(header)
        print '*** new material file,', materialsFile, 'created'

def get_materials():
    name = 'Default'
    p_height = w(fcutparms + '.pierce-height','get')
    p_delay = w(fcutparms + '.pierce-delay','get')
    pj_height = w(fcutparms + '.puddle-jump-height','get')
    pj_delay = w(fcutparms + '.puddle-jump-delay','get')
    c_height = w(fcutparms + '.cut-height','get')
    c_speed = w(fcutparms + '.cut-feed-rate','get')
    c_amps = w(fcutparms + '.cut-amps','get')
    c_volts = w(fcutparms + '.cut-volts','get')
    try:
        with open(materialsFile, 'r') as f_in:
            for line in f_in:
                if not line.startswith('#'):
                    if line.startswith('[') and line.strip().endswith(']') and not 'VERSION' in line:
                        materialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
                        w(fmaterial + '.materials','insert','end',name)
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
            materialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
            w(fmaterial + '.materials','insert','end',name)
        w(fmaterial + '.materials','setvalue','first')
    except:
        print '*** materials file,', materialsFile, 'is invalid'
    finally:
        f_in.close()

def set_mode(mode):
    if mode == '0':
        w(fthc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
    elif mode == '1':
        w(fthc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
        w('grid','forget',farc + '.arc-ok-high')
        w('grid','forget',farc + '.aOHlab')
        w('grid','forget',farc + '.arc-ok-low')
        w('grid','forget',farc + '.aOLlab')
    elif mode == '2':
        w(fthc + '.pid-p-gain','configure','-from','0','-to','100','-increment','1','-format','%0.0f') #25
        w(fthc + '.pPGlab','configure','-text','Speed (%)')
        w('grid','forget',fthc + '.use-auto-volts')
        w('grid','forget',fthc + '.uAVlab') 
        w('grid','forget',fthc + '.thc-threshold')
        w('grid','forget',fthc + '.tTlab')
        w('pack','forget',fkerflock)
        w('grid','forget',farc + '.arc-ok-high')
        w('grid','forget',farc + '.aOHlab')
        w('grid','forget',farc + '.arc-ok-low')
        w('grid','forget',farc + '.aOLlab')
        w('grid','forget',farc + '.arc-voltage-scale')
        w('grid','forget',farc + '.aVSlab')
        w('grid','forget',farc + '.arc-voltage-offset')
        w('grid','forget',farc + '.aVOlab')
        w('grid','forget',foffsets + '.pid-i-gain')
        w('grid','forget',foffsets + '.pIGlab')
        w('grid','forget',foffsets + '.pid-d-gain')
        w('grid','forget',foffsets + '.pDGlab')
        w('grid','forget',fmonitor + '.arc-voltage')
        w('grid','forget',fmonitor + '.aVlab')
    hal.set_p('plasmac.mode','%d' % (int(mode)))



################################################################################
# setup
firstrundone = 0
thcFeedRate = (float(inifile.find('AXIS_Z','MAX_VELOCITY')) * \
               float(inifile.find('AXIS_Z','OFFSET_AV_RATIO'))) * 60
hal.set_p('plasmac.thc-feed-rate','%f' % (thcFeedRate))
configFile = inifile.find('EMC','MACHINE').lower() + '.cfg'
materialsFile = inifile.find('EMC','MACHINE').lower() + '.mat'
materialsList = []
configDict = {}
dryRun = 0
torchPulse = 0
materialsUpdate = False
wLabels =\
    [fmonitor + '.aVlab',\
    fmonitor + '.lTlab',\
    fmonitor + '.lAOlab',\
    fmonitor + '.lFlab',\
    fmonitor + '.lBlab',\
    fmonitor + '.lSHlab',\
    fcutparms + '.pHlab',\
    fcutparms + '.pDlab',\
    fcutparms + '.pJHlab',\
    fcutparms + '.pJDlab',\
    fcutparms + '.cHlab',\
    fcutparms + '.cFRlab',\
    fcutparms + '.cAlab',\
    fcutparms + '.cVlab',\
    fthc + '.tElab',\
    fthc + '.tTlab',\
    fthc + '.pPGlab',\
    fthc + '.uAVlab',\
    fthc + '.lUlab',\
    fthc + '.lDlab',\
    fcornerlock + '.cElab',\
    fcornerlock + '.cTlab',\
    fcornerlock + '.lClab',\
    fkerflock + '.kElab',\
    fkerflock + '.kTlab',\
    fkerflock + '.lKlab',\
    fmotion + '.sHlab',\
    fmotion + '.pFRlab',\
    fmotion + '.fSTlab',\
    fmotion + '.sIDlab',\
    farc + '.aFDlab',\
    farc + '.aVSlab',\
    farc + '.aMSlab',\
    farc + '.aVOlab',\
    farc + '.aRDlab',\
    farc + '.aOHlab',\
    farc + '.tODlab',\
    farc + '.aOLlab',\
    foffsets + '.msplab',\
    foffsets + '.pIGlab',\
    foffsets + '.sFRlab',\
    foffsets + '.pDGlab',\
    ]
wCheckbuttons =\
    [fcornerlock + '.cornerlock-enable',\
    fkerflock + '.kerfcross-enable',\
    fthc + '.thc-enable',\
    fthc + '.use-auto-volts',\
    ]
wSpinboxes =\
    [fcutparms + '.pierce-height',\
    fcutparms + '.pierce-delay',\
    fcutparms + '.puddle-jump-height',\
    fcutparms + '.puddle-jump-delay',\
    fcutparms + '.cut-height',\
    fcutparms + '.cut-feed-rate',\
    fcutparms + '.cut-amps',\
    fcutparms + '.cut-volts',\
    fthc + '.thc-threshold',\
    fthc + '.pid-p-gain',\
    fcornerlock + '.cornerlock-threshold',\
    fkerflock + '.kerfcross-threshold',\
    fmotion + '.safe-height',\
    fmotion + '.float-switch-travel',\
    fmotion + '.probe-feed-rate',\
    fmotion + '.skip-ihs-distance',\
    farc + '.arc-fail-delay',\
    farc + '.arc-max-starts',\
    farc + '.restart-delay',\
    farc + '.torch-off-delay',\
    farc + '.arc-voltage-scale',\
    farc + '.arc-voltage-offset',\
    farc + '.arc-ok-high',\
    farc + '.arc-ok-low',\
    foffsets + '.setup-feed-rate',\
    foffsets + '.pid-i-gain',\
    foffsets + '.pid-d-gain',\
    ]
wScales =\
    [ftorch + '.torch-pulse-time',\
    foverride + '.height-override',\
    fpausedmotion + '.paused-motion-speed',\
    ]
wScalesConfig =\
    [ftorch + '.torch-pulse-time',\
    fpausedmotion + '.paused-motion-speed',\
    ]
wScalesHal =\
    [ftorch + '.torch-pulse-time',\
    foverride + '.height-override',\
    ]
wComboBoxes =\
    [fmaterial + '.materials',\
    ]
wLeds =\
    [fthc + '.led-up',\
    fthc + '.led-down',\
    fcornerlock + '.led-cornerlock',\
    fkerflock + '.led-kerfcross',\
    fmonitor + '.led-arc-ok',\
    fmonitor + '.led-torch',\
    fmonitor + '.led-float',\
    fmonitor + '.led-breakaway',\
    fmonitor + '.led-safe-height',\
    ]
configure_widgets()
load_settings()
check_materials_file()
get_materials()
for widget in wSpinboxes:
    w(widget,'configure','-wrap','1','-width',swidth,'-font',font,'-justify','r')
for widget in wLabels:
    w(widget,'configure','-anchor','w','-width',lwidth)
widgetValues={}
for widget in wSpinboxes + wScales:
        widgetValues[widget] = float(w(widget,'get'))
for widget in wCheckbuttons:
    tmp, item = widget.rsplit('.',1)
    widgetValues[widget] = int(w('set',item))
for widget in wLeds:
    w(widget,'configure','-state','disabled')
    widgetValues[widget] = 0
w(fmotion + '.probe-feed-rate','configure','-to',widgetValues[foffsets + '.setup-feed-rate'])
units = hal.get_value('halui.machine.units-per-mm')
maxPidP = thcFeedRate / units * 0.1
mode = inifile.find('PLASMAC','MODE') or '0'
set_mode(mode)
commands.set_view_z()



################################################################################
#   gets widget information
#   shows parent and child/children plus properties
#   uncomment any you need to look at, one or more at a time
#   lots more can be added...

my_widget = [\
#'.',\
#'.menu',\
#'.toolbar',\
#'.pane',\
#'.pane.top',\
#'.pane.top.tabs',\
#'.pane.top.tabs.c',\
#'.pane.top.tabs.fmanual',\
#'.pane.top.tabs.fmanual.space1',\
#'.pane.top.tabs.fmanual.axis',\
#'.pane.top.tabs.fmanual.axes',\
#'.pane.top.tabs.fmanual.spindlel',\
#'.pane.top.tabs.fmanual.spindlef',\
#'.pane.top.jogspeed',\
#'.pane.top.right',\
#'.pane.top.right.fpreview',\
#'.pane.top.right.fnumbers',\
#'.pane.top.right.fnumbers.text',\
#'.pane.bottom',\
#'.pane.bottom.t',\
#'.pane.bottom.t.text',\
]
for widget in my_widget:
    print '\n********** BEGIN',widget,'**********'
    print '\nwidget',widget,'is a',w('winfo','class',widget)
    print '\nmanager =',w('winfo','manager',widget)
    print '\nparent is:',w('winfo','parent',widget)
    print '\nchildren are:'
    for item in w('winfo','children',widget):
        print '  ',item,'which is managed by',w('winfo','manager',item)
    print '\nvalid options are:'
    for item in range (len(w(widget,'configure'))):
        print '  ',w(widget,'configure')[item]
    print '\n********** END',widget,'**********\n'
