#''' set the window size, change pad_width and pad_height to suit your setup'''
#maxgeo=root_window.tk.call('wm','maxsize','.')
#if type(maxgeo) == tuple:
    #fullsize=str(maxgeo[0]),str(maxgeo[1])
#else:
    #fullsize=maxgeo.split(' ')[0],maxgeo.split(' ')[1]
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

# if we find plasma anywhere in the title
#if 'plasma' in inifile.find("EMC","MACHINE").lower():






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
root_window.tk.call('grid','forget','.pane.top.tabs.fmanual.jogf.zerohome.tooltouch')
root_window.tk.call('pack','forget','.pane.top.tabs.fmanual.spindlef.ccw')
root_window.tk.call('pack','forget','.pane.top.tabs.fmanual.spindlef.cw')
root_window.tk.call('pack','forget','.pane.top.tabs.fmanual.spindlef.stop')
root_window.tk.call('pack','forget','.pane.top.tabs.fmanual.spindlef.spindleminus')
root_window.tk.call('pack','forget','.pane.top.tabs.fmanual.spindlef.spindleplus')
root_window.tk.call('pack','forget','.pane.top.tabs.fmanual.spindlef.brake')
root_window.tk.call('grid','forget','.pane.top.tabs.fmanual.spindlef.row2')
#root_window.tk.call('grid','forget','.pane.top.tabs.fmanual.coolant')
root_window.tk.call('grid','forget','.pane.top.tabs.fmanual.flood')
root_window.tk.call('grid','forget','.pane.top.tabs.fmanual.mist')
root_window.tk.call('grid','forget','.pane.top.tabs.fmanual.space2')
root_window.tk.call('grid','forget','.pane.top.spinoverride')

# change some original widgets
root_window.tk.call('.pane.top.tabs.fmanual.space1','configure','-height','16')
root_window.tk.call('.pane.top.tabs.fmanual.spindlel','configure','-text','Torch: ')
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

# some new commands for TCL
def material_changed():
    if not materialsUpdate:
        newmaterial = root_window.tk.call(material + '.materials','getvalue')
        root_window.tk.call(cutparms + '.pierce-height','set',materialsList[newmaterial][1])
        root_window.tk.call(cutparms + '.pierce-delay','set',materialsList[newmaterial][2])
        root_window.tk.call(cutparms + '.puddle-jump-height','set',materialsList[newmaterial][3])
        root_window.tk.call(cutparms + '.puddle-jump-delay','set',materialsList[newmaterial][4])
        root_window.tk.call(cutparms + '.cut-height','set',materialsList[newmaterial][5])
        root_window.tk.call(cutparms + '.cut-feed-rate','set',materialsList[newmaterial][6])
        root_window.tk.call(cutparms + '.cut-amps','set',materialsList[newmaterial][7])
        root_window.tk.call(cutparms + '.cut-volts','set',materialsList[newmaterial][8])

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
    root_window.tk.call(material + '.materials','configure','-values','')
    get_materials()
    materialsUpdate = False

def x_to_home():
    goto_home('X')

def y_to_home():
    goto_home('Y')

def z_to_home():
    goto_home('Z')

def dry_run():
    if Popen(['halcmd getp halui.program.is-idle'], stdout=PIPE, shell=True).communicate()[0].strip() == 'TRUE':
        Popen('halcmd setp plasmac.dry-run-start 1', shell=True)
        global dryRun
        dryRun = 1

def torch_pulse():
    if Popen(['halcmd getp halui.program.is-idle'], stdout=PIPE, shell=True).communicate()[0].strip() == 'TRUE':
        Popen('halcmd setp plasmac.torch-pulse-start 1', shell=True)
        global torchPulse
        torchPulse = 1

def wait_for_completion():
    pass
    while c.wait_complete() == -1:
        pass

def goto_home(axis):
    idle = Popen(['halcmd getp halui.program.is-idle'], stdout=PIPE, shell=True).communicate()[0].strip()
    if idle == 'TRUE':
        home = inifile.find('JOINT_' + str(inifile.find('TRAJ','COORDINATES').upper().index(axis)), 'HOME')
        mode = Popen(['halcmd getp halui.mode.is-mdi'], stdout=PIPE, shell=True).communicate()[0].strip()
        if mode == 'FALSE':
            c.mode(linuxcnc.MODE_MDI)
            wait_for_completion()
        c.mdi('G53 G0 ' + axis + home)

# add the commands to TclCommands
TclCommands.material_changed = material_changed
TclCommands.save_config = save_config
TclCommands.reload_config = reload_config
TclCommands.x_to_home = x_to_home
TclCommands.y_to_home = y_to_home
TclCommands.z_to_home = z_to_home
TclCommands.dry_run = dry_run
TclCommands.torch_pulse = torch_pulse
commands = TclCommands(root_window)

# set sizes for widgets
swidth = 5  # spinboxes width
lwidth = 12 # labels width
bwidth = 8  # buttons width
cwidth = int(fsize) * 2 #canvas width
cheight = int(fsize) * 2 #canvas height
ledwidth = cwidth - 2 #led width
ledheight = cheight - 2 #led height
ledx = cwidth-ledwidth # led x start
ledy = cheight-ledheight # led y start

# make torch frame
torch = '.pane.top.tabs.fmanual.spindlef.row1.torch'
root_window.tk.call('labelframe',torch,'-relief','flat')

# make and place widgets for torch frame
root_window.tk.call('Button', torch + '.torch-button','-command','torch_pulse','-text','PULSE','-takefocus','0')
root_window.tk.call('append','manualgroup',' ' + torch + '.torch-button')
root_window.tk.call('scale', torch + '.torch-pulse-time','-orient','horizontal','-variable','torchPulse','-showvalue','0')
root_window.tk.call('label', torch + '.torch-time','-textvariable','torchPulse','-width','3','-anchor','e')
root_window.tk.call('label', torch + '.torch-label','-text','Sec')
root_window.tk.call('pack', torch + '.torch-button','-side','left','-pady','2')
root_window.tk.call('pack', torch + '.torch-pulse-time','-side','left')
root_window.tk.call('pack', torch + '.torch-time','-side','left')
root_window.tk.call('pack', torch + '.torch-label','-side','left')

# place torch frame
root_window.tk.call('pack', torch,'-side','left','-in','.pane.top.tabs.fmanual.spindlef.row1')

#make monitor frame
monitor = '.pane.top.monitor'
root_window.tk.call('labelframe',monitor,'-text','Monitor','-relief','raised')

