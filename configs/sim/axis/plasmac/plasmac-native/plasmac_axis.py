''' set the window size, change pad_width and pad_height to suit your setup
    then uncomment the next 13 lines'''
#maxgeo=root_window.tk.call('wm','maxsize','.')
#if type(maxgeo) == tuple:
#    fullsize=str(maxgeo[0]),str(maxgeo[1])
#else:
#    fullsize=maxgeo.split(' ')[0],maxgeo.split(' ')[1]
#pad_width=60
#pad_height=60
#width=str(int(fullsize[0])-pad_width)
#height=str(int(fullsize[1])-pad_height)
#x=str(pad_width/2)
#y=str(pad_height/2)
#print '\nAxis window is', width, 'x', height, 'and starts at', x, 'x', y, '\n'
#root_window.tk.call('wm','geometry','.',width + 'x' + height + '+' + x + '+' + y)

# disable the 'do you want to close' dialog
root_window.tk.call('wm','protocol','.','WM_DELETE_WINDOW','destroy .')

# set the default font and the gcode font
font = inifile.find("PLASMAC","FONT") or 'sans 10'
fname = font.split()[0]
fsize = font.split()[1]
root_window.tk.call('font','configure','TkDefaultFont','-family', fname, '-size', fsize)
root_window.tk.call('.pane.bottom.t.text','configure','-height','10','-font', font, '-foreground','blue')

# redo the text in tabs so they resize for the new default font
root_window.tk.call('.pane.top.tabs','itemconfigure','manual','-text',' Manual - F3 ')
root_window.tk.call('.pane.top.tabs','itemconfigure','mdi','-text',' MDI - F5 ')
root_window.tk.call('.pane.top.right','itemconfigure','preview','-text',' Preview ')
root_window.tk.call('.pane.top.right','itemconfigure','numbers','-text',' DRO ')

# hide some original widgets
fmanual = '.pane.top.tabs.fmanual'
root_window.tk.call('pack','forget','.toolbar.rule0')
root_window.tk.call('pack','forget','.toolbar.rule4')
root_window.tk.call('pack','forget','.toolbar.rule8')
root_window.tk.call('pack','forget','.toolbar.rule9')
root_window.tk.call('grid','forget',fmanual + '.axis')
root_window.tk.call('grid','forget',fmanual + '.jogf')
#root_window.tk.call('grid','forget',fmanual + '.jogf.zerohome.tooltouch')
root_window.tk.call('grid','forget',fmanual + '.space2')
root_window.tk.call('grid','forget',fmanual + '.spindlel')
root_window.tk.call('grid','forget',fmanual + '.spindlef')
root_window.tk.call('grid','forget',fmanual + '.space2')
root_window.tk.call('grid','forget',fmanual + '.coolant')
root_window.tk.call('grid','forget',fmanual + '.mist')
root_window.tk.call('grid','forget',fmanual + '.flood')
root_window.tk.call('grid','forget','.pane.top.spinoverride')

# change layout for some scales
root_window.tk.call('pack','forget','.pane.top.jogspeed.l0')
root_window.tk.call('pack','forget','.pane.top.jogspeed.l')
root_window.tk.call('pack','forget','.pane.top.jogspeed.l1')
root_window.tk.call('pack','forget','.pane.top.jogspeed.s')
root_window.tk.call('pack','forget','.pane.top.maxvel.l0')
root_window.tk.call('pack','forget','.pane.top.maxvel.l')
root_window.tk.call('pack','forget','.pane.top.maxvel.l1')
root_window.tk.call('pack','forget','.pane.top.maxvel.s')
root_window.tk.call('pack','.pane.top.jogspeed.s','-side','right')
root_window.tk.call('pack','.pane.top.jogspeed.l1','-side','right')
root_window.tk.call('pack','.pane.top.jogspeed.l','-side','right')
root_window.tk.call('pack','.pane.top.jogspeed.l0','-side','left')
root_window.tk.call('pack','.pane.top.maxvel.s','-side','right')
root_window.tk.call('pack','.pane.top.maxvel.l1','-side','right')
root_window.tk.call('pack','.pane.top.maxvel.l','-side','right')
root_window.tk.call('pack','.pane.top.maxvel.l0','-side','left')

# modify the toolbar
root_window.tk.call('label','.toolbar.space1','-width','5')
root_window.tk.call('label','.toolbar.space2','-width','5')
root_window.tk.call('label','.toolbar.space3','-width','5')
root_window.tk.call('label','.toolbar.space4','-width','10')
root_window.tk.call('pack','.toolbar.space1','-after','.toolbar.machine_power','-side','left')
root_window.tk.call('pack','.toolbar.space2','-after','.toolbar.reload','-side','left')
root_window.tk.call('pack','.toolbar.space3','-after','.toolbar.program_stop','-side','left')
root_window.tk.call('pack','.toolbar.space4','-after','.toolbar.program_optpause','-side','left')


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

# some names to save fingers
faxes = fmanual + '.axes'
fjoints = fmanual + '.joints'
fjogf = fmanual + '.jogf'
ftorch = fmanual + '.torch'
foverride = fmanual + '.override'
fpausedmotion = fmanual + '.pausedmotion'
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

