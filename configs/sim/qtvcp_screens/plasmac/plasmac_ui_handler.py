############################
# **** IMPORT SECTION **** #
############################

import sys
import os
import linuxcnc
import hal
import gobject

from PyQt5 import QtCore, QtWidgets, QtGui

from qtvcp.widgets.origin_offsetview import OriginOffsetView as OFFVIEW_WIDGET
from qtvcp.widgets.dialog_widget import CamViewDialog as CAMVIEW
from qtvcp.widgets.dialog_widget import MacroTabDialog as LATHEMACRO
from qtvcp.widgets.dialog_widget import FileDialog as FILE_DIALOG
from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
from qtvcp.widgets.mdi_history import MDIHistory as MDI_HISTORY
from qtvcp.widgets.gcode_editor import GcodeEditor as GCODE
from qtvcp.lib.keybindings import Keylookup
from qtvcp.core import Status, Action, Info
from qtvcp.qt_action import FilterProgram
from qtvcp import logger
from qtvcp.widgets.stylesheeteditor import  StyleSheetEditor as SSE

from subprocess import Popen,PIPE

##########################
# *** Set up logging *** #
##########################

#LOG = logger.getLogger(__name__)
#LOG.setLevel(logger.DEBUG) # One of DEBUG, INFO, WARNING, ERROR, CRITICAL


###########################################
# **** instantiate libraries section **** #
###########################################

KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()
INFO = Info()


###################################
# **** HANDLER CLASS SECTION **** #
###################################

class HandlerClass:

    ########################
    # **** INITIALIZE **** #
    ########################
    # widgets allows access to  widgets from the qtvcp files
    # at this point the widgets and hal pins are not instantiated
    def __init__(self, halcomp,widgets,paths):
        self.hal = halcomp
        self.w = widgets
        self.stat = linuxcnc.stat()
        self.cmnd = linuxcnc.command()
        self.ini = linuxcnc.ini(os.environ['INI_FILE_NAME'])
        self.error = linuxcnc.error_channel()
        self.PATHS = paths
        self.IMAGE_PATH = paths.IMAGEDIR
        self.STYLEEDITOR = SSE(widgets,paths)

    ##########################################
    # Special Functions called from QTSCREEN
    ##########################################
    # at this point:
    # the widgets are instantiated.
    # the HAL pins are built but HAL is not set ready
    def initialized__(self):
        self.thcFeedRate = (float(self.ini.find('AXIS_Z', 'MAX_VELOCITY')) * \
                            float(self.ini.find('AXIS_Z', 'OFFSET_AV_RATIO'))) * 60
        hal.set_p('plasmac.thc-feed-rate','%f' %(int(self.thcFeedRate)))
        self.w.max_feed_rate.setText(str(int(self.thcFeedRate)))
        self.w.plasmac_settings_tabs.setTabEnabled(1, not int(self.ini.find('PLASMAC', 'CONFIG_DISABLE')))
        self.w.plasmac_settings_tabs.setCurrentIndex(0)
        self.materialsUpdate = False
        hal.set_p('plasmac.mode','%d' % (int(self.ini.find('PLASMAC','MODE') or '0')))
        self.oldMode = 0
        self.oldTaskMode = STATUS.stat.task_mode
        self.mname = self.ini.find('EMC','MACHINE')
        self.configure_widgets()
        self.load_settings()
        self.w.probe_feed_rate.setMaximum(self.w.setup_feed_rate.value())
        self.check_materials_file()
        self.get_materials()
        self.init_user_buttons()
        self.w.ho_label.setText('%d V' %(self.w.height_override.value()))
        self.w.tp_label.setText('%0.1f Sec' %((int(self.w.torch_pulse_time.value()) * 0.1)))
        self.w.pm_label.setText('%s%%' %(self.w.paused_motion_speed.value()))
        self.w.setStyleSheet(open('plasmac_ui.qss').read())
        self.w.feed_override.setMaximum(INFO.MAX_FEED_OVERRIDE)
        self.w.rapid_override.setMaximum(100)
        self.w.jog_rate.setMaximum(INFO.MAX_TRAJ_VELOCITY)
        STATUS.connect('periodic', self.periodic)
        STATUS.connect('error', self.error__)
        STATUS.connect('all-homed', self.is_homed)
        STATUS.connect('not-all-homed', self.is_not_homed)
        STATUS.connect('gcode-line-selected', lambda w, line: self.update_selected_line(line))
        STATUS.connect('general', self.dialog_return)
        self.fKeys = ('blank','blank','blank',
                      QtCore.Qt.Key_F3,QtCore.Qt.Key_F4,
                      QtCore.Qt.Key_F5,QtCore.Qt.Key_F6,
                      QtCore.Qt.Key_F7,QtCore.Qt.Key_F8,
                      QtCore.Qt.Key_F9,QtCore.Qt.Key_F10,
                      QtCore.Qt.Key_F11,QtCore.Qt.Key_F12)
        self.keyFunctions = {3:self.on_F3,4:self.on_F4,
                             5:self.on_F5,6:self.on_F6,
                             7:self.on_F7,8:self.on_F8,
                             9:self.on_F9,10:self.on_F10,
                             12:self.on_F12}
        for child in self.w.mdi_history.children():
            if isinstance(child, QtWidgets.QListView):
                child.setObjectName('mdi_list')

    def class_patch__(self):
        GCODE.exitCall = self.editor_exit

    def processed_key_event__(self,receiver,event,is_pressed,key,code,shift,cntrl):
        # when typing in widgets, we don't want keybinding to call functions
        # so we catch and process the events directly.
        # We do want ESC, F1 and F2 to call keybinding functions though
        if code not in(QtCore.Qt.Key_Escape,QtCore.Qt.Key_F1 ,QtCore.Qt.Key_F2):
            if code in self.fKeys:
                self.do_key(self.fKeys.index(code),is_pressed)
                return True
            # search for the top widget of whatever widget received the event
            # then check if it's one we want the keypress events to go to
            flag = False
            receiver2 = receiver
            while receiver2 is not None and not flag:
                if isinstance(receiver2, QtWidgets.QDialog):
                    flag = True
                    break
                if isinstance(receiver2, MDI_WIDGET):
                    flag = True
                    break
                if isinstance(receiver2, GCODE):
                    flag = True #False
                    break
                if isinstance(receiver2, MDI_HISTORY):
                    flag = True
                    break
                if receiver2.objectName() == 'plasmac_settings_tabs':
                    flag = True
                    break
                receiver2 = receiver2.parent()
                print 'receiver2', receiver2.objectName(), receiver2
            if flag:
                print 'FLAGGED', receiver2
                if isinstance(receiver2, GCODE):
                    print 'is gcode'
                    if self.w.gcoder.topMenu.isVisible():
                        print 'edit mode'
                        if is_pressed:
                            receiver.keyPressEvent(event)
                            event.accept()
                        return True
                elif is_pressed:
                    print 'pressed, not gcode'
                    receiver.keyPressEvent(event)
                    event.accept()
                    return True
                else:
                    print 'released, not gcode'
                    event.accept()
                    return True
            else:
                print 'NOT FLAGGED', receiver2
        # ok if we got here then try keybindings
        try:
            return KEYBIND.call(self,event,is_pressed,shift,cntrl)
        except NameError as e:
            LOG.debug('Exception in KEYBINDING: {}'.format (e))
            print 'NameError for %s' %(key)
        except Exception as e:
            LOG.debug('Exception in KEYBINDING:', exc_info=e)
            print 'Error in, or no function for: %s in handler file for-%s'%(KEYBIND.convert(event),key)
            return False

    def dialog_send(self):
        message = _('The machine is already homed')
        more = _('Do you wish to unhome?')
        mess = {'NAME':'MESSAGE',
                'ID':'__REHOME__',
                'ICON':'QUESTION',
                'TYPE':'False',
                'MESSAGE':message,
                'MORE': more,
                'TITLE':'HOMING REQUEST'}
        STATUS.emit('dialog-request', mess)