#make and place widgets for monitor frame
#fname = font.split()[0]
#fsize = font.split()[1]
arcfont = fname + ' ' + str(int(fsize) + 2) + ' bold'
root_window.tk.call('label',monitor + '.arc-voltage','-anchor','e','-width',swidth,'-fg','blue','-font',arcfont)
root_window.tk.call('label',monitor + '.aVlab','-text','Arc Voltage')
root_window.tk.call('canvas',monitor + '.led-float','-width',cwidth,'-height',cheight)
root_window.tk.call(monitor + '.led-float','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',monitor + '.lFlab','-text','Float Switch')
root_window.tk.call('canvas',monitor + '.led-torch','-width',cwidth,'-height',cheight)
root_window.tk.call(monitor + '.led-torch','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','orange','-disabledfill','grey')
root_window.tk.call('label',monitor + '.lTlab','-text','Torch On')
root_window.tk.call('canvas',monitor + '.led-breakaway','-width',cwidth,'-height',cheight)
root_window.tk.call(monitor + '.led-breakaway','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',monitor + '.lBlab','-text','Breakaway')
root_window.tk.call('canvas',monitor + '.led-arc-ok','-width',cwidth,'-height',cheight)
root_window.tk.call(monitor + '.led-arc-ok','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','lightgreen','-disabledfill','grey')
root_window.tk.call('label',monitor + '.lAOlab','-text','Ark OK')
root_window.tk.call('canvas',monitor + '.led-safe-height','-width',cwidth,'-height',cheight)
root_window.tk.call(monitor + '.led-safe-height','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',monitor + '.lSHlab','-text','Safe Limited')
root_window.tk.call('grid',monitor + '.arc-voltage','-row','0','-column','0','-sticky','e')
root_window.tk.call('grid',monitor + '.aVlab','-row','0','-column','1',)
root_window.tk.call('grid',monitor + '.led-float','-row','0','-column','2','-sticky','e')
root_window.tk.call('grid',monitor + '.lFlab','-row','0','-column','3')
root_window.tk.call('grid',monitor + '.led-torch','-row','1','-column','0','-sticky','e')
root_window.tk.call('grid',monitor + '.lTlab','-row','1','-column','1')
root_window.tk.call('grid',monitor + '.led-breakaway','-row','1','-column','2','-sticky','e')
root_window.tk.call('grid',monitor + '.lBlab','-row','1','-column','3')
root_window.tk.call('grid',monitor + '.led-arc-ok','-row','2','-column','0','-sticky','e')
root_window.tk.call('grid',monitor + '.lAOlab','-row','2','-column','1')
root_window.tk.call('grid',monitor + '.led-safe-height','-row','2','-column','2','-sticky','e')
root_window.tk.call('grid',monitor + '.lSHlab','-row','2','-column','3')