# rework the axis/joints frame
root_window.tk.call('destroy',faxes)
root_window.tk.call('labelframe',faxes,'-text','Axis:','-relief','ridge')
root_window.tk.call('destroy',fjoints)
root_window.tk.call('labelframe',fjoints,'-text','Joint:','-relief','ridge')
# make axis radiobuttons
for letter in 'xyzabcuvw':
    root_window.tk.call('radiobutton',faxes + '.axis' + letter,\
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
            root_window.tk.call('grid',faxes + '.axis' + letters[count],'-row',row,'-column',column,'-padx','4')
        count += 1
        if count == 9: break
# make joints radiobuttons
for number in range(0,linuxcnc.MAX_JOINTS):
    root_window.tk.call('radiobutton',fjoints + '.joint' + str(number),\
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
        root_window.tk.call('grid',fjoints + '.joint' + str(count),'-row',row,'-column',column,'-padx','4')
        count += 1

# rework the jogf frame
root_window.tk.call('destroy',fjogf)
root_window.tk.call('labelframe',fjogf,'-relief','flat','-bd','0')
root_window.tk.call('labelframe',fjogf + '.jog','-text','Jog','-relief','ridge')
root_window.tk.call('button',fjogf + '.jog.jogminus','-command','if ![is_continuous] {jog_minus 1}','-height','1','-text','-')
root_window.tk.call('bind',fjogf + '.jog.jogminus','<Button-1>','if [is_continuous] {jog_minus}')
root_window.tk.call('bind',fjogf + '.jog.jogminus','<ButtonRelease-1>','if [is_continuous] {jog_stop}')
root_window.tk.call('button',fjogf + '.jog.jogplus','-command','if ![is_continuous] {jog_plus 1}','-height','1','-text','+')
root_window.tk.call('bind',fjogf + '.jog.jogplus','<Button-1>','if [is_continuous] {jog_plus}')
root_window.tk.call('bind',fjogf + '.jog.jogplus','<ButtonRelease-1>','if [is_continuous] {jog_stop}')
root_window.tk.call('combobox',fjogf + '.jog.jogincr','-editable','0','-textvariable','jogincrement','-value','Continuous','-width','10')
root_window.tk.call(fjogf + '.jog.jogincr','list','insert','end','Continuous',0.1000,0.0100,0.0010,0.0001)
root_window.tk.call('labelframe',fjogf + '.zerohome','-text','Zero','-relief','ridge')
root_window.tk.call('button',fjogf + '.zerohome.home','-command','home_joint','-height','1')
root_window.tk.call('setup_widget_accel',fjogf + '.zerohome.home','Home Axis')
root_window.tk.call('button',fjogf + '.zerohome.zero','-command','touch_off_system','-height','1')
root_window.tk.call('setup_widget_accel',fjogf + '.zerohome.zero','Touch Off')
# unused, just for tcl hierarchy
root_window.tk.call('button',fjogf + '.zerohome.tooltouch')
root_window.tk.call('checkbutton',fjogf + '.override')
# populate the jog frame
root_window.tk.call('grid',fjogf + '.jog.jogminus','-row','0','-column','0','-padx','0 3','-sticky','nsew')
root_window.tk.call('grid',fjogf + '.jog.jogplus','-row','0','-column','1','-padx','3 3','-sticky','nsew')
root_window.tk.call('grid',fjogf + '.jog.jogincr','-row','0','-column','2','-padx','3 0','-sticky','nsew')
root_window.tk.call('grid',fjogf + '.jog','-row','0','-column','0','-sticky','ew')
root_window.tk.call('grid',fjogf + '.zerohome.home','-row','0','-column','0','-padx','0 3','-sticky','ew')
root_window.tk.call('grid',fjogf + '.zerohome.zero','-row','0','-column','1','-padx','3 0','-sticky','ew')
root_window.tk.call('grid',fjogf + '.zerohome','-row','1','-column','0','-pady','4 0','-sticky','ew')
root_window.tk.call('grid',fjogf,'-column','0','-row','1','-padx','4','-pady','4 0','-sticky','ew')
root_window.tk.call('grid','columnconfigure',fmanual,'0','-weight','1')
root_window.tk.call('grid','columnconfigure',fjogf,'0','-weight','1')
root_window.tk.call('grid','columnconfigure',fjogf + '.jog','0 1 2','-weight','1')
root_window.tk.call('grid','columnconfigure',fjogf + '.zerohome','0 1','-weight','1')
if homing_order_defined:
    widgets.homebutton.configure(text=_('Home All'), command='home_all_joints')
    root_window.tk.call('DynamicHelp::add', widgets.homebutton,'-text', _('Home all %ss [Ctrl-Home]') % ja_name)

# torch frame
root_window.tk.call('labelframe',ftorch,'-text','Torch:','-relief','ridge')
root_window.tk.call('Button', ftorch + '.torch-button','-command','torch_pulse','-text','PULSE','-takefocus','0','-width','3')
root_window.tk.call('append','manualgroup',' ' + ftorch + '.torch-button')
root_window.tk.call('scale', ftorch + '.torch-pulse-time','-orient','horizontal','-variable','torchPulse','-showvalue','0')
root_window.tk.call('label', ftorch + '.torch-time','-textvariable','torchPulse','-width','3','-anchor','e')
root_window.tk.call('label', ftorch + '.torch-label','-text','Sec','-anchor','e')
root_window.tk.call('pack', ftorch + '.torch-button','-side','left','-pady','2')
root_window.tk.call('pack', ftorch + '.torch-pulse-time','-side','left','-fill','x','-expand','1')
root_window.tk.call('pack', ftorch + '.torch-label','-side','right')
root_window.tk.call('pack', ftorch + '.torch-time','-side','right')
root_window.tk.call('grid',ftorch,'-column','0','-row','2','-columnspan','1','-padx','4','-pady','4 0','-sticky','ew')

# override frame
root_window.tk.call('labelframe',foverride,'-text','Height Override:','-relief','ridge')
root_window.tk.call('scale',foverride + '.height-override','-orient','horizontal')
root_window.tk.call('pack',foverride + '.height-override','-fill','x','-expand','1')
root_window.tk.call('grid',foverride,'-column','0','-row','3','-columnspan','1','-padx','4','-pady','4 0','-sticky','ew')

# paused motion frame
root_window.tk.call('labelframe',fpausedmotion,'-text','Paused Motion Speed:','-relief','ridge')
root_window.tk.call('scale',fpausedmotion + '.paused-motion-speed','-orient','horizontal')
root_window.tk.call('pack',fpausedmotion + '.paused-motion-speed','-fill','x')
root_window.tk.call('grid',fpausedmotion,'-column','0','-row','4','-columnspan','1','-padx','4','-pady','4 0','-sticky','ew')

# bottom pane - hide until modified
root_window.tk.call('pack','forget','.pane.bottom.t.text')
root_window.tk.call('pack','forget','.pane.bottom.t.sb')

# common frame
common = '.pane.bottom.t.common'
root_window.tk.call('labelframe',common,'-text','','-relief','raised')

# monitor frame
root_window.tk.call('labelframe',fmonitor,'-text','','-relief','flat')
arcfont = fname + ' ' + str(int(fsize) + 2) + ' bold'
root_window.tk.call('label',fmonitor + '.arc-voltage','-anchor','e','-width',swidth,'-fg','blue','-font',arcfont)
root_window.tk.call('label',fmonitor + '.aVlab','-text','Arc Voltage')
root_window.tk.call('canvas',fmonitor + '.led-float','-width',cwidth,'-height',cheight)
root_window.tk.call(fmonitor + '.led-float','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',fmonitor + '.lFlab','-text','Float Switch')
root_window.tk.call('canvas',fmonitor + '.led-torch','-width',cwidth,'-height',cheight)
root_window.tk.call(fmonitor + '.led-torch','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','orange','-disabledfill','grey')
root_window.tk.call('label',fmonitor + '.lTlab','-text','Torch On')
root_window.tk.call('canvas',fmonitor + '.led-breakaway','-width',cwidth,'-height',cheight)
root_window.tk.call(fmonitor + '.led-breakaway','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',fmonitor + '.lBlab','-text','Breakaway')
root_window.tk.call('canvas',fmonitor + '.led-arc-ok','-width',cwidth,'-height',cheight)
root_window.tk.call(fmonitor + '.led-arc-ok','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','lightgreen','-disabledfill','grey')
root_window.tk.call('label',fmonitor + '.lAOlab','-text','Ark OK')
root_window.tk.call('canvas',fmonitor + '.led-safe-height','-width',cwidth,'-height',cheight)
root_window.tk.call(fmonitor + '.led-safe-height','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',fmonitor + '.lSHlab','-text','Safe Limited')
root_window.tk.call('grid',fmonitor + '.arc-voltage','-row','0','-column','0','-sticky','e')
root_window.tk.call('grid',fmonitor + '.aVlab','-row','0','-column','1',)
root_window.tk.call('grid',fmonitor + '.led-float','-row','1','-column','0','-sticky','e')
root_window.tk.call('grid',fmonitor + '.lFlab','-row','1','-column','1')
root_window.tk.call('grid',fmonitor + '.led-torch','-row','2','-column','0','-sticky','e')
root_window.tk.call('grid',fmonitor + '.lTlab','-row','2','-column','1')
root_window.tk.call('grid',fmonitor + '.led-breakaway','-row','3','-column','0','-sticky','e')
root_window.tk.call('grid',fmonitor + '.lBlab','-row','3','-column','1')
root_window.tk.call('grid',fmonitor + '.led-arc-ok','-row','4','-column','0','-sticky','e')
root_window.tk.call('grid',fmonitor + '.lAOlab','-row','4','-column','1')
root_window.tk.call('grid',fmonitor + '.led-safe-height','-row','5','-column','0','-sticky','e')
root_window.tk.call('grid',fmonitor + '.lSHlab','-row','5','-column','1')
root_window.tk.call('grid','rowconfigure',fmonitor,'0 1 2 3 4 5','-pad','4')

# buttons frame
root_window.tk.call('labelframe',fbuttons,'-relief','flat')
root_window.tk.call('button',fbuttons + '.xtohome','-text','X to Home','-command','x_to_home','-width',bwidth)
root_window.tk.call('button',fbuttons + '.ytohome','-text','Y to Home','-command','y_to_home','-width',bwidth)
root_window.tk.call('button',fbuttons + '.ztohome','-text','Z to Home','-command','z_to_home','-width',bwidth)
root_window.tk.call('button',fbuttons + '.dryRun','-text','Dry Run','-command','dry_run','-width',bwidth)
root_window.tk.call('grid',fbuttons + '.xtohome','-row','0','-column','0')
root_window.tk.call('grid',fbuttons + '.ytohome','-row','1','-column','0')
root_window.tk.call('grid',fbuttons + '.ztohome','-row','2','-column','0')
root_window.tk.call('grid',fbuttons + '.dryRun','-row','3','-column','0')
root_window.tk.call('grid','columnconfigure',fbuttons,0,'-weight','1')

# populate bottom frame
root_window.tk.call('pack',fmonitor,'-fill','y','-side','left')
root_window.tk.call('pack',fbuttons,'-fill','y','-side','left')
root_window.tk.call('.pane.bottom.t','configure','-relief','flat')
root_window.tk.call('.pane.bottom.t.text','configure','-borderwidth','2','-relief','sunken')
root_window.tk.call('pack',common,'-fill','y','-side','left')
root_window.tk.call('pack','.pane.bottom.t.text','-fill','both','-expand','1','-side','left','-padx','4','-pady','0')
root_window.tk.call('pack','.pane.bottom.t.sb','-fill','y','-side','left')

# new notebook for plasmac stuff
root_window.tk.call('NoteBook','.plasmac','-borderwidth','2','-arcradius','3')
root_window.tk.call('.plasmac','insert','end','run','-text','Run')
root_window.tk.call('.plasmac','insert','end','config','-text','Configure')

# frames for run tab
root_window.tk.call('labelframe',fmaterial,'-text','Material','-relief','ridge')
root_window.tk.call('labelframe',fcutparms,'-text','Cut Parameters','-relief','ridge')
root_window.tk.call('labelframe',fthc,'-text','THC','-relief','ridge')
root_window.tk.call('labelframe',flocks,'-text','Locks','-relief','ridge')

# frames for config tab
root_window.tk.call('labelframe',fmotion,'-text','Motion','-relief','ridge')
root_window.tk.call('labelframe',farc,'-text','Arc','-relief','ridge')
root_window.tk.call('labelframe',foffsets,'-text','Offsets','-relief','ridge')
root_window.tk.call('labelframe',fsettings,'-text','Settings','-relief','ridge')

# material frame
root_window.tk.call('ComboBox',fmaterial + '.materials','-modifycmd','material_changed')
root_window.tk.call('DynamicHelp::add',fmaterial + '.materials','-text','select material from materials file')
root_window.tk.call('pack',fmaterial + '.materials','-fill','x')

# cut parameters frame
root_window.tk.call('spinbox',fcutparms + '.pierce-height')
root_window.tk.call('DynamicHelp::add',fcutparms + '.pierce-height','-text','piercing height\nin machine units')
root_window.tk.call('label',fcutparms + '.pHlab','-text','Pierce Height')
root_window.tk.call('spinbox',fcutparms + '.pierce-delay')
root_window.tk.call('label',fcutparms + '.pDlab','-text','Pierce Delay')
root_window.tk.call('spinbox',fcutparms + '.cut-height')
root_window.tk.call('label',fcutparms + '.cHlab','-text','Cut Height')
root_window.tk.call('spinbox',fcutparms + '.cut-feed-rate')
root_window.tk.call('label',fcutparms + '.cFRlab','-text','Cut Feed Rate')
root_window.tk.call('spinbox',fcutparms + '.puddle-jump-height')
root_window.tk.call('label',fcutparms + '.pJHlab','-text','P-J Height')
root_window.tk.call('spinbox',fcutparms + '.puddle-jump-delay')
root_window.tk.call('label',fcutparms + '.pJDlab','-text','P-J Delay')
root_window.tk.call('spinbox',fcutparms + '.cut-amps')
root_window.tk.call('label',fcutparms + '.cAlab','-text','Cut Amps')
root_window.tk.call('spinbox',fcutparms + '.cut-volts')
root_window.tk.call('label',fcutparms + '.cVlab','-text','Cut Volts')
root_window.tk.call('grid',fcutparms + '.pierce-height','-row','0','-column','0')
root_window.tk.call('grid',fcutparms + '.pHlab','-row','0','-column','1')
root_window.tk.call('grid',fcutparms + '.pierce-delay','-row','1','-column','0')
root_window.tk.call('grid',fcutparms + '.pDlab','-row','1','-column','1')
root_window.tk.call('grid',fcutparms + '.cut-height','-row','2','-column','0')
root_window.tk.call('grid',fcutparms + '.cHlab','-row','2','-column','1')
root_window.tk.call('grid',fcutparms + '.cut-feed-rate','-row','3','-column','0')
root_window.tk.call('grid',fcutparms + '.cFRlab','-row','3','-column','1')
root_window.tk.call('grid',fcutparms + '.puddle-jump-height','-row','4','-column','0')
root_window.tk.call('grid',fcutparms + '.pJHlab','-row','4','-column','1')
root_window.tk.call('grid',fcutparms + '.puddle-jump-delay','-row','5','-column','0')
root_window.tk.call('grid',fcutparms + '.pJDlab','-row','5','-column','1')
root_window.tk.call('grid',fcutparms + '.cut-amps','-row','6','-column','0')
root_window.tk.call('grid',fcutparms + '.cAlab','-row','6','-column','1')
root_window.tk.call('grid',fcutparms + '.cut-volts','-row','7','-column','0')
root_window.tk.call('grid',fcutparms + '.cVlab','-row','7','-column','1')
root_window.tk.call('grid','rowconfigure',fcutparms,'0 1 2 3 4 5 6 7','-pad','2')
root_window.tk.call('grid','columnconfigure',fcutparms,'0 1 2 3','-weight','1')

# thc frame
root_window.tk.call('checkbutton',fthc + '.thc-enable')
root_window.tk.call('label',fthc + '.tElab','-text','Enable')
root_window.tk.call('checkbutton',fthc + '.use-auto-volts')
root_window.tk.call('label',fthc + '.uAVlab','-text','Use Auto Volts')
root_window.tk.call('spinbox',fthc + '.thc-threshold')
root_window.tk.call('label',fthc + '.tTlab','-text','Threshold')
root_window.tk.call('spinbox',fthc + '.pid-p-gain')
root_window.tk.call('label',fthc + '.pPGlab','-text','Speed (PIDP)')
root_window.tk.call('canvas',fthc + '.led-up','-width',cwidth,'-height',cheight)
root_window.tk.call(fthc + '.led-up','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','yellow','-disabledfill','grey')
root_window.tk.call('label',fthc + '.lUlab','-text','Move Up')
root_window.tk.call('canvas',fthc + '.led-down','-width',cwidth,'-height',cheight)
root_window.tk.call(fthc + '.led-down','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','yellow','-disabledfill','grey')
root_window.tk.call('label',fthc + '.lDlab','-text','Move Down')
root_window.tk.call('grid',fthc + '.thc-enable','-row','0','-column','0')
root_window.tk.call('grid',fthc + '.tElab','-row','0','-column','1')
root_window.tk.call('grid',fthc + '.use-auto-volts','-row','1','-column','0')
root_window.tk.call('grid',fthc + '.uAVlab','-row','1','-column','1')
root_window.tk.call('grid',fthc + '.thc-threshold','-row','2','-column','0')
root_window.tk.call('grid',fthc + '.tTlab','-row','2','-column','1')
root_window.tk.call('grid',fthc + '.pid-p-gain','-row','3','-column','0')
root_window.tk.call('grid',fthc + '.pPGlab','-row','3','-column','1')
root_window.tk.call('grid',fthc + '.led-up','-row','4','-column','0')
root_window.tk.call('grid',fthc + '.lUlab','-row','4','-column','1')
root_window.tk.call('grid',fthc + '.led-down','-row','5','-column','0')
root_window.tk.call('grid',fthc + '.lDlab','-row','5','-column','1')
root_window.tk.call('grid','rowconfigure',fthc,'2 3','-pad','2')
root_window.tk.call('grid','columnconfigure',fthc,'0 1 2 3','-weight','1')

# locks frame
root_window.tk.call('labelframe',fcornerlock,'-text','Corner','-relief','sunken')
root_window.tk.call('checkbutton',fcornerlock + '.cornerlock-enable')
root_window.tk.call('label',fcornerlock + '.cElab','-text','Enable')
root_window.tk.call('spinbox',fcornerlock + '.cornerlock-threshold')
root_window.tk.call('label',fcornerlock + '.cTlab','-text','Threshold(%)')
root_window.tk.call('canvas',fcornerlock + '.led-cornerlock','-width',cwidth,'-height',cheight)
root_window.tk.call(fcornerlock + '.led-cornerlock','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',fcornerlock + '.lClab','-text','Locked(%)')
root_window.tk.call('labelframe',fkerflock,'-text','Kerf','-relief','sunken')
root_window.tk.call('checkbutton',fkerflock + '.kerfcross-enable')
root_window.tk.call('label',fkerflock + '.kElab','-text','Enable')
root_window.tk.call('spinbox',fkerflock + '.kerfcross-threshold')
root_window.tk.call('label',fkerflock + '.kTlab','-text','Threshold(V)')
root_window.tk.call('canvas',fkerflock + '.led-kerfcross','-width',cwidth,'-height',cheight)
root_window.tk.call(fkerflock + '.led-kerfcross','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',fkerflock + '.lKlab','-text','Locked(%)')
root_window.tk.call('grid',fcornerlock + '.cornerlock-enable','-row','0','-column','0')
root_window.tk.call('grid',fcornerlock + '.cElab','-row','0','-column','1')
root_window.tk.call('grid',fcornerlock + '.cornerlock-threshold','-row','1','-column','0')
root_window.tk.call('grid',fcornerlock + '.cTlab','-row','1','-column','1')
root_window.tk.call('grid',fcornerlock + '.led-cornerlock','-row','2','-column','0')
root_window.tk.call('grid',fcornerlock + '.lClab','-row','2','-column','1')
root_window.tk.call('grid',fkerflock + '.kerfcross-enable','-row','0','-column','0')
root_window.tk.call('grid',fkerflock + '.kElab','-row','0','-column','1')
root_window.tk.call('grid',fkerflock + '.kerfcross-threshold','-row','1','-column','0')
root_window.tk.call('grid',fkerflock + '.kTlab','-row','1','-column','1')
root_window.tk.call('grid',fkerflock + '.led-kerfcross','-row','2','-column','0')
root_window.tk.call('grid',fkerflock + '.lKlab','-row','2','-column','1')
root_window.tk.call('pack',fcornerlock,'-side','top','-padx','1','-pady','2','-fill','x')
root_window.tk.call('pack',fkerflock,'-side','top','-padx','1','-pady','2','-fill','x')
root_window.tk.call('grid','rowconfigure',fcornerlock,'1','-pad','2')
root_window.tk.call('grid','rowconfigure',fkerflock,'1','-pad','2')
root_window.tk.call('grid','columnconfigure',flocks,'0','-weight','1')

# motion frame
root_window.tk.call('spinbox',fmotion + '.safe-height')
root_window.tk.call('label',fmotion + '.sHlab','-text','Safe Height')
root_window.tk.call('spinbox',fmotion + '.float-switch-travel')
root_window.tk.call('label',fmotion + '.fSTlab','-text','Float Travel')
root_window.tk.call('spinbox',fmotion + '.probe-feed-rate')
root_window.tk.call('label',fmotion + '.pFRlab','-text','Probe Speed')
root_window.tk.call('spinbox',fmotion + '.skip-ihs-distance','-from','0','-to','20')
root_window.tk.call('label',fmotion + '.sIDlab','-text','Skip IHS')
root_window.tk.call('grid',fmotion + '.safe-height','-row','0','-column','0')
root_window.tk.call('grid',fmotion + '.sHlab','-row','0','-column','1')
root_window.tk.call('grid',fmotion + '.float-switch-travel','-row','1','-column','0')
root_window.tk.call('grid',fmotion + '.fSTlab','-row','1','-column','1')
root_window.tk.call('grid',fmotion + '.probe-feed-rate','-row','2','-column','0')
root_window.tk.call('grid',fmotion + '.pFRlab','-row','2','-column','1')
root_window.tk.call('grid',fmotion + '.skip-ihs-distance','-row','3','-column','0')
root_window.tk.call('grid',fmotion + '.sIDlab','-row','3','-column','1')
root_window.tk.call('grid','rowconfigure',fmotion,'0 1 2 3','-pad','2')
root_window.tk.call('grid','columnconfigure',fmotion,'0 1 2 3','-weight','1')

# arc frame
root_window.tk.call('spinbox',farc + '.arc-fail-delay')
root_window.tk.call('label',farc + '.aFDlab','-text','Fail Timeout')
root_window.tk.call('spinbox',farc + '.arc-max-starts')
root_window.tk.call('label',farc + '.aMSlab','-text','Max. Starts')
root_window.tk.call('spinbox',farc + '.restart-delay')
root_window.tk.call('label',farc + '.aRDlab','-text','Retry Delay')
root_window.tk.call('spinbox',farc + '.torch-off-delay')
root_window.tk.call('label',farc + '.tODlab','-text','Off Delay')
root_window.tk.call('spinbox',farc + '.arc-voltage-scale')
root_window.tk.call('label',farc + '.aVSlab','-text','Voltage Scale')
root_window.tk.call('spinbox',farc + '.arc-voltage-offset')
root_window.tk.call('label',farc + '.aVOlab','-text','Voltage Offset')
root_window.tk.call('spinbox',farc + '.arc-ok-high')
root_window.tk.call('label',farc + '.aOHlab','-text','OK High Volts')
root_window.tk.call('spinbox',farc + '.arc-ok-low')
root_window.tk.call('label',farc + '.aOLlab','-text','OK Low Volts')
root_window.tk.call('grid',farc + '.arc-fail-delay','-row','0','-column','0')
root_window.tk.call('grid',farc + '.aFDlab','-row','0','-column','1')
root_window.tk.call('grid',farc + '.arc-max-starts','-row','1','-column','0')
root_window.tk.call('grid',farc + '.aMSlab','-row','1','-column','1')
root_window.tk.call('grid',farc + '.restart-delay','-row','2','-column','0')
root_window.tk.call('grid',farc + '.aRDlab','-row','2','-column','1')
root_window.tk.call('grid',farc + '.torch-off-delay','-row','3','-column','0')
root_window.tk.call('grid',farc + '.tODlab','-row','3','-column','1')
root_window.tk.call('grid',farc + '.arc-voltage-scale','-row','4','-column','0')
root_window.tk.call('grid',farc + '.aVSlab','-row','4','-column','1')
root_window.tk.call('grid',farc + '.arc-voltage-offset','-row','5','-column','0')
root_window.tk.call('grid',farc + '.aVOlab','-row','5','-column','1')
root_window.tk.call('grid',farc + '.arc-ok-high','-row','6','-column','0')
root_window.tk.call('grid',farc + '.aOHlab','-row','6','-column','1')
root_window.tk.call('grid',farc + '.arc-ok-low','-row','7','-column','0')
root_window.tk.call('grid',farc + '.aOLlab','-row','7','-column','1')
root_window.tk.call('grid','rowconfigure',farc,'0 1 2 3 4 5 6 7','-pad','2')
root_window.tk.call('grid','columnconfigure',farc,'0 1 2 3','-weight','1')

# offsets frame
root_window.tk.call('label',foffsets + '.maxspeed','-text','0','-anchor','e','-width',swidth)
root_window.tk.call('label',foffsets + '.msplab','-text','Max. Speed')
root_window.tk.call('spinbox',foffsets + '.setup-feed-rate')
root_window.tk.call('label',foffsets + '.sFRlab','-text','Setup Speed')
root_window.tk.call('spinbox',foffsets + '.pid-i-gain')
root_window.tk.call('label',foffsets + '.pIGlab','-text','PID I Gain')
root_window.tk.call('spinbox',foffsets + '.pid-d-gain','-from','0','-to','20')
root_window.tk.call('label',foffsets + '.pDGlab','-text','PID D Gain')
root_window.tk.call('grid',foffsets + '.maxspeed','-row','0','-column','0')
root_window.tk.call('grid',foffsets + '.msplab','-row','0','-column','1')
root_window.tk.call('grid',foffsets + '.setup-feed-rate','-row','1','-column','0')
root_window.tk.call('grid',foffsets + '.sFRlab','-row','1','-column','1')
root_window.tk.call('grid',foffsets + '.pid-i-gain','-row','2','-column','0')
root_window.tk.call('grid',foffsets + '.pIGlab','-row','2','-column','1')
root_window.tk.call('grid',foffsets + '.pid-d-gain','-row','3','-column','0')
root_window.tk.call('grid',foffsets + '.pDGlab','-row','3','-column','1')
root_window.tk.call('grid','rowconfigure',foffsets,'0 1 2 3','-pad','2')
root_window.tk.call('grid','columnconfigure',foffsets,'0 1 2 3','-weight','1')

# settings frame
root_window.tk.call('button',fsettings + '.save','-text','Save','-command','save_config','-width',bwidth)
root_window.tk.call('button',fsettings + '.reload','-text','Reload','-width',bwidth,'-command','reload_config')
root_window.tk.call('grid',fsettings + '.save','-row','0','-column','0')
root_window.tk.call('grid',fsettings + '.reload','-row','0','-column','1')
root_window.tk.call('grid','columnconfigure',fsettings,'0 1','-weight','1','-pad','2')

# populate run tab
root_window.tk.call('pack',fmaterial,'-fill','x')
root_window.tk.call('pack',fcutparms,'-fill','x')
root_window.tk.call('pack',fthc,'-fill','x')
root_window.tk.call('pack',flocks,'-fill','x')

# populate config tab
root_window.tk.call('pack',fmotion,'-fill','x','-expand','0')
root_window.tk.call('pack',farc,'-fill','x','-expand','0')
root_window.tk.call('pack',foffsets,'-fill','x','-expand','0')
root_window.tk.call('pack',fsettings,'-fill','x','-expand','0')

# move original pane to right
root_window.tk.call('grid','.pane','-column','1','-row','1','-sticky','nsew','-rowspan','2')

# place new notebook left of original pane
root_window.tk.call('.plasmac','raise','run')
root_window.tk.call('grid','.plasmac','-column','0','-row','1','-sticky','nsew','-rowspan','2')
root_window.tk.call('grid','columnconfigure','.','0','-weight','0')
root_window.tk.call('grid','columnconfigure','.','1','-weight','1')

# some new commands for TCL
def material_changed():
    if not materialsUpdate:
        newmaterial = root_window.tk.call(fmaterial + '.materials','getvalue')
        root_window.tk.call(fcutparms + '.pierce-height','set',materialsList[newmaterial][1])
        root_window.tk.call(fcutparms + '.pierce-delay','set',materialsList[newmaterial][2])
        root_window.tk.call(fcutparms + '.puddle-jump-height','set',materialsList[newmaterial][3])
        root_window.tk.call(fcutparms + '.puddle-jump-delay','set',materialsList[newmaterial][4])
        root_window.tk.call(fcutparms + '.cut-height','set',materialsList[newmaterial][5])
        root_window.tk.call(fcutparms + '.cut-feed-rate','set',materialsList[newmaterial][6])
        root_window.tk.call(fcutparms + '.cut-amps','set',materialsList[newmaterial][7])
        root_window.tk.call(fcutparms + '.cut-volts','set',materialsList[newmaterial][8])

def save_config():
    try:
        with open(configFile, 'w') as f_out:
            f_out.write('#plasmac configuration file, format is:\n#name = value\n\n')
            for key in sorted(configDict.iterkeys()):
                for widget in wCheckbuttons + wSpinboxes + wScalesSaved:
                    if widget.endswith(key):
                        if widget in wCheckbuttons:
                            value = root_window.tk.call('set',key)
                            f_out.write(key + ' = ' + str(value) + '\n')
                            break
                        elif widget in wSpinboxes + wScalesSaved:
                            value = root_window.tk.call(widget,'get')
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
    root_window.tk.call(fmaterial + '.materials','configure','-values','')
    get_materials()
    materialsUpdate = False

def x_to_home():
    goto_home('X')

def y_to_home():
    goto_home('Y')

def z_to_home():
    goto_home('Z')

def dry_run():
    if hal.get_value('halui.program.is-idle'):
        hal.set_p('plasmac.dry-run-start','1')
        global dryRun
        dryRun = 1

def torch_pulse():
    if hal.get_value('halui.program.is-idle'):
        hal.set_p('plasmac.torch-pulse-start','1')
        global torchPulse
        torchPulse = 1

def wait_for_completion():
    pass
    while c.wait_complete() == -1:
        pass

def goto_home(axis):
    if hal.get_value('halui.program.is-idle'):
        home = inifile.find('JOINT_' + str(inifile.find('TRAJ','COORDINATES').upper().index(axis)), 'HOME')
        if not hal.get_value('halui.mode.is-mdi'):
            c.mode(linuxcnc.MODE_MDI)
            wait_for_completion()
        c.mdi('G53 G0 ' + axis + home)

def joint_mode_switch(a,b,c):
    if vars.motion_mode.get() == linuxcnc.TRAJ_MODE_FREE and s.kinematics_type != linuxcnc.KINEMATICS_IDENTITY:
        root_window.tk.call('grid','forget',fmanual + '.axes')
        root_window.tk.call('grid',fmanual + '.joints','-column','0','-row','0','-padx','4','-pady','0','-sticky','ew')
        widget = getattr(widgets, "joint_%d" % 0)
        widget.focus()
        vars.ja_rbutton.set(0)
    else:
        root_window.tk.call('grid','forget',fmanual + '.joints')
        root_window.tk.call('grid',fmanual + '.axes','-column','0','-row','0','-padx','4','-pady','0','-sticky','ew')
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
TclCommands.joint_mode_switch = joint_mode_switch
TclCommands.ja_button_activated = ja_button_activated
commands = TclCommands(root_window)

# some python functions

# original in axis.py line 3000
def user_live_update():
    for widget in wSpinboxes + wScalesSaved + wScalesVolatile:
        tmp, item = widget.rsplit('.',1)
        if item != 'cut-amps':
            value = float(root_window.tk.call(widget,'get'))
            if value != widgetValues[widget]:
                widgetValues[widget] = value
                if item == 'arc-max-starts':
                    hal.set_p('plasmac.%s' % (item),'%d' % (value))
                else:
                    hal.set_p('plasmac.%s' % (item),'%f' % (value))
                if item == 'setup-feed-rate': #limit max probe feed rate to setup feed rate
                    root_window.tk.call(fmotion + '.probe-feed-rate','configure','-to',value)
    for widget in wCheckbuttons:
        tmp, item = widget.rsplit('.',1)
        value = int(root_window.tk.call('set',item))
        if value != widgetValues[widget]:
            widgetValues[widget] = value
            hal.set_p('plasmac.%s' % (item),'%d' % (value))
    for widget in wLeds:
        tmp, item = widget.rsplit('.',1)
        if pcomp[item] != widgetValues[widget]:
            widgetValues[widget] = pcomp[item]
            if pcomp[item] == 1:
                root_window.tk.call(widget,'configure','-state','normal')
            else:
                root_window.tk.call(widget,'configure','-state','disabled')
    root_window.tk.call(fmonitor + '.arc-voltage','configure','-text','%0.1f' % (pcomp['arc-voltage']))
    global dryRun
    if dryRun == 1:
        if hal.get_value('halui.program.is-running'):
            hal.set_p('plasmac.dry-run-start','0')
            dryRun = 0
    global torchPulse
    if torchPulse == 1:
        if hal.get_value('plasmac.torch-on'):
            hal.set_p('plasmac.torch-pulse-start','0')
            torchPulse = 0
    if hal.get_value('plasmac-panel.config-disable'):
        root_window.tk.call('.plasmac','itemconfigure','config','-state','disabled')
    else:
        root_window.tk.call('.plasmac','itemconfigure','config','-state','normal')

def configure_widgets():
    root_window.tk.call(ftorch + '.torch-pulse-time','configure','-from','0','-to','3','-resolution','0.1')
    root_window.tk.call(foverride + '.height-override','configure','-from','-10','-to','10','-resolution','0.1') #0
    root_window.tk.call(fpausedmotion + '.paused-motion-speed','configure','-from','-1','-to','1','-resolution','0.1') #0
    root_window.tk.call(fcutparms + '.pierce-delay','configure','-from','0','-to','10','-increment','0.1','-format','%0.1f') #0.1
    root_window.tk.call(fcutparms + '.puddle-jump-height','configure','-from','0','-to','200','-increment','1','-format','%0.0f') #0
    root_window.tk.call(fcutparms + '.puddle-jump-delay','configure','-from','0','-to','9','-increment','0.01','-format','%0.2f') #0
    root_window.tk.call(fcutparms + '.cut-amps','configure','-from','0','-to','999','-increment','1','-format','%0.0f') #45
    root_window.tk.call(fcutparms + '.cut-volts','configure','-from','50','-to','300','-increment','0.1','-format','%0.1f') #122
    root_window.tk.call(fthc + '.use-auto-volts','select')
    root_window.tk.call(fthc + '.thc-enable','select')
    root_window.tk.call(fthc + '.thc-threshold','configure','-from','0.05','-to','9','-increment','0.01','-format','%0.2f') #1
    root_window.tk.call(fcornerlock + '.cornerlock-enable','select')
    root_window.tk.call(fcornerlock + '.cornerlock-threshold','configure','-from','1','-to','99','-increment','1','-format','%0.0f') #90
    root_window.tk.call(fkerflock + '.kerfcross-enable','select')
    root_window.tk.call(fkerflock + '.kerfcross-threshold','configure','-from','1','-to','10','-increment','0.1','-format','%0.1f') #3
    root_window.tk.call(farc + '.torch-off-delay','configure','-from','0','-to','9','-increment','0.1','-format','%0.1f') #0
    root_window.tk.call(farc + '.arc-fail-delay','configure','-from','0','-to','60','-increment','0.1','-format','%0.1f') #1
    root_window.tk.call(farc + '.arc-ok-low','configure','-from','0','-to','200','-increment','0.5','-format','%0.1f') #0
    root_window.tk.call(farc + '.arc-ok-high','configure','-from','50','-to','200','-increment','0.5','-format','%0.1f') #50
    root_window.tk.call(farc + '.arc-max-starts','configure','-from','1','-to','9','-increment','1','-format','%0.0f') #3
    root_window.tk.call(farc + '.restart-delay','configure','-from','1','-to','60','-increment','1','-format','%0.0f') #1
    root_window.tk.call(farc + '.arc-voltage-offset','configure','-from','-100','-to','100','-increment','0.1','-format','%0.1f') #0
    root_window.tk.call(farc + '.arc-voltage-scale','configure','-from','0.01','-to','99','-increment','0.01','-format','%0.2f') #1
    root_window.tk.call(foffsets + '.maxspeed','configure','-text',str(int(thcFeedRate)))
    root_window.tk.call(foffsets + '.pid-i-gain','configure','-from','0','-to','1000','-increment','1','-format','%0.0f') #0
    root_window.tk.call(foffsets + '.pid-d-gain','configure','-from','0','-to','1000','-increment','1','-format','%0.0f') #0
    if inifile.find('TRAJ','LINEAR_UNITS').lower() == 'mm':
        root_window.tk.call(fcutparms + '.cut-feed-rate','configure','-from','50','-to','9999','-increment','1','-format','%0.0f') #4000
        root_window.tk.call(fcutparms + '.cut-height','configure','-from','0','-to','25.4','-increment','0.1','-format','%0.1f') #1
        root_window.tk.call(fcutparms + '.pierce-height','configure','-from','0','-to','25.4','-increment','0.1','-format','%0.1f') #4
        root_window.tk.call(fmotion + '.float-switch-travel','configure','-from','0','-to','20','-increment','0.01','-format','%0.2f') #1.5
        root_window.tk.call(fmotion + '.probe-feed-rate','configure','-from','1','-to',thcFeedRate,'-increment','1','-format','%0.0f') #300
        root_window.tk.call(fmotion + '.safe-height','configure','-from','1','-to','99','-increment','1','-format','%0.0f') #20
        root_window.tk.call(fmotion + '.skip-ihs-distance','configure','-from','0','-to','999','-increment','1','-format','%0.0f') #0
        root_window.tk.call(foffsets + '.setup-feed-rate','configure','-from','1','-to',thcFeedRate,'-increment','1','-format','%0.0f') #int(thcFeedRate * 0.8)
    elif inifile.find('TRAJ','LINEAR_UNITS').lower() == 'inch':
        root_window.tk.call(fcutparms + '.cut-feed-rate','configure','-from','2','-to','400','-increment','0.1','-format','%0.1f') #160
        root_window.tk.call(fcutparms + '.cut-height','configure','-from','0','-to','1','-increment','0.01','-format','%0.2f') #0.04
        root_window.tk.call(fcutparms + '.pierce-height','configure','-from','0','-to','1','-increment','0.01','-format','%0.2f') #0.16
        root_window.tk.call(fmotion + '.float-switch-travel','configure','-from','0','-to','0.75','-increment','0.001','-format','%0.3f') #0.06
        root_window.tk.call(fmotion + '.probe-feed-rate','configure','-from','0.1','-to',thcFeedRate,'-increment','0.1','-format','%0.1f') #12
        root_window.tk.call(fmotion + '.safe-height','configure','-from','0.04','-to','4','-increment','0.01','-format','%0.2f') #0.75
        root_window.tk.call(fmotion + '.skip-ihs-distance','configure','-from','0','-to','99','-increment','0.1','-format','%0.1f') #0
        root_window.tk.call(foffsets + '.setup-feed-rate','configure','-from','0.1','-to',thcFeedRate,'-increment','0.1','-format','%0.1f') #int(thcFeedRate * 0.8)
    else:
        print '*** incorrect [TRAJ]LINEAR_UNITS in ini file'

def load_settings():
    for widget in wCheckbuttons + wSpinboxes + wScalesSaved:
        tmp, item = widget.rsplit('.',1)
        if item != 'height-override' or item != 'paused-motion-speed':
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
        for widget in wCheckbuttons + wSpinboxes + wScalesSaved:
            tmp, item = widget.rsplit('.',1)
            if widget in wCheckbuttons:
                if item in tmpDict:
                    if configDict.get(item) == '1':
                        root_window.tk.call(widget,'select')
                        hal.set_p('plasmac.%s' % (item),'1')
                    else:
                        root_window.tk.call(widget,'deselect')
                        hal.set_p('plasmac.%s' % (item),'0')
                else:
                    root_window.tk.call(widget,'deselect')
                    hal.set_p('plasmac.%s' % (item),'0')
                    print '***', item, 'missing from', configFile
            elif widget in wSpinboxes + wScalesSaved:
                if item in tmpDict:
                    if item == 'setup-feed-rate' and float(configDict.get(item)) > thcFeedRate:
                        configDict[item] = thcFeedRate
                    root_window.tk.call(widget,'set',configDict.get(item))
                    if item == 'arc-max-starts':
                        hal.set_p('plasmac.%s' % (item),'%d' % (float(configDict.get(item))))
                    elif item != 'cut-amps':
                        hal.set_p('plasmac.%s' % (item),'%f' % (float(configDict.get(item))))
                else:
                    root_window.tk.call(widget,'set','0')
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
    p_height = root_window.tk.call(fcutparms + '.pierce-height','get')
    p_delay = root_window.tk.call(fcutparms + '.pierce-delay','get')
    pj_height = root_window.tk.call(fcutparms + '.puddle-jump-height','get')
    pj_delay = root_window.tk.call(fcutparms + '.puddle-jump-delay','get')
    c_height = root_window.tk.call(fcutparms + '.cut-height','get')
    c_speed = root_window.call(fcutparms + '.cut-feed-rate','get')
    c_amps = root_window.tk.call(fcutparms + '.cut-amps','get')
    c_volts = root_window.tk.call(fcutparms + '.cut-volts','get')
    try:
        with open(materialsFile, 'r') as f_in:
            combolist = '[list'
            for line in f_in:
                if not line.startswith('#'):
                    if line.startswith('[') and line.strip().endswith(']') and not 'VERSION' in line:
                        materialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
                        root_window.tk.call(fmaterial + '.materials','insert','end',name)
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
            root_window.tk.call(fmaterial + '.materials','insert','end',name)
        root_window.tk.call(fmaterial + '.materials','setvalue','first')
    except:
        print '*** materials file,', materialsFile, 'is invalid'
    finally:
        f_in.close()

def set_mode(mode):
    if mode == '0':
        root_window.tk.call(fthc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
    elif mode == '1':
        root_window.tk.call('grid','forget',farc + '.arc-ok-high')
        root_window.tk.call('grid','forget',farc + '.aOHlab')
        root_window.tk.call('grid','forget',farc + '.arc-ok-low')
        root_window.tk.call('grid','forget',farc + '.aOLlab')
    elif mode == '2':
        root_window.tk.call(fthc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
        root_window.tk.call('grid','forget',fmonitor + '.arc-voltage')
        root_window.tk.call('grid','forget',fmonitor + '.aVlab')
        root_window.tk.call('grid','forget',farc + '.arc-ok-high')
        root_window.tk.call('grid','forget',farc + '.aOHlab')
        root_window.tk.call('grid','forget',farc + '.arc-ok-low')
        root_window.tk.call('grid','forget',farc + '.aOLlab')
        root_window.tk.call('grid','forget',farc + '.arc-voltage-scale')
        root_window.tk.call('grid','forget',farc + '.aVSlab')
        root_window.tk.call('grid','forget',farc + '.arc-voltage-offset')
        root_window.tk.call('grid','forget',farc + '.aVOlab')
        root_window.tk.call('grid','forget',fthc + '.use-auto-volts')
        root_window.tk.call('grid','forget',fthc + '.uAVlab') 
        root_window.tk.call('grid','forget',fthc + '.thc-threshold')
        root_window.tk.call('grid','forget',fthc + '.tTlab')
        root_window.tk.call(fthc + '.pid-p-gain','configure','-from','0','-to','100','-increment','1','-format','%0.0f') #25
        root_window.tk.call(fthc + '.pPGlab','configure','-text','Speed (%)')
        root_window.tk.call('pack','forget',fkerflock)
        root_window.tk.call('grid','forget',foffsets + '.pid-i-gain')
        root_window.tk.call('grid','forget',foffsets + '.pIGlab')
        root_window.tk.call('grid','forget',foffsets + '.pid-d-gain')
        root_window.tk.call('grid','forget',foffsets + '.pDGlab')
    hal.set_p('plasmac.mode','%d' % (int(mode)))
thcFeedRate = (float(inifile.find('AXIS_Z','MAX_VELOCITY')) * \
               float(inifile.find('AXIS_Z','OFFSET_AV_RATIO'))) * 60
hal.set_p('plasmac.thc-feed-rate','%f' % (thcFeedRate))
configFile = inifile.find('PLASMAC','CONFIG_FILE') or inifile.find('EMC','MACHINE').lower() + '.cfg'
materialsFile = inifile.find('PLASMAC','MATERIAL_FILE') or inifile.find('EMC','MACHINE').lower() + '.mat'
materialsList = []
configDict = {}
dryRun = 0
torchPulse = 0
materialsUpdate = False
wLabels = [fmonitor + '.aVlab',\
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
wCheckbuttons = [fcornerlock + '.cornerlock-enable',\
                 fkerflock + '.kerfcross-enable',\
                 fthc + '.thc-enable',\
                 fthc + '.use-auto-volts',\
                 ]
wSpinboxes = [fcutparms + '.pierce-height',\
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
wScalesSaved = [ftorch + '.torch-pulse-time']
wScalesVolatile = [foverride + '.height-override',\
                   fpausedmotion + '.paused-motion-speed',\
                   ]
wComboBoxes = [fmaterial + '.materials']
wLeds = [fthc + '.led-up',\
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
pcomp = hal.component('plasmac-panel')
pcomp.newpin('led-up', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('led-down', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('led-cornerlock', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('led-kerfcross', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('arc-voltage', hal.HAL_FLOAT, hal.HAL_IN)
pcomp.newpin('led-arc-ok', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('led-torch', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('led-float', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('led-breakaway', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('led-safe-height', hal.HAL_BIT, hal.HAL_IN)
pcomp.newpin('config-disable', hal.HAL_BIT, hal.HAL_IN)
pcomp.ready()
hal_data = [[0,'plasmac:arc-voltage-out','plasmac.arc-voltage-out','plasmac-panel.arc-voltage'],\
            [1,'plasmac:axis-min-limit','ini.z.min_limit','plasmac.axis-z-min-limit'],\
            [2,'plasmac:axis-max-limit','ini.z.max_limit','plasmac.axis-z-max-limit'],\
            [3,'plasmac:led-up','plasmac.led-up','plasmac-panel.led-up'],\
            [4,'plasmac:led-down','plasmac.led-down','plasmac-panel.led-down'],\
            [5,'plasmac:cornerlock-is-locked','plasmac.cornerlock-is-locked','plasmac-panel.led-cornerlock'],\
            [6,'plasmac:kerfcross-is-locked','plasmac.kerfcross-is-locked','plasmac-panel.led-kerfcross'],\
            [7,'plasmac:arc-ok-out','plasmac.arc-ok-out','plasmac-panel.led-arc-ok'],\
            [8,'plasmac:safe-height-is-limited','plasmac.safe-height-is-limited','plasmac-panel.led-safe-height'],\
            ]
for line in hal_data:
    if line[0] < 3:
        hal.new_sig(line[1],hal.HAL_FLOAT)
    else:
        hal.new_sig(line[1],hal.HAL_BIT)
    hal.connect(line[2],line[1])
    hal.connect(line[3],line[1])
hal.connect('plasmac-panel.led-float','plasmac:float-switch-out')
hal.connect('plasmac-panel.led-breakaway','plasmac:breakaway-switch-out')
hal.connect('plasmac-panel.led-torch','plasmac:torch-on')
for widget in wSpinboxes:
    root_window.tk.call(widget,'configure','-wrap','1','-width',swidth,'-font',font,'-justify','r')
for widget in wLabels:
    root_window.tk.call(widget,'configure','-anchor','w','-width',lwidth)
widgetValues={}
for widget in wSpinboxes + wScalesSaved + wScalesVolatile:
        widgetValues[widget] = float(root_window.tk.call(widget,'get'))
for widget in wCheckbuttons:
    tmp, item = widget.rsplit('.',1)
    widgetValues[widget] = int(root_window.tk.call('set',item))
for widget in wLeds:
    tmp, item = widget.rsplit('.',1)
    if pcomp[item] == 1:
        root_window.tk.call(widget,'configure','-state','normal')
        widgetValues[widget] = 1
    else:
        root_window.tk.call(widget,'configure','-state','disabled')
        widgetValues[widget] = 0
root_window.tk.call(fmotion + '.probe-feed-rate','configure','-to',widgetValues[foffsets + '.setup-feed-rate'])
units = hal.get_value('halui.machine.units-per-mm')
maxPidP = thcFeedRate / units * 0.1
mode = inifile.find('PLASMAC','MODE') or '0'
set_mode(mode)
commands.set_view_z()