#                log.error('Filter Program Error:{}'.format (stderr))

    ########################
    # callbacks from STATUS #
    ########################

    def error__(self, w, kind ,error):
        if kind in (linuxcnc.NML_ERROR, linuxcnc.OPERATOR_ERROR):
            eType = 'ERROR'
        else:
            eType = 'INFO'
        print '%s: %s' %(eType,error)
        self.w.error_text.appendPlainText(eType +': ' + error)

    def is_homed(self, w):
        self.w.x_dro.setStyleSheet('color: #00B000')
        self.w.y_dro.setStyleSheet('color: #00B000')
        self.w.z_dro.setStyleSheet('color: #00B000')
        self.w.home_button.indicator_update(1)
        self.w.mdi_history.MDILine.setStyleSheet("""QLineEdit { background-color: rgb(250,250,250) }""")

    def is_not_homed(self, w, joints):
        self.w.x_dro.setStyleSheet('color: #B00000')
        self.w.y_dro.setStyleSheet('color: #B00000')
        self.w.z_dro.setStyleSheet('color: #B00000')
        self.w.home_button.indicator_update(0)
        self.w.mdi_history.MDILine.setStyleSheet("""QLineEdit { background-color: rgb(220,220,220) }""")

    def update_selected_line(self, line):
        self.selected_line = line + 1

    def dialog_return(self,w,message):
        rtn = message.get('RETURN')
        code = bool(message.get('ID') == '__REHOME__')
        name = bool(message.get('NAME') == 'MESSAGE')
        if rtn and code and name:
            print ('Entry return value from {} = {} which is a {}').format(code, rtn, type(rtn))
            if rtn:
                ACTION.SET_MACHINE_UNHOMED(-1)

    #######################
    # callbacks from form #
    #######################

    def home_clicked(self, mode):
        self.on_F3()

    def edit_clicked(self, mode):
        if hal.get_value('halui.program.is-idle'):
            self.w.gcoder.layout().setSpacing(0)
            self.w.gcoder.setGeometry(2,2,528,716)
            self.w.preview.setGeometry(532,2,490,612)
            self.w.error_text.setGeometry(532,618,490,100)
            self.w.gcoder.editMode()
            self.w.gcoder.topMenu.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.w.gcoder.bottomMenu.setFrameShape(QtWidgets.QFrame.StyledPanel)

    def spin_value_changed(self,value):
        name = 'plasmac.' + self.w.sender().objectName().replace('_','-')
        if name != 'plasmac.cut-amps':
            if name == 'plasmac.arc-max-starts':
                hal.set_p(name,str(int(value)))
            elif name == 'plasmac.arc-restart-delay':
                hal.set_p('plasmac.restart-delay',str(value))
            else:
                hal.set_p(name,str(value))

    def checkbox_changed(self,value):
        name = 'plasmac.' + self.w.sender().objectName().replace('_','-')
        if value == 0:
            hal.set_p(name,'0')
        else:
            hal.set_p(name,'1')

    def material_changed(self,index):
        if not self.materialsUpdate:
            self.w.pierce_height.setValue(self.materialsList[index][1])
            self.w.pierce_delay.setValue(self.materialsList[index][2])
            self.w.puddle_jump_height.setValue(self.materialsList[index][3])
            self.w.puddle_jump_delay.setValue(self.materialsList[index][4])
            self.w.cut_height.setValue(self.materialsList[index][5])
            self.w.cut_feed_rate.setValue(self.materialsList[index][6])
            self.w.cut_amps.setValue(self.materialsList[index][7])
            self.w.cut_volts.setValue(self.materialsList[index][8])

    def feed_override_changed(self, rate):
        ACTION.SET_FEED_RATE(rate)

    def rapid_override_changed(self, rate):
        ACTION.SET_RAPID_RATE(rate)

    def jog_rate_changed(self, rate):
        STATUS.set_jograte(float(rate))

    def height_override_changed(self, height):
        self.w.ho_label.setText('%0.1f V' %(int(height) * 0.1))
        hal.set_p('plasmac.height-override','%f' %(int(height) * 0.1))

    def torch_pulse_time_changed(self, time):
        self.w.tp_label.setText('%0.1f Sec' %(int(time) * 0.1))

    def paused_motion_speed_changed(self, speed):
        self.w.pm_label.setText('%d%%' %(int(speed)))

    def forward_pressed(self):
        speed = self.w.paused_motion_speed.value() * 0.01
        hal.set_p('plasmac.paused-motion-speed','%f' %(speed))

    def forward_released(self):
        hal.set_p('plasmac.paused-motion-speed','0')

    def reverse_pressed(self):
        speed = self.w.paused_motion_speed.value() * -0.01
        hal.set_p('plasmac.paused-motion-speed','%f' %(speed))

    def reverse_released(self):
        hal.set_p('plasmac.paused-motion-speed','0')

    def torch_pulse_start_pressed(self):
        time = self.w.torch_pulse_time.value() * 0.1
        hal.set_p('plasmac.torch-pulse-time','%f' %(time))
        hal.set_p('plasmac.torch-pulse-start','1')

    def torch_pulse_start_released(self):
        hal.set_p('plasmac.torch-pulse-start','0')
        hal.set_p('plasmac.torch-pulse-time','0')

    def ohmic_probe_pressed(self):
        pass

    def hal_scope_clicked(self):
        os.system('halscope')

    def save_clicked(self):
        self.save_settings()
        self.materialsList[0][1] = self.w.pierce_height.value()
        self.materialsList[0][2] = self.w.pierce_delay.value()
        self.materialsList[0][3] = self.w.puddle_jump_height.value()
        self.materialsList[0][4] = self.w.puddle_jump_delay.value()
        self.materialsList[0][5] = self.w.cut_height.value()
        self.materialsList[0][6] = self.w.cut_feed_rate.value()
        self.materialsList[0][7] = self.w.cut_amps.value()
        self.materialsList[0][8] = self.w.cut_volts.value()
        self.w.materials.setCurrentIndex(0)

    def reload_clicked(self):
        self.materialsUpdate = True
        self.load_settings()
        self.materialsList = []
        self.w.materials.clear()
        self.get_materials()
        self.materialsUpdate = False

    def run_from_line_clicked(self):
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state == linuxcnc.INTERP_IDLE and\
           self.selected_line:
            ACTION.RUN(self.selected_line)

    def button1_pressed(self):
        self.user_button_pressed(self.iniButtonCode[1])

    def button1_released(self):
        self.user_button_released(self.iniButtonCode[1])

    def button2_pressed(self):
        self.user_button_pressed(self.iniButtonCode[2])

    def button2_released(self):
        self.user_button_released(self.iniButtonCode[2])

    def button3_pressed(self):
        self.user_button_pressed(self.iniButtonCode[3])

    def button3_released(self):
        self.user_button_released(self.iniButtonCode[3])

    def button4_pressed(self):
        self.user_button_pressed(self.iniButtonCode[4])

    def button4_released(self):
        self.user_button_released(self.iniButtonCode[4])

    def button5_pressed(self):
        self.user_button_pressed(self.iniButtonCode[5])

    def button5_released(self):
        self.user_button_released(self.iniButtonCode[5])

    def button6_pressed(self):
        self.user_button_pressed(self.iniButtonCode[6])

    def button6_released(self):
        self.user_button_released(self.iniButtonCode[6])

    #####################
    # general functions #
    #####################

    def init_user_buttons(self):
        self.iniButtonName = ['Names']
        self.iniButtonCode = ['Codes']
        self.buttons = ['blank',self.w.button1,self.w.button2,self.w.button3,self.w.button4,self.w.button5,self.w.button6]
        for button in range(1,7):
            bname = self.ini.find('PLASMAC', 'BUTTON_' + str(button) + '_NAME') or '0'
            self.iniButtonName.append(bname)
            self.iniButtonCode.append(self.ini.find('PLASMAC', 'BUTTON_' + str(button) + '_CODE'))
            if bname != '0':
                bname = bname.split('\\')
                if len(bname) > 1:
                    blabel = bname[0] + '\n' + bname[1]
                else:
                    blabel = bname[0]
                name = 'button' + str(button)
                self.buttons[button].setText(blabel)

    def user_button_pressed(self, commands):
        if not commands: return
        if commands.lower() == 'dry-run':
            hal.set_p('plasmac.dry-run-start','1')
        elif commands.lower() == 'ohmic-test':
            hal.set_p('plasmac.ohmic-test','1')
        elif commands.lower() == 'probe-test':
            hal.set_p('plasmac.probe-test','1')
        else:
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
                                newCommand += self.ini.find(f1[1:],f2)
                                newCommand += ' '
                                subCommand = ''
                            else:
                                newCommand += char
                        if subCommand.startswith('['):
                            f1, f2 = subCommand.split()
                            newCommand += self.ini.find(f1[1:],f2)
                            newCommand += ' '
                        command = newCommand
                    if STATUS.machine_is_on() and STATUS.is_all_homed() and (STATUS.stat.interp_state == linuxcnc.INTERP_IDLE):
                        self.oldTaskMode = STATUS.stat.task_mode
                        if self.oldTaskMode != linuxcnc.MODE_MDI:
                            self.cmnd.mode(linuxcnc.MODE_MDI)
                            self.cmnd.wait_complete()
                        self.cmnd.mdi(command)

    def user_button_released(self, commands):
        if not commands: return
        if commands.lower() == 'dry-run':
            hal.set_p('plasmac.dry-run-start','0')
        elif commands.lower() == 'ohmic-test':
            hal.set_p('plasmac.ohmic-test','0')
        elif commands.lower() == 'probe-test':
            hal.set_p('plasmac.probe-test','0')

    def editor_exit(self):
        if self.w.gcoder.editor.isModified():
            result = self.w.gcoder.killCheck()
            if result:
                self.w.gcoder.editor.reload_last(self)
                self.w.gcoder.setGeometry(532,418,300,300)
                self.w.preview.setGeometry(532,54,490,360)
                self.w.error_text.setGeometry(836,618,186,100)
                self.w.gcoder.readOnlyMode()
        else:
            self.w.gcoder.setGeometry(532,418,300,300)
            self.w.preview.setGeometry(532,54,490,360)
            self.w.error_text.setGeometry(836,618,186,100)
            self.w.gcoder.readOnlyMode()

    # keyboard jogging from key binding calls
    # double the rate if fast is true 
    def kb_jog(self, state, joint, direction, fast = False, linear = True):
        if linear:
            distance = STATUS.get_jog_increment()
            rate = STATUS.get_jograte()/60
        else:
            distance = STATUS.get_jog_increment_angular()
            rate = STATUS.get_jograte_angular()/60
        if state:
            if fast:
                rate = rate * 2
            ACTION.JOG(joint, direction, rate, distance)
        else:
            ACTION.JOG(joint, 0, 0, 0)

    def configure_widgets(self):
        if self.ini.find('TRAJ', 'LINEAR_UNITS').lower() == 'mm':
            self.w.cut_feed_rate.setDecimals(0)
            self.w.cut_feed_rate.setRange(50,9999)
            self.w.cut_height.setDecimals(1)
            self.w.cut_height.setRange(0,25.4)
            self.w.float_switch_travel.setDecimals(2)
            self.w.float_switch_travel.setRange(0,9)
            self.w.pierce_height.setDecimals(1)
            self.w.pierce_height.setRange(0,25.4)
            self.w.probe_feed_rate.setDecimals(0)
            self.w.probe_feed_rate.setRange(1,self.thcFeedRate)
            self.w.safe_height.setDecimals(0)
            self.w.safe_height.setRange(1,99)
            self.w.setup_feed_rate.setDecimals(0)
            self.w.setup_feed_rate.setRange(1,self.thcFeedRate)
            self.w.skip_ihs_distance.setDecimals(0)
            self.w.skip_ihs_distance.setRange(0,999)
        elif self.ini.find('TRAJ', 'LINEAR_UNITS').lower() == 'inch':
            self.w.cut_feed_rate.setDecimals(1)
            self.w.cut_feed_rate.setRange(2,400)
            self.w.cut_height.setDecimals(2)
            self.w.cut_height.setRange(0,1)
            self.w.float_switch_travel.setDecimals(3)
            self.w.float_switch_travel.setRange(0,1)
            self.w.pierce_height.setDecimals(2)
            self.w.pierce_height.setRange(0,1)
            self.w.probe_feed_rate.setDecimals(1)
            self.w.probe_feed_rate.setRange(0.1,self.thcFeedRate)
            self.w.safe_height.setDecimals(2)
            self.w.safe_height.setRange(0.04,4)
            self.w.setup_feed_rate.setDecimals(1)
            self.w.setup_feed_rate.setRange(0.1,self.thcFeedRate)
            self.w.skip_ihs_distance.setDecimals(1)
            self.w.skip_ihs_distance.setRange(0,99)
        else:
            print '*** incorrect [TRAJ]LINEAR_UNITS in ini file'

    def load_settings(self):
        self.configFile = self.ini.find('EMC', 'MACHINE').lower() + '.cfg'
        self.configDict = {}
        self.config_widgets = ['pierce_height','pierce_delay','puddle_jump_height',\
                               'puddle_jump_delay','cut_height','cut_feed_rate',\
                               'cut_amps','cut_volts','thc_enable','use_auto_volts',\
                               'thc_threshold','pid_p_gain','cornerlock_enable',\
                               'cornerlock_threshold','kerfcross_enable',\
                               'kerfcross_threshold','safe_height',\
                               'float_switch_travel','probe_feed_rate','skip_ihs_distance',\
                               'arc_fail_delay','arc_max_starts','arc_restart_delay',\
                               'torch_off_delay','arc_voltage_scale','arc_voltage_offset',\
                               'arc_ok_high','arc_ok_low','setup_feed_rate','pid_i_gain',\
                               'pid_d_gain','paused-motion-speed','torch-pulse-time',\
                               ]
        for item in self.config_widgets:
            self.configDict[item.replace('_','-')] = '0'
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
            for item in sorted(self.configDict):
                widget = getattr(self.w,item.replace('-','_'),None)
                if isinstance(widget,QtWidgets.QDoubleSpinBox):
                    if item in tmpDict:
                        if item == 'puddle-jump-height' and float(self.configDict.get(item)) < 50:
                            widget.setValue(100)
                        else:
                            widget.setValue(float(self.configDict.get(item)))
                    else:
                        if item == 'puddle-jump-height':
                            widget.setValue(100)
                        else:
                            widget.setValue(0)
                            print '***', item, 'missing from', self.configFile
                elif isinstance(widget, QtWidgets.QCheckBox):
                    if item in tmpDict:
                        if int(self.configDict.get(item)) == 0:
                            widget.setCheckState(0)
                        else:
                            widget.setCheckState(2)
                    else:
                        widget.setCheckState(False)
                        print '***', item, 'missing from', self.configFile
                elif item == 'torch-pulse-time':
                    if item in tmpDict:
                        widget.setValue(int(float(self.configDict.get(item)) * 10))
                    else:
                        widget.setValue(0)
                        print '***', item, 'missing from', self.configFile
                elif item == 'paused-motion-speed':
                    if item in tmpDict:
                        widget.setValue(int(float(self.configDict.get(item)) * 100))
                    else:
                        widget.setValue(0)
                        print '***', item, 'missing from', self.configFile
                else:
                    print item, 'does not exist'
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
                for key in sorted(self.configDict.iterkeys()):
                    widget = getattr(self.w,key.replace('-','_'),None)
                    if isinstance(widget, QtWidgets.QDoubleSpinBox):
                        value = widget.value()
                        f_out.write(key + '=' + str(value) + '\n')
                    elif isinstance(widget, QtWidgets.QCheckBox):
                        value = widget.checkState()
                        f_out.write(key + '=' + str(value) + '\n')
                    elif key == 'torch-pulse-time':
                        value = widget.value() * 0.1
                        f_out.write(key + '=' + str(value) + '\n')
                    elif key == 'paused-motion-speed':
                        value = widget.value() * 0.01
                        f_out.write(key + '=' + str(value) + '\n')
        except:
            print '*** error opening', self.configFile

    def check_materials_file(self):
        self.materialsFile = self.ini.find('EMC','MACHINE').lower() + '.mat'
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
            with open(self.materialsFile, 'w') as f_out:
                f_out.write(header)
            print '*** new material file,', self.materialsFile, 'created'

    def get_materials(self):
        self.materialsList = []
        name = 'Default'
        p_height = self.w.pierce_height.value()
        p_delay = self.w.pierce_delay.value()
        pj_height = self.w.puddle_jump_height.value()
        pj_delay = self.w.puddle_jump_delay.value()
        c_height = self.w.cut_height.value()
        c_speed = self.w.cut_feed_rate.value()
        c_amps = self.w.cut_amps.value()
        c_volts = self.w.cut_volts.value()
        try:
            with open(self.materialsFile, 'r') as f_in:
                for line in f_in:
                    if not line.startswith('#'):
                        if line.startswith('[') and line.strip().endswith(']') and not 'VERSION' in line:
                            self.materialsList.append([name, p_height, p_delay, pj_height, pj_delay, c_height, c_speed, c_amps, c_volts])
                            self.w.materials.addItem(name)
                            name = line.strip().lstrip('[').rstrip(']')
                            p_height = p_delay = pj_height = pj_delay = c_height = c_speed = c_amps = c_volts = 0
                        elif line.startswith('PIERCE_HEIGHT'):
                            p_height = float(line.split('=')[1].strip())
                        elif line.startswith('PIERCE_DELAY'):
                            p_delay = float(line.split('=')[1].strip())
                        elif line.startswith('PUDDLE_JUMP_HEIGHT'):
                            if float(line.split('=')[1].strip()) < 50:
                                pj_height = 100
                            else:
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
                self.w.materials.addItem(name)
                self.w.materials.setCurrentIndex(0)
        except:
            print '*** materials file,', self.materialsFile, 'is invalid'
        finally:
            f_in.close()

    def set_mode(self, mode):
        units = hal.get_value('halui.machine.units-per-mm')
        maxPidP = self.thcFeedRate / units * 0.1
        if mode == 0:
            self.w.arc_ok_high.show()
            self.w.aOHLabel.show()
            self.w.arc_ok_low.show()
            self.w.aOLLabel.show()
            if self.oldMode == 1:
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() + 52)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() + 52)
                self.w.settings_frame.move(self.w.settings_frame.geometry().left(), self.w.settings_frame.geometry().top() + 52)
            else:
                self.w.arc_voltage.show()
                self.w.aVLabel.setText('Arc Voltage')
                self.w.height_override.show()
                self.w.ho_label.show()
                self.w.ho_label_1.show()
                self.w.cut_volts.show()
                self.w.cVLabel.show()
                self.w.cut_frame.resize(self.w.cut_frame.geometry().width(), self.w.cut_frame.geometry().height() + 26)
                self.w.thc_frame.move(self.w.thc_frame.geometry().left(), self.w.thc_frame.geometry().top() + 26)
                self.w.use_auto_volts.show()
                self.w.pid_p_gain.setRange(1, maxPidP)
                self.w.pPLabel.setText('Speed (PID P)')
                self.w.thc_threshold.show()
                self.w.tTLabel.show()
                self.w.pid_p_gain.move(self.w.pid_p_gain.geometry().left(), self.w.pid_p_gain.geometry().top() + 52)
                self.w.pPLabel.move(self.w.pPLabel.geometry().left(), self.w.pPLabel.geometry().top() + 52)
                self.w.up_led.move(self.w.up_led.geometry().left(), self.w.up_led.geometry().top() + 52)
                self.w.lULabel.move(self.w.lULabel.geometry().left(), self.w.lULabel.geometry().top() + 52)
                self.w.down_led.move(self.w.down_led.geometry().left(), self.w.down_led.geometry().top() + 52)
                self.w.lDLabel.move(self.w.lULabel.geometry().left(), self.w.lDLabel.geometry().top() + 52)
                self.w.thc_frame.resize(self.w.thc_frame.geometry().width(), self.w.thc_frame.geometry().height() + 52)
                self.w.corner_frame.move(self.w.corner_frame.geometry().left(), self.w.corner_frame.geometry().top() + 78)
                self.w.kerf_frame.show()
                self.w.arc_voltage_scale.show()
                self.w.aVSLabel.show()
                self.w.arc_voltage_offset.show()
                self.w.aVOLabel.show()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() + 104)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() + 104)
                self.w.pid_i_gain.show()
                self.w.pILabel.show()
                self.w.pid_d_gain.show()
                self.w.pDLabel.show()
                self.w.offsets_frame.resize(self.w.offsets_frame.geometry().width(), self.w.offsets_frame.geometry().height() + 52)
                self.w.settings_frame.move(self.w.settings_frame.geometry().left(), self.w.settings_frame.geometry().top() + 156)
        elif mode == 1:
            if self.oldMode == 0:
                self.w.arc_ok_high.close()
                self.w.aOHLabel.close()
                self.w.arc_ok_low.close()
                self.w.aOHLabel.close()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() - 52)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() - 52)
                self.w.settings_frame.move(self.w.settings_frame.geometry().left(), self.w.settings_frame.geometry().top() - 52)
            else:
                self.w.arc_voltage.show()
                self.w.aVLabel.setText('Arc Voltage')
                self.w.height_override.show()
                self.w.ho_label.show()
                self.w.ho_label_1.show()
                self.w.cut_volts.show()
                self.w.cVLabel.show()
                self.w.cut_frame.resize(self.w.cut_frame.geometry().width(), self.w.cut_frame.geometry().height() + 26)
                self.w.thc_frame.move(self.w.thc_frame.geometry().left(), self.w.thc_frame.geometry().top() + 26)
                self.w.use_auto_volts.show()
                self.w.pid_p_gain.setRange(1, 100)
                self.w.pPLabel.setText('Speed (%)')
                self.w.thc_threshold.show()
                self.w.tTLabel.show()
                self.w.pid_p_gain.move(self.w.pid_p_gain.geometry().left(), self.w.pid_p_gain.geometry().top() + 52)
                self.w.pPLabel.move(self.w.pPLabel.geometry().left(), self.w.pPLabel.geometry().top() + 52)
                self.w.up_led.move(self.w.up_led.geometry().left(), self.w.up_led.geometry().top() + 52)
                self.w.lULabel.move(self.w.lULabel.geometry().left(), self.w.lULabel.geometry().top() + 52)
                self.w.down_led.move(self.w.down_led.geometry().left(), self.w.down_led.geometry().top() + 52)
                self.w.lDLabel.move(self.w.lULabel.geometry().left(), self.w.lDLabel.geometry().top() + 52)
                self.w.thc_frame.resize(self.w.thc_frame.geometry().width(), self.w.thc_frame.geometry().height() + 52)
                self.w.corner_frame.move(self.w.corner_frame.geometry().left(), self.w.corner_frame.geometry().top() + 78)
                self.w.kerf_frame.show()
                self.w.arc_voltage_scale.show()
                self.w.aVSLabel.show()
                self.w.arc_voltage_offset.show()
                self.w.aVOLabel.show()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() + 52)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() + 52)
                self.w.pid_i_gain.show()
                self.w.pILabel.show()
                self.w.pid_d_gain.show()
                self.w.pDLabel.show()
                self.w.offsets_frame.resize(self.w.offsets_frame.geometry().width(), self.w.offsets_frame.geometry().height() + 52)
                self.w.settings_frame.move(self.w.settings_frame.geometry().left(), self.w.settings_frame.geometry().top() + 104)
        elif mode == 2:
            self.w.arc_voltage.close()
            self.w.aVLabel.setText('')
            self.w.height_override.close()
            self.w.ho_label.close()
            self.w.ho_label_1.close()
            self.w.cut_volts.close()
            self.w.cVLabel.close()
            self.w.cut_frame.resize(self.w.cut_frame.geometry().width(), self.w.cut_frame.geometry().height() - 26)
            self.w.thc_frame.move(self.w.thc_frame.geometry().left(), self.w.thc_frame.geometry().top() - 26)
            self.w.use_auto_volts.close()
            self.w.pid_p_gain.setRange(1, 100)
            self.w.pPLabel.setText('Speed (%)')
            self.w.thc_threshold.close()
            self.w.tTLabel.close()
            self.w.pid_p_gain.move(self.w.pid_p_gain.geometry().left(), self.w.pid_p_gain.geometry().top() - 52)
            self.w.pPLabel.move(self.w.pPLabel.geometry().left(), self.w.pPLabel.geometry().top() - 52)
            self.w.up_led.move(self.w.up_led.geometry().left(), self.w.up_led.geometry().top() - 52)
            self.w.lULabel.move(self.w.lULabel.geometry().left(), self.w.lULabel.geometry().top() - 52)
            self.w.down_led.move(self.w.down_led.geometry().left(), self.w.down_led.geometry().top() - 52)
            self.w.lDLabel.move(self.w.lULabel.geometry().left(), self.w.lDLabel.geometry().top() - 52)
            self.w.thc_frame.resize(self.w.thc_frame.geometry().width(), self.w.thc_frame.geometry().height() - 52)
            self.w.corner_frame.move(self.w.corner_frame.geometry().left(), self.w.corner_frame.geometry().top() - 78)
            self.w.kerf_frame.close()
            self.w.arc_voltage_scale.close()
            self.w.aVSLabel.close()
            self.w.arc_voltage_offset.close()
            self.w.aVOLabel.close()
            self.w.pid_i_gain.close()
            self.w.pILabel.close()
            self.w.pid_d_gain.close()
            self.w.pDLabel.close()
            self.w.offsets_frame.resize(self.w.offsets_frame.geometry().width(), self.w.offsets_frame.geometry().height() - 52)
            if self.oldMode == 0:
                self.w.arc_ok_high.close()
                self.w.aOHLabel.close()
                self.w.arc_ok_low.close()
                self.w.aOLLabel.close()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() - 104)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() - 104)
                self.w.settings_frame.move(self.w.settings_frame.geometry().left(), self.w.settings_frame.geometry().top() - 156)
            else:
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() - 52)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() - 52)
                self.w.settings_frame.move(self.w.settings_frame.geometry().left(), self.w.settings_frame.geometry().top() - 104)
        else:
            print mode, 'is an invalid plasmac mode...'
        self.oldMode = mode

    ###############################
    # PERIODIC CALLED EVERY 100mS #
    ###############################

    def periodic(self, w):
        if self.ini.find('PLASMAC', 'DEBUG') == '1':
            self.w.mdi_history.setEnabled(True)
            self.w.mdi_history.MDILine.setEnabled(True)
        if STATUS.stat.interp_state == linuxcnc.INTERP_IDLE and STATUS.stat.task_mode != self.oldTaskMode and self.oldTaskMode > 0:
            self.cmnd.mode(self.oldTaskMode)
            self.cmnd.wait_complete()
        self.w.feed_override.setValue(STATUS.stat.feedrate * 100)
        self.w.rapid_override.setValue(STATUS.stat.rapidrate * 100)
        self.w.jog_rate.setValue(STATUS.get_jograte())
        if STATUS.is_metric_mode():
            self.w.jog_rate_status._set_text(STATUS.get_jograte())
        else:
            self.w.jog_rate_status._set_alt_text(STATUS.get_jograte())
        fname = STATUS.stat.file.split('/')[-1]
        self.w.setWindowTitle('PLASMAP   ' + self.mname + '   ' + fname)
        if STATUS.is_metric_mode():
            units = 'Metric     '
        else:
            units = 'Inch       '
        self.w.statusBar.showMessage(units + \
                              STATUS['old']['g-code'].replace(' ',',')[0:-1] + \
                              '     ' + \
                              STATUS['old']['m-code'].replace(' ',',')[3:-1] \
                              , 0)
        if STATUS.machine_is_on() and hal.get_value('halui.program.is-idle'):
            self.w.home_button.setEnabled(True)
            self.w.edit_button.setEnabled(True)
            self.w.run_from_button.setEnabled(True)
            self.w.torch_pulse_start.setEnabled(True)
            self.w.reverse.setEnabled(False)
            self.w.forward.setEnabled(False)
        elif STATUS.machine_is_on() and \
            (hal.get_value('halui.program.is-paused') or self.w.reverse.isDown() or self.w.forward.isDown()):
            self.w.home_button.setEnabled(False)
            self.w.edit_button.setEnabled(False)
            self.w.run_from_button.setEnabled(False)
            self.w.torch_pulse_start.setEnabled(False)
            self.w.reverse.setEnabled(True)
            self.w.forward.setEnabled(True)
        else:
            self.w.home_button.setEnabled(False)
            self.w.edit_button.setEnabled(False)
            self.w.run_from_button.setEnabled(False)
            self.w.torch_pulse_start.setEnabled(False)
            self.w.reverse.setEnabled(False)
            self.w.forward.setEnabled(False)
        if STATUS.machine_is_on() and not hal.get_value('plasmac.arc-ok-out'):
            isOn = True
        else:
            isOn = False
        for n in range(1,7):
            if self.iniButtonCode[n] in ['ohmic-test']:
                if isOn:
                    self.buttons[n].setEnabled(True)
                else:
                    self.buttons[n].setEnabled(False)
            elif not self.iniButtonCode[n] in ['ohmic-test'] and not self.iniButtonCode[n].startswith('%'):
                if STATUS.machine_is_on() and STATUS.is_all_homed():
                    self.buttons[n].setEnabled(True)
                    if self.iniButtonCode[n] == 'dry-run' and not STATUS.is_file_loaded():
                        self.buttons[n].setEnabled(False)
                else:
                    self.buttons[n].setEnabled(False)
        self.w.plasmac_settings_tabs.setTabEnabled(1, not hal.get_value('plasmac_ui.config_disable'))
        mode = hal.get_value('plasmac.mode')
        if mode != self.oldMode: self.set_mode(mode)
        return True

    #####################
    # KEY BINDING CALLS #
    #####################

    def on_keycall_ESTOP(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_ESTOP_STATE(STATUS.estop_is_clear())

    def on_keycall_POWER(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_MACHINE_STATE(not STATUS.machine_is_on())

    def on_keycall_ABORT(self,event,state,shift,cntrl):
        if state:
            if STATUS.stat.interp_state != linuxcnc.INTERP_IDLE:
                self.cmnd.abort()

    # Linear Jogging
    def on_keycall_XPOS(self,event,state,shift,cntrl):
        if state:
            print 'xpos on'
        else:
            print 'xpos off'
        #self.kb_jog(state, 0, 1, shift)

    def on_keycall_XNEG(self,event,state,shift,cntrl):
        if state:
            print 'xneg on'
        else:
            print 'xneg off'
        #self.kb_jog(state, 0, -1, shift)

    def on_keycall_YPOS(self,event,state,shift,cntrl):
        if state:
            print 'ypos on'
        else:
            print 'ypos off'
        #self.kb_jog(state, 1, 1, shift)

    def on_keycall_YNEG(self,event,state,shift,cntrl):
        if state:
            print 'yneg on'
        else:
            print 'yneg off'
        #self.kb_jog(state, 1, -1, shift)

    def on_keycall_ZPOS(self,event,state,shift,cntrl):
        if state:
            print 'zpos on'
        else:
            print 'zpos off'
        #self.kb_jog(state, 2, 1, shift)

    def on_keycall_ZNEG(self,event,state,shift,cntrl):
        if state:
            print 'zneg on'
        else:
            print 'zneg off'
        #self.kb_jog(state, 2, -1, shift)

    #######################
    # LOCAL KEY FUNCTIONS #
    #######################

    def do_key(self,key,is_pressed):
        if not is_pressed: return
        self.keyFunctions[key]()

    def on_F3(self): # home all
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state == linuxcnc.INTERP_IDLE and\
           not self.w.gcoder.topMenu.isVisible():
            if not STATUS.is_all_homed():
                ACTION.SET_MACHINE_HOMING(-1)
            else:
                self.dialog_send()

    def on_F4(self): # open file
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state == linuxcnc.INTERP_IDLE and\
           not self.w.gcoder.topMenu.isVisible():
            STATUS.emit('dialog-request',{'NAME':'LOAD'})

    def on_F5(self): # run program
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state == linuxcnc.INTERP_IDLE and\
           STATUS.stat.file and\
           not self.w.gcoder.topMenu.isVisible():
            ACTION.RUN()

    def on_F6(self): # pause/resume program
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state != linuxcnc.INTERP_IDLE and\
           not self.w.gcoder.topMenu.isVisible():
            ACTION.PAUSE()

    def on_F7(self): # abort program
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state != linuxcnc.INTERP_IDLE :
            ACTION.ABORT()

    def on_F8(self): # run from line
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state == linuxcnc.INTERP_IDLE and\
           STATUS.stat.file and\
           not self.w.gcoder.topMenu.isVisible():
            self.run_from_line_clicked()

    def on_F9(self): # edit gcode
        if STATUS.stat.task_state == linuxcnc.STATE_ON and\
           STATUS.stat.interp_state == linuxcnc.INTERP_IDLE:
            self.edit_clicked(0)

    def on_F10(self): # clear backplot
        ACTION.SET_GRAPHICS_VIEW('clear')

    def on_F12(self): # stylesheet editor
        if STATUS.stat.interp_state == linuxcnc.INTERP_IDLE:
            self.STYLEEDITOR.load_dialog()

    ###########################
    # **** closing event **** #
    ###########################

    ##############################
    # required class boiler code #
    ##############################

    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        return setattr(self, item, value)

################################
# required handler boiler code #
################################

def get_handlers(halcomp,widgets,paths):
     return [HandlerClass(halcomp,widgets,paths)]