#place monitor frame
root_window.tk.call('grid',monitor,'-column','0','-row','8','-sticky','new','-pady','4')
root_window.tk.call('grid','columnconfigure',monitor,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',monitor,1,'-weight','1')
root_window.tk.call('grid','columnconfigure',monitor,2,'-weight','1')
root_window.tk.call('grid','columnconfigure',monitor,3,'-weight','1')

#make new notebook for plasmac stuff
root_window.tk.call('NoteBook','.plasmac','-borderwidth','2','-arcradius','3')
root_window.tk.call('.plasmac','insert','end','run','-text','Run')
root_window.tk.call('.plasmac','insert','end','config','-text','Configure')
frun = '.plasmac.frun'
fconfig = '.plasmac.fconfig'

#make run label frames
material = '.plasmac.frun.material'
cutparms = '.plasmac.frun.cutparms'
thc = '.plasmac.frun.thc'



#override = '.plasmac.frun.override'
override = '.pane.top.tabs.fmanual.coolant.override'



locks = '.plasmac.frun.locks'
buttons = '.plasmac.frun.buttons'
pausedmotion = '.plasmac.frun.pausedmotion'
root_window.tk.call('labelframe',material,'-text','Material','-relief','ridge')
root_window.tk.call('labelframe',cutparms,'-text','Cut Parameters','-relief','ridge')
root_window.tk.call('labelframe',thc,'-text','THC','-relief','ridge')
root_window.tk.call('labelframe',override,'-text','Height Override','-relief','ridge')
root_window.tk.call('labelframe',locks,'-text','Locks','-relief','ridge')
root_window.tk.call('labelframe',buttons,'-text','Buttons','-relief','ridge')
root_window.tk.call('labelframe',pausedmotion,'-text','Paused Motion Speed','-relief','ridge')

#make config label frames
motion = '.plasmac.fconfig.motion'
arc = '.plasmac.fconfig.arc'
offsets = '.plasmac.fconfig.offsets'
settings ='.plasmac.fconfig.settings'
root_window.tk.call('labelframe',motion,'-text','Motion','-relief','ridge')
root_window.tk.call('labelframe',arc,'-text','Arc','-relief','ridge')
root_window.tk.call('labelframe',offsets,'-text','Offsets','-relief','ridge')
root_window.tk.call('labelframe',settings,'-text','Settings','-relief','ridge')

#make and place widgets for material frame
root_window.tk.call('ComboBox',material + '.materials','-modifycmd','material_changed')
root_window.tk.call('DynamicHelp::add',material + '.materials','-text','select material from materials file')
root_window.tk.call('pack',material + '.materials','-fill','x')

#make and place widgets for cut parameters frame
root_window.tk.call('spinbox',cutparms + '.pierce-height')
root_window.tk.call('DynamicHelp::add',cutparms + '.pierce-height','-text','piercing height\nin machine units')
root_window.tk.call('label',cutparms + '.pHlab','-text','Pierce Height')
root_window.tk.call('spinbox',cutparms + '.cut-height')
root_window.tk.call('label',cutparms + '.cHlab','-text','Cut Height')
root_window.tk.call('spinbox',cutparms + '.pierce-delay')
root_window.tk.call('label',cutparms + '.pDlab','-text','Pierce Delay')
root_window.tk.call('spinbox',cutparms + '.cut-feed-rate')
root_window.tk.call('label',cutparms + '.cFRlab','-text','Cut Feed Rate')
root_window.tk.call('spinbox',cutparms + '.puddle-jump-height')
root_window.tk.call('label',cutparms + '.pJHlab','-text','P-J Height')
root_window.tk.call('spinbox',cutparms + '.cut-amps')
root_window.tk.call('label',cutparms + '.cAlab','-text','Cut Amps')
root_window.tk.call('spinbox',cutparms + '.puddle-jump-delay')
root_window.tk.call('label',cutparms + '.pJDlab','-text','P-J Delay')
root_window.tk.call('spinbox',cutparms + '.cut-volts')
root_window.tk.call('label',cutparms + '.cVlab','-text','Cut Volts')
root_window.tk.call('grid',cutparms + '.pierce-height','-row','0','-column','0')
root_window.tk.call('grid',cutparms + '.pHlab','-row','0','-column','1')
root_window.tk.call('grid',cutparms + '.cut-height','-row','0','-column','2')
root_window.tk.call('grid',cutparms + '.cHlab','-row','0','-column','3')
root_window.tk.call('grid',cutparms + '.pierce-delay','-row','1','-column','0')
root_window.tk.call('grid',cutparms + '.pDlab','-row','1','-column','1')
root_window.tk.call('grid',cutparms + '.cut-feed-rate','-row','1','-column','2')
root_window.tk.call('grid',cutparms + '.cFRlab','-row','1','-column','3')
root_window.tk.call('grid',cutparms + '.puddle-jump-height','-row','2','-column','0')
root_window.tk.call('grid',cutparms + '.pJHlab','-row','2','-column','1')
root_window.tk.call('grid',cutparms + '.cut-amps','-row','2','-column','2')
root_window.tk.call('grid',cutparms + '.cAlab','-row','2','-column','3')
root_window.tk.call('grid',cutparms + '.puddle-jump-delay','-row','3','-column','0')
root_window.tk.call('grid',cutparms + '.pJDlab','-row','3','-column','1')
root_window.tk.call('grid',cutparms + '.cut-volts','-row','3','-column','2')
root_window.tk.call('grid',cutparms + '.cVlab','-row','3','-column','3')

#make and place widgets for thc frame
root_window.tk.call('checkbutton',thc + '.thc-enable')
root_window.tk.call('label',thc + '.tElab','-text','Enable')
root_window.tk.call('checkbutton',thc + '.use-auto-volts')
root_window.tk.call('label',thc + '.uAVlab','-text','Auto Volts')
root_window.tk.call('spinbox',thc + '.thc-threshold')
root_window.tk.call('label',thc + '.tTlab','-text','Threshold')
root_window.tk.call('canvas',thc + '.led-up','-width',cwidth,'-height',cheight)
root_window.tk.call(thc + '.led-up','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','yellow','-disabledfill','grey')
root_window.tk.call('label',thc + '.lUlab','-text','Move Up')
root_window.tk.call('spinbox',thc + '.pid-p-gain')
root_window.tk.call('label',thc + '.pPGlab','-text','Speed (PIDP)')
root_window.tk.call('canvas',thc + '.led-down','-width',cwidth,'-height',cheight)
root_window.tk.call(thc + '.led-down','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','yellow','-disabledfill','grey')
root_window.tk.call('label',thc + '.lDlab','-text','Move Down')
root_window.tk.call('grid',thc + '.thc-enable','-row','0','-column','0')
root_window.tk.call('grid',thc + '.tElab','-row','0','-column','1')
root_window.tk.call('grid',thc + '.use-auto-volts','-row','0','-column','2')
root_window.tk.call('grid',thc + '.uAVlab','-row','0','-column','3')
root_window.tk.call('grid',thc + '.thc-threshold','-row','1','-column','0')
root_window.tk.call('grid',thc + '.tTlab','-row','1','-column','1')
root_window.tk.call('grid',thc + '.led-up','-row','1','-column','2')
root_window.tk.call('grid',thc + '.lUlab','-row','1','-column','3')
root_window.tk.call('grid',thc + '.pid-p-gain','-row','2','-column','0')
root_window.tk.call('grid',thc + '.pPGlab','-row','2','-column','1')
root_window.tk.call('grid',thc + '.led-down','-row','2','-column','2')
root_window.tk.call('grid',thc + '.lDlab','-row','2','-column','3')




#make and place widgets for override frame
root_window.tk.call('scale',override + '.height-override','-orient','horizontal')
root_window.tk.call('pack',override + '.height-override','-fill','x')
root_window.tk.call('grid','.pane.top.tabs.fmanual.coolant','-column','0','-row','5','-columnspan','2','-sticky','ew')

#root_window.tk.call('scale',override + '.height-override','-orient','horizontal')
#root_window.tk.call('pack',override + '.height-override','-fill','x')




#make and place widgets for locks frame
cornerlock = '.plasmac.frun.locks.cornerlock'
kerflock = '.plasmac.frun.locks.kerflock'
root_window.tk.call('labelframe',cornerlock,'-text','Corner','-relief','sunken')
root_window.tk.call('checkbutton',cornerlock + '.cornerlock-enable')
root_window.tk.call('label',cornerlock + '.cElab','-text','Enable')
root_window.tk.call('spinbox',cornerlock + '.cornerlock-threshold')
root_window.tk.call('label',cornerlock + '.cTlab','-text','Threshold(%)')
root_window.tk.call('canvas',cornerlock + '.led-cornerlock','-width',cwidth,'-height',cheight)
root_window.tk.call(cornerlock + '.led-cornerlock','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',cornerlock + '.lClab','-text','Locked(%)')
root_window.tk.call('labelframe',kerflock,'-text','Kerf','-relief','sunken')
root_window.tk.call('checkbutton',kerflock + '.kerfcross-enable')
root_window.tk.call('label',kerflock + '.kElab','-text','Enable')
root_window.tk.call('spinbox',kerflock + '.kerfcross-threshold')
root_window.tk.call('label',kerflock + '.kTlab','-text','Threshold(V)')
root_window.tk.call('canvas',kerflock + '.led-kerfcross','-width',cwidth,'-height',cheight)
root_window.tk.call(kerflock + '.led-kerfcross','create','oval',ledx,ledy,ledwidth,ledheight,'-fill','red','-disabledfill','grey')
root_window.tk.call('label',kerflock + '.lKlab','-text','Locked(%)')
root_window.tk.call('grid',cornerlock + '.cornerlock-enable','-row','0','-column','0')
root_window.tk.call('grid',cornerlock + '.cElab','-row','0','-column','1')
root_window.tk.call('grid',cornerlock + '.cornerlock-threshold','-row','1','-column','0')
root_window.tk.call('grid',cornerlock + '.cTlab','-row','1','-column','1')
root_window.tk.call('grid',cornerlock + '.led-cornerlock','-row','2','-column','0')
root_window.tk.call('grid',cornerlock + '.lClab','-row','2','-column','1')
root_window.tk.call('grid',kerflock + '.kerfcross-enable','-row','0','-column','0')
root_window.tk.call('grid',kerflock + '.kElab','-row','0','-column','1')
root_window.tk.call('grid',kerflock + '.kerfcross-threshold','-row','1','-column','0')
root_window.tk.call('grid',kerflock + '.kTlab','-row','1','-column','1')
root_window.tk.call('grid',kerflock + '.led-kerfcross','-row','2','-column','0')
root_window.tk.call('grid',kerflock + '.lKlab','-row','2','-column','1')
root_window.tk.call('pack',cornerlock,'-side','left','-padx','1','-pady','1')
root_window.tk.call('pack',kerflock,'-side','right','-padx','1','-pady','1')

#make and place widgets for buttons frame
root_window.tk.call('button',buttons + '.xtohome','-text','X to Home','-command','x_to_home','-width',bwidth)
root_window.tk.call('button',buttons + '.ytohome','-text','Y to Home','-command','y_to_home','-width',bwidth)
root_window.tk.call('button',buttons + '.ztohome','-text','Z to Home','-command','z_to_home','-width',bwidth)
root_window.tk.call('button',buttons + '.dryRun','-text','Dry Run','-command','dry_run','-width',bwidth)
root_window.tk.call('grid',buttons + '.xtohome','-row','0','-column','0')
root_window.tk.call('grid',buttons + '.ytohome','-row','0','-column','1')
root_window.tk.call('grid',buttons + '.ztohome','-row','0','-column','2')
root_window.tk.call('grid',buttons + '.dryRun','-row','1','-column','0')

#make and place widgets for paused motion frame
root_window.tk.call('scale',pausedmotion + '.paused-motion-speed','-orient','horizontal')
root_window.tk.call('pack',pausedmotion + '.paused-motion-speed','-fill','x')

#make and place widgets for motion frame
root_window.tk.call('spinbox',motion + '.safe-height')
root_window.tk.call('label',motion + '.sHlab','-text','Safe Height')
root_window.tk.call('spinbox',motion + '.probe-feed-rate')
root_window.tk.call('label',motion + '.pFRlab','-text','Probe Speed')
root_window.tk.call('spinbox',motion + '.float-switch-travel')
root_window.tk.call('label',motion + '.fSTlab','-text','Float Travel')
root_window.tk.call('spinbox',motion + '.skip-ihs-distance','-from','0','-to','20')
root_window.tk.call('label',motion + '.sIDlab','-text','Skip IHS')
root_window.tk.call('grid',motion + '.safe-height','-row','0','-column','0')
root_window.tk.call('grid',motion + '.sHlab','-row','0','-column','1')
root_window.tk.call('grid',motion + '.probe-feed-rate','-row','0','-column','2')
root_window.tk.call('grid',motion + '.pFRlab','-row','0','-column','3')
root_window.tk.call('grid',motion + '.float-switch-travel','-row','1','-column','0')
root_window.tk.call('grid',motion + '.fSTlab','-row','1','-column','1')
root_window.tk.call('grid',motion + '.skip-ihs-distance','-row','1','-column','2')
root_window.tk.call('grid',motion + '.sIDlab','-row','1','-column','3')

#make and place widgets for arc frame
root_window.tk.call('spinbox',arc + '.arc-fail-delay')
root_window.tk.call('label',arc + '.aFDlab','-text','Fail Timeout')
root_window.tk.call('spinbox',arc + '.arc-voltage-scale')
root_window.tk.call('label',arc + '.aVSlab','-text','Voltage Scale')
root_window.tk.call('spinbox',arc + '.arc-max-starts')
root_window.tk.call('label',arc + '.aMSlab','-text','Max. Starts')
root_window.tk.call('spinbox',arc + '.arc-voltage-offset')
root_window.tk.call('label',arc + '.aVOlab','-text','Voltage Offset')
root_window.tk.call('spinbox',arc + '.restart-delay')
root_window.tk.call('label',arc + '.aRDlab','-text','Retry Delay')
root_window.tk.call('spinbox',arc + '.arc-ok-high')
root_window.tk.call('label',arc + '.aOHlab','-text','OK High Volts')
root_window.tk.call('spinbox',arc + '.torch-off-delay')
root_window.tk.call('label',arc + '.tODlab','-text','Off Delay')
root_window.tk.call('spinbox',arc + '.arc-ok-low')
root_window.tk.call('label',arc + '.aOLlab','-text','OK Low Volts')
root_window.tk.call('grid',arc + '.arc-fail-delay','-row','0','-column','0')
root_window.tk.call('grid',arc + '.aFDlab','-row','0','-column','1')
root_window.tk.call('grid',arc + '.arc-voltage-scale','-row','0','-column','2')
root_window.tk.call('grid',arc + '.aVSlab','-row','0','-column','3')
root_window.tk.call('grid',arc + '.arc-max-starts','-row','1','-column','0')
root_window.tk.call('grid',arc + '.aMSlab','-row','1','-column','1')
root_window.tk.call('grid',arc + '.arc-voltage-offset','-row','1','-column','2')
root_window.tk.call('grid',arc + '.aVOlab','-row','1','-column','3')
root_window.tk.call('grid',arc + '.restart-delay','-row','2','-column','0')
root_window.tk.call('grid',arc + '.aRDlab','-row','2','-column','1')
root_window.tk.call('grid',arc + '.arc-ok-high','-row','2','-column','2')
root_window.tk.call('grid',arc + '.aOHlab','-row','2','-column','3')
root_window.tk.call('grid',arc + '.torch-off-delay','-row','3','-column','0')
root_window.tk.call('grid',arc + '.tODlab','-row','3','-column','1')
root_window.tk.call('grid',arc + '.arc-ok-low','-row','3','-column','2')
root_window.tk.call('grid',arc + '.aOLlab','-row','3','-column','3')

#make and place widgets for offsets frame
root_window.tk.call('label',offsets + '.maxspeed','-text','0','-anchor','e','-width',swidth)
root_window.tk.call('label',offsets + '.msplab','-text','Max. Speed')
root_window.tk.call('spinbox',offsets + '.pid-i-gain')
root_window.tk.call('label',offsets + '.pIGlab','-text','PID I Gain')
root_window.tk.call('spinbox',offsets + '.setup-feed-rate')
root_window.tk.call('label',offsets + '.sFRlab','-text','Setup Speed')
root_window.tk.call('spinbox',offsets + '.pid-d-gain','-from','0','-to','20')
root_window.tk.call('label',offsets + '.pDGlab','-text','PID D Gain')
root_window.tk.call('grid',offsets + '.maxspeed','-row','0','-column','0')
root_window.tk.call('grid',offsets + '.msplab','-row','0','-column','1')
root_window.tk.call('grid',offsets + '.pid-i-gain','-row','0','-column','2')
root_window.tk.call('grid',offsets + '.pIGlab','-row','0','-column','3')
root_window.tk.call('grid',offsets + '.setup-feed-rate','-row','1','-column','0')
root_window.tk.call('grid',offsets + '.sFRlab','-row','1','-column','1')
root_window.tk.call('grid',offsets + '.pid-d-gain','-row','1','-column','2')
root_window.tk.call('grid',offsets + '.pDGlab','-row','1','-column','3')

#make and place widgets for settings frame
root_window.tk.call('button',settings + '.save','-text','Save','-command','save_config','-width',bwidth)
root_window.tk.call('button',settings + '.reload','-text','Reload','-width',bwidth,'-command','reload_config')
root_window.tk.call('grid',settings + '.save','-row','0','-column','0')
root_window.tk.call('grid',settings + '.reload','-row','0','-column','1')

#place run label frames
root_window.tk.call('pack',material,'-fill','x')
root_window.tk.call('pack',cutparms,'-fill','x')
root_window.tk.call('pack',thc,'-fill','x')
root_window.tk.call('pack',override,'-fill','x')
root_window.tk.call('pack',locks,'-fill','x')
root_window.tk.call('pack',buttons,'-fill','x')
root_window.tk.call('pack',pausedmotion,'-fill','x')
root_window.tk.call('grid','columnconfigure',cutparms,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',cutparms,1,'-weight','1')
root_window.tk.call('grid','columnconfigure',cutparms,2,'-weight','1')
root_window.tk.call('grid','columnconfigure',cutparms,3,'-weight','1')
root_window.tk.call('grid','columnconfigure',thc,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',thc,1,'-weight','1')
root_window.tk.call('grid','columnconfigure',thc,2,'-weight','1')
root_window.tk.call('grid','columnconfigure',thc,3,'-weight','1')
root_window.tk.call('grid','columnconfigure',buttons,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',buttons,1,'-weight','1')
root_window.tk.call('grid','columnconfigure',buttons,2,'-weight','1')

#place config label frames
root_window.tk.call('pack',motion,'-fill','x','-expand','0')
root_window.tk.call('pack',arc,'-fill','x','-expand','0')
root_window.tk.call('pack',offsets,'-fill','x','-expand','0')
root_window.tk.call('pack',settings,'-fill','x','-expand','0')
root_window.tk.call('grid','columnconfigure',motion,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',motion,1,'-weight','1')
root_window.tk.call('grid','columnconfigure',motion,2,'-weight','1')
root_window.tk.call('grid','columnconfigure',motion,3,'-weight','1')
root_window.tk.call('grid','columnconfigure',arc,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',arc,1,'-weight','1')
root_window.tk.call('grid','columnconfigure',arc,2,'-weight','1')
root_window.tk.call('grid','columnconfigure',arc,3,'-weight','1')
root_window.tk.call('grid','columnconfigure',offsets,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',offsets,1,'-weight','1')
root_window.tk.call('grid','columnconfigure',offsets,2,'-weight','1')
root_window.tk.call('grid','columnconfigure',offsets,3,'-weight','1')
root_window.tk.call('grid','columnconfigure',settings,0,'-weight','1')
root_window.tk.call('grid','columnconfigure',settings,1,'-weight','1')

#move original pane
root_window.tk.call('grid','.pane','-column','1','-row','1','-sticky','nsew','-rowspan','2')

#place new notebook
root_window.tk.call('.plasmac','raise','run')
root_window.tk.call('grid','.plasmac','-column','0','-row','1','-sticky','nsew','-rowspan','2')
root_window.tk.call('grid','columnconfigure','.','0','-weight','0')
root_window.tk.call('grid','columnconfigure','.','1','-weight','1')

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
                    Popen('halcmd setp plasmac.%s %d' % (item, value), shell=True)
                else:
                    Popen('halcmd setp plasmac.%s %f' % (item, value), shell=True)
                if item == 'setup-feed-rate': #limit max probe feed rate to setup feed rate
                    root_window.tk.call(motion + '.probe-feed-rate','configure','-to',value)
    for widget in wCheckbuttons:
        tmp, item = widget.rsplit('.',1)
        value = int(root_window.tk.call('set',item))
        if value != widgetValues[widget]:
            widgetValues[widget] = value
            Popen('halcmd setp plasmac.%s %d' % (item, value), shell=True)
    for widget in wLeds:
        tmp, item = widget.rsplit('.',1)
        if pcomp[item] != widgetValues[widget]:
            widgetValues[widget] = pcomp[item]
            if pcomp[item] == 1:
                root_window.tk.call(widget,'configure','-state','normal')
            else:
                root_window.tk.call(widget,'configure','-state','disabled')
    root_window.tk.call(monitor + '.arc-voltage','configure','-text','%0.1f' % (pcomp['arc-voltage']))
    global dryRun
    if dryRun == 1:
        if Popen(['halcmd getp halui.program.is-running'], stdout=PIPE, shell=True).communicate()[0].strip() == 'TRUE':
            Popen('halcmd setp plasmac.dry-run-start 0', shell=True)
            dryRun = 0
    global torchPulse
    if torchPulse == 1:
        if Popen(['halcmd getp plasmac.torch-on'], stdout=PIPE, shell=True).communicate()[0].strip() == 'TRUE':
            Popen('halcmd setp plasmac.torch-pulse-start 0', shell=True)
            torchPulse = 0
    if Popen(['halcmd getp plasmac-panel.config-disable'], stdout=PIPE, shell=True).communicate()[0].strip() == 'TRUE':
        root_window.tk.call('.plasmac','itemconfigure','config','-state','disabled')
    else:
        root_window.tk.call('.plasmac','itemconfigure','config','-state','normal')

def configure_widgets():
    root_window.tk.call(torch + '.torch-pulse-time','configure','-from','0','-to','3','-resolution','0.1')
    root_window.tk.call(arc + '.arc-fail-delay','configure','-from','0','-to','60','-increment','0.1','-format','%0.1f') #1
    root_window.tk.call(arc + '.arc-ok-low','configure','-from','0','-to','200','-increment','0.5','-format','%0.1f') #0
    root_window.tk.call(arc + '.arc-ok-high','configure','-from','50','-to','200','-increment','0.5','-format','%0.1f') #50
    root_window.tk.call(arc + '.arc-max-starts','configure','-from','1','-to','9','-increment','1','-format','%0.0f') #3
    root_window.tk.call(arc + '.restart-delay','configure','-from','1','-to','60','-increment','1','-format','%0.0f') #1
    root_window.tk.call(arc + '.arc-voltage-offset','configure','-from','-100','-to','100','-increment','0.1','-format','%0.1f') #0
    root_window.tk.call(arc + '.arc-voltage-scale','configure','-from','0.01','-to','99','-increment','0.01','-format','%0.2f') #1
    root_window.tk.call(thc + '.use-auto-volts','select')
    root_window.tk.call(cornerlock + '.cornerlock-enable','select')
    root_window.tk.call(cornerlock + '.cornerlock-threshold','configure','-from','1','-to','99','-increment','1','-format','%0.0f') #90
    root_window.tk.call(cutparms + '.cut-amps','configure','-from','0','-to','999','-increment','1','-format','%0.0f') #45
    root_window.tk.call(cutparms + '.cut-volts','configure','-from','50','-to','300','-increment','0.1','-format','%0.1f') #122
    root_window.tk.call(override + '.height-override','configure','-from','-10','-to','10','-resolution','0.1') #0
    root_window.tk.call(kerflock + '.kerfcross-enable','select')
    root_window.tk.call(kerflock + '.kerfcross-threshold','configure','-from','1','-to','10','-increment','0.1','-format','%0.1f') #3
    root_window.tk.call(offsets + '.maxspeed','configure','-text',str(int(thcFeedRate)))
    root_window.tk.call(offsets + '.pid-i-gain','configure','-from','0','-to','1000','-increment','1','-format','%0.0f') #0
    root_window.tk.call(offsets + '.pid-d-gain','configure','-from','0','-to','1000','-increment','1','-format','%0.0f') #0
    root_window.tk.call(cutparms + '.pierce-delay','configure','-from','0','-to','10','-increment','0.1','-format','%0.1f') #0.1
    root_window.tk.call(cutparms + '.puddle-jump-height','configure','-from','0','-to','200','-increment','1','-format','%0.0f') #0
    root_window.tk.call(cutparms + '.puddle-jump-delay','configure','-from','0','-to','9','-increment','0.01','-format','%0.2f') #0
    root_window.tk.call(pausedmotion + '.paused-motion-speed','configure','-from','-1','-to','1','-resolution','0.1') #0
    root_window.tk.call(thc + '.thc-enable','select')
    root_window.tk.call(thc + '.thc-threshold','configure','-from','0.05','-to','9','-increment','0.01','-format','%0.2f') #1
    root_window.tk.call(arc + '.torch-off-delay','configure','-from','0','-to','9','-increment','0.1','-format','%0.1f') #0
    if inifile.find('TRAJ','LINEAR_UNITS').lower() == 'mm':
        root_window.tk.call(cutparms + '.cut-feed-rate','configure','-from','50','-to','9999','-increment','1','-format','%0.0f') #4000
        root_window.tk.call(cutparms + '.cut-height','configure','-from','0','-to','25.4','-increment','0.1','-format','%0.1f') #1
        root_window.tk.call(motion + '.float-switch-travel','configure','-from','0','-to','20','-increment','0.01','-format','%0.2f') #1.5
        root_window.tk.call(cutparms + '.pierce-height','configure','-from','0','-to','25.4','-increment','0.1','-format','%0.1f') #4
        root_window.tk.call(motion + '.probe-feed-rate','configure','-from','1','-to',thcFeedRate,'-increment','1','-format','%0.0f') #300
        root_window.tk.call(motion + '.safe-height','configure','-from','1','-to','99','-increment','1','-format','%0.0f') #20
        root_window.tk.call(offsets + '.setup-feed-rate','configure','-from','1','-to',thcFeedRate,'-increment','1','-format','%0.0f') #int(thcFeedRate * 0.8)
        root_window.tk.call(motion + '.skip-ihs-distance','configure','-from','0','-to','999','-increment','1','-format','%0.0f') #0
    elif inifile.find('TRAJ','LINEAR_UNITS').lower() == 'inch':
        root_window.tk.call(cutparms + '.cut-feed-rate','configure','-from','2','-to','400','-increment','0.1','-format','%0.1f') #160
        root_window.tk.call(cutparms + '.cut-height','configure','-from','0','-to','1','-increment','0.01','-format','%0.2f') #0.04
        root_window.tk.call(motion + '.float-switch-travel','configure','-from','0','-to','0.75','-increment','0.001','-format','%0.3f') #0.06
        root_window.tk.call(cutparms + '.pierce-height','configure','-from','0','-to','1','-increment','0.01','-format','%0.2f') #0.16
        root_window.tk.call(motion + '.probe-feed-rate','configure','-from','0.1','-to',thcFeedRate,'-increment','0.1','-format','%0.1f') #12
        root_window.tk.call(motion + '.safe-height','configure','-from','0.04','-to','4','-increment','0.01','-format','%0.2f') #0.75
        root_window.tk.call(offsets + '.setup-feed-rate','configure','-from','0.1','-to',thcFeedRate,'-increment','0.1','-format','%0.1f') #int(thcFeedRate * 0.8)
        root_window.tk.call(motion + '.skip-ihs-distance','configure','-from','0','-to','99','-increment','0.1','-format','%0.1f') #0
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
                        Popen('halcmd setp plasmac.%s %d' % (item, 1), shell=True)
                    else:
                        root_window.tk.call(widget,'deselect')
                        Popen('halcmd setp plasmac.%s %d' % (item, 0), shell=True)
                else:
                    root_window.tk.call(widget,'deselect')
                    Popen('halcmd setp plasmac.%s %d' % (item, 0), shell=True)
                    print '***', item, 'missing from', configFile
            elif widget in wSpinboxes + wScalesSaved:
                if item in tmpDict:
                    root_window.tk.call(widget,'set',configDict.get(item))
                    if item == 'arc-max-starts':
                        Popen('halcmd setp plasmac.%s %d' % (item, float(configDict.get(item))), shell=True)
                    elif item != 'cut-amps':
                        Popen('halcmd setp plasmac.%s %f' % (item, float(configDict.get(item))), shell=True)
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
    p_height = root_window.tk.call(cutparms + '.pierce-height','get')
    p_delay = root_window.tk.call(cutparms + '.pierce-delay','get')
    pj_height = root_window.tk.call(cutparms + '.puddle-jump-height','get')
    pj_delay = root_window.tk.call(cutparms + '.puddle-jump-delay','get')
    c_height = root_window.tk.call(cutparms + '.cut-height','get')
    c_speed = root_window.call(cutparms + '.cut-feed-rate','get')
    c_amps = root_window.tk.call(cutparms + '.cut-amps','get')
    c_volts = root_window.tk.call(cutparms + '.cut-volts','get')
    try:
        with open(materialsFile, 'r') as f_in:
            combolist = '[list'
            for line in f_in:
                if not line.startswith('#'):
                    if line.startswith('[') and line.strip().endswith(']') and not 'VERSION' in line:
                        materialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
                        root_window.tk.call(material + '.materials','insert','end',name)
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
            root_window.tk.call(material + '.materials','insert','end',name)
        root_window.tk.call(material + '.materials','setvalue','first')
    except:
        print '*** materials file,', materialsFile, 'is invalid'
    finally:
        f_in.close()

def set_mode0():
    root_window.tk.call(thc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
#    Popen('halcmd setp plasmac.mode 0', shell=True)

def set_mode1():
    root_window.tk.call('grid','forget',arc + '.arc-ok-high')
    root_window.tk.call('grid','forget',arc + '.aOHlab')
    root_window.tk.call('grid','forget',arc + '.arc-ok-low')
    root_window.tk.call('grid','forget',arc + '.aOLlab')
    root_window.tk.call(thc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
#    Popen('halcmd setp plasmac.mode 1', shell=True)

def set_mode2():
    root_window.tk.call('grid','forget',monitor + '.arc-voltage')
    root_window.tk.call('grid','forget',monitor + '.aVlab')
    root_window.tk.call('grid','forget',arc + '.arc-ok-high')
    root_window.tk.call('grid','forget',arc + '.aOHlab')
    root_window.tk.call('grid','forget',arc + '.arc-ok-low')
    root_window.tk.call('grid','forget',arc + '.aOLlab')
    root_window.tk.call('grid','forget',arc + '.arc-voltage-scale')
    root_window.tk.call('grid','forget',arc + '.aVSlab')
    root_window.tk.call('grid','forget',arc + '.arc-voltage-offset')
    root_window.tk.call('grid','forget',arc + '.aVOlab')
    root_window.tk.call('grid','forget',thc + '.use-auto-volts')
    root_window.tk.call('grid','forget',thc + '.uAVlab') 
    root_window.tk.call('grid','forget',thc + '.thc-threshold')
    root_window.tk.call('grid','forget',thc + '.tTlab')
    root_window.tk.call(thc + '.pid-p-gain','configure','-from','0','-to','100','-increment','1','-format','%0.0f') #25
    root_window.tk.call(thc + '.pPGlab','configure','-text','Speed (%)')
    root_window.tk.call('grid',thc + '.pid-p-gain','-row','1')
    root_window.tk.call('grid',thc + '.pPGlab','-row','1')
    root_window.tk.call('grid',thc + '.led-up','-row','0')
    root_window.tk.call('grid',thc + '.lUlab','-row','0')
    root_window.tk.call('grid',thc + '.led-down','-row','1')
    root_window.tk.call('grid',thc + '.lDlab','-row','1')
    root_window.tk.call('pack','forget',kerflock)
    root_window.tk.call('grid','forget',offsets + '.pid-i-gain')
    root_window.tk.call('grid','forget',offsets + '.pIGlab')
    root_window.tk.call('grid','forget',offsets + '.pid-d-gain')
    root_window.tk.call('grid','forget',offsets + '.pDGlab')
#    Popen('halcmd setp plasmac.mode 2', shell=True)



def set_mode(mode):
    if mode == '0':
        root_window.tk.call(thc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
    elif mode == '1':
        root_window.tk.call('grid','forget',arc + '.arc-ok-high')
        root_window.tk.call('grid','forget',arc + '.aOHlab')
        root_window.tk.call('grid','forget',arc + '.arc-ok-low')
        root_window.tk.call('grid','forget',arc + '.aOLlab')
    elif mode == '2':
        root_window.tk.call(thc + '.pid-p-gain','configure','-from','0','-to',maxPidP,'-increment','1','-format','%0.0f') #25
        root_window.tk.call('grid','forget',monitor + '.arc-voltage')
        root_window.tk.call('grid','forget',monitor + '.aVlab')
        root_window.tk.call('grid','forget',arc + '.arc-ok-high')
        root_window.tk.call('grid','forget',arc + '.aOHlab')
        root_window.tk.call('grid','forget',arc + '.arc-ok-low')
        root_window.tk.call('grid','forget',arc + '.aOLlab')
        root_window.tk.call('grid','forget',arc + '.arc-voltage-scale')
        root_window.tk.call('grid','forget',arc + '.aVSlab')
        root_window.tk.call('grid','forget',arc + '.arc-voltage-offset')
        root_window.tk.call('grid','forget',arc + '.aVOlab')
        root_window.tk.call('grid','forget',thc + '.use-auto-volts')
        root_window.tk.call('grid','forget',thc + '.uAVlab') 
        root_window.tk.call('grid','forget',thc + '.thc-threshold')
        root_window.tk.call('grid','forget',thc + '.tTlab')
        root_window.tk.call(thc + '.pid-p-gain','configure','-from','0','-to','100','-increment','1','-format','%0.0f') #25
        root_window.tk.call(thc + '.pPGlab','configure','-text','Speed (%)')
        root_window.tk.call('grid',thc + '.pid-p-gain','-row','1')
        root_window.tk.call('grid',thc + '.pPGlab','-row','1')
        root_window.tk.call('grid',thc + '.led-up','-row','0')
        root_window.tk.call('grid',thc + '.lUlab','-row','0')
        root_window.tk.call('grid',thc + '.led-down','-row','1')
        root_window.tk.call('grid',thc + '.lDlab','-row','1')
        root_window.tk.call('pack','forget',kerflock)
        root_window.tk.call('grid','forget',offsets + '.pid-i-gain')
        root_window.tk.call('grid','forget',offsets + '.pIGlab')
        root_window.tk.call('grid','forget',offsets + '.pid-d-gain')
        root_window.tk.call('grid','forget',offsets + '.pDGlab')




from subprocess import Popen, PIPE
thcFeedRate = (float(inifile.find('AXIS_Z','MAX_VELOCITY')) * \
               float(inifile.find('AXIS_Z','OFFSET_AV_RATIO'))) * 60
Popen('halcmd setp plasmac.thc-feed-rate %f' % thcFeedRate, shell=True)
configFile = inifile.find('PLASMAC','CONFIG_FILE') or inifile.find('EMC','MACHINE').lower() + '.cfg'
materialsFile = inifile.find('PLASMAC','MATERIAL_FILE') or inifile.find('EMC','MACHINE').lower() + '.mat'
materialsList = []
configDict = {}
dryRun = 0
torchPulse = 0
materialsUpdate = False
wLabels = [monitor + '.aVlab',\
           monitor + '.lTlab',\
           monitor + '.lAOlab',\
           monitor + '.lFlab',\
           monitor + '.lBlab',\
           monitor + '.lSHlab',\
           cutparms + '.pHlab',\
           cutparms + '.pDlab',\
           cutparms + '.pJHlab',\
           cutparms + '.pJDlab',\
           cutparms + '.cHlab',\
           cutparms + '.cFRlab',\
           cutparms + '.cAlab',\
           cutparms + '.cVlab',\
           thc + '.tElab',\
           thc + '.tTlab',\
           thc + '.pPGlab',\
           thc + '.uAVlab',\
           thc + '.lUlab',\
           thc + '.lDlab',\
           cornerlock + '.cElab',\
           cornerlock + '.cTlab',\
           cornerlock + '.lClab',\
           kerflock + '.kElab',\
           kerflock + '.kTlab',\
           kerflock + '.lKlab',\
           motion + '.sHlab',\
           motion + '.pFRlab',\
           motion + '.fSTlab',\
           motion + '.sIDlab',\
           arc + '.aFDlab',\
           arc + '.aVSlab',\
           arc + '.aMSlab',\
           arc + '.aVOlab',\
           arc + '.aRDlab',\
           arc + '.aOHlab',\
           arc + '.tODlab',\
           arc + '.aOLlab',\
           offsets + '.msplab',\
           offsets + '.pIGlab',\
           offsets + '.sFRlab',\
           offsets + '.pDGlab',\
           ]
wCheckbuttons = [cornerlock + '.cornerlock-enable',\
                      kerflock + '.kerfcross-enable',\
                      thc + '.thc-enable',\
                      thc + '.use-auto-volts',\
                      ]
wSpinboxes = [cutparms + '.pierce-height',\
                   cutparms + '.pierce-delay',\
                   cutparms + '.puddle-jump-height',\
                   cutparms + '.puddle-jump-delay',\
                   cutparms + '.cut-height',\
                   cutparms + '.cut-feed-rate',\
                   cutparms + '.cut-amps',\
                   cutparms + '.cut-volts',\
                   thc + '.thc-threshold',\
                   thc + '.pid-p-gain',\
                   cornerlock + '.cornerlock-threshold',\
                   kerflock + '.kerfcross-threshold',\
                   motion + '.safe-height',\
                   motion + '.float-switch-travel',\
                   motion + '.probe-feed-rate',\
                   motion + '.skip-ihs-distance',\
                   arc + '.arc-fail-delay',\
                   arc + '.arc-max-starts',\
                   arc + '.restart-delay',\
                   arc + '.torch-off-delay',\
                   arc + '.arc-voltage-scale',\
                   arc + '.arc-voltage-offset',\
                   arc + '.arc-ok-high',\
                   arc + '.arc-ok-low',\
                   offsets + '.setup-feed-rate',\
                   offsets + '.pid-i-gain',\
                   offsets + '.pid-d-gain',\
                   ]
wScalesSaved = [torch + '.torch-pulse-time']
wScalesVolatile = [override + '.height-override',\
                pausedmotion + '.paused-motion-speed',\
                ]
wComboBoxes = [material + '.materials']
wLeds = [thc + '.led-up',\
              thc + '.led-down',\
              cornerlock + '.led-cornerlock',\
              kerflock + '.led-kerfcross',\
              monitor + '.led-arc-ok',\
              monitor + '.led-torch',\
              monitor + '.led-float',\
              monitor + '.led-breakaway',\
              monitor + '.led-safe-height',\
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
Popen(['halcmd net plasmac:led-up plasmac.led-up plasmac-panel.led-up'], shell=True)
Popen(['halcmd net plasmac:led-down plasmac.led-down plasmac-panel.led-down'], shell=True)
Popen(['halcmd net plasmac:cornerlock-is-locked plasmac.cornerlock-is-locked plasmac-panel.led-cornerlock'], shell=True)
Popen(['halcmd net plasmac:kerfcross-is-locked plasmac.kerfcross-is-locked plasmac-panel.led-kerfcross'], shell=True)
Popen(['halcmd net plasmac:arc-voltage-out plasmac.arc-voltage-out plasmac-panel.arc-voltage'], shell=True)
Popen(['halcmd net plasmac:arc-ok-out plasmac.arc-ok-out plasmac-panel.led-arc-ok'], shell=True)
Popen(['halcmd net plasmac:torch-on plasmac.torch-on plasmac-panel.led-torch'], shell=True)
hal.connect('plasmac-panel.led-float','plasmac:float-switch-out')
hal.connect('plasmac-panel.led-breakaway','plasmac:breakaway-switch-out')
Popen(['halcmd net plasmac:safe-height-is-limited plasmac.safe-height-is-limited plasmac-panel.led-safe-height'], shell=True)
Popen(['halcmd net plasmac:axis-min-limit ini.z.min_limit plasmac.axis-z-min-limit'], shell=True)
Popen(['halcmd net plasmac:axis-max-limit ini.z.max_limit plasmac.axis-z-max-limit'], shell=True)
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
root_window.tk.call(motion + '.probe-feed-rate','configure','-to',widgetValues[offsets + '.setup-feed-rate'])
units = float(Popen(['halcmd getp halui.machine.units-per-mm'], stdout=PIPE, shell=True).communicate()[0].strip())
maxPidP = thcFeedRate / units * 0.1
mode = inifile.find('PLASMAC','MODE') or '0'
set_mode(mode)
commands.set_view_z()

########################################################################
#   gets widget information
#   uncomment any you need to look at, one or more at a time
#   lots more can be added

my_widget = [\
#'.',\
#'.plasmac',\
#'.plasmac.frun',\
#'.pane',\
#'.toolbar',\
#'.toolbar.view_p',\
#'.pane.top',\
#'.pane.top.tabs',\
#'.pane.top.tabs.c',\
'.pane.top.tabs.fmanual',\
#'.pane.top.tabs.fmanual.space1',\
#'.pane.top.tabs.fmanual.axis',\
#'.pane.top.tabs.fmanual.axes',\
#'.pane.top.tabs.fmanual.axes.axisx',\
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
    print '\n********** BEGIN', widget, '**********'
    print '\nwidget', widget, 'is a', root_window.tk.call('winfo','class', widget)
    print '\nparent is:', root_window.tk.call('winfo','parent', widget)
    print '\nchildren are:'
    for item in root_window.tk.call('winfo','children', widget):
        print '  ', item
    print '\nvalid options are:'
    for item in range (len(root_window.tk.call(widget,'configure'))):
        print '  ', root_window.tk.call(widget,'configure')[item]
    print '\n********** END', widget, '**********\n'

########################################################################
