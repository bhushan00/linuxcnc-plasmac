############################
# **** IMPORT SECTION **** #
############################

from PyQt5 import QtCore, QtWidgets
from qtvcp.widgets.origin_offsetview import OriginOffsetView as OFFVIEW_WIDGET
from qtvcp.widgets.dialog_widget import CamViewDialog as CAMVIEW
from qtvcp.widgets.dialog_widget import MacroTabDialog as LATHEMACRO
from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
from qtvcp.lib.keybindings import Keylookup
from qtvcp.core import Status, Action

# Set up logging
from qtvcp import logger
log = logger.getLogger(__name__)

import linuxcnc
import sys
import os
import hal
import gobject

###########################################
# **** instantiate libraries section **** #
###########################################

KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()

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

    ##########################################
    # Special Functions called from QTSCREEN
    ##########################################
    # at this point:
    # the widgets are instantiated.
    # the HAL pins are built but HAL is not set ready
    def initialized__(self):
        self.thcFeedRate = (float(self.ini.find('AXIS_Z', 'MAX_VELOCITY')) * \
                            float(self.ini.find('AXIS_Z', 'OFFSET_AV_RATIO'))) * 60
        hal.set_p('plasmac.thc-feed-rate','%f' % (int(self.thcFeedRate)))
        self.w.max_feed_rate.setText(str(int(self.thcFeedRate)))
        self.w.plasmac_settings_tabs.setTabEnabled(1, not int(self.ini.find('PLASMAC', 'CONFIG_DISABLE')))
        self.materialsUpdate = False
        self.oldMode = 0
        self.configure_widgets()
        self.load_settings()
        self.w.probe_feed_rate.setMaximum(self.w.setup_feed_rate.value())
        self.check_materials_file()
        self.get_materials()




        gobject.timeout_add(100, self.periodic)


    def your_function(a,b):
        print 'double clicked'
        print a
        print b
        
    def processed_key_event__(self,receiver,event,is_pressed,key,code,shift,cntrl):
        # when typing in MDI, we don't want keybinding to call functions
        # so we catch and process the events directly.
        # We do want ESC, F1 and F2 to call keybinding functions though
        if code not in(QtCore.Qt.Key_Escape,QtCore.Qt.Key_F1 ,QtCore.Qt.Key_F2,
                    QtCore.Qt.Key_F3,QtCore.Qt.Key_F5,QtCore.Qt.Key_F5):
            if isinstance(receiver, OFFVIEW_WIDGET)\
            or isinstance(receiver, MDI_WIDGET)\
            or isinstance(receiver, QtWidgets.QDoubleSpinBox):
                if is_pressed:
                    receiver.keyPressEvent(event)
                    event.accept()
                return True
            if isinstance(receiver,QtWidgets.QDialog):
                print 'dialog'
                return True
        try:
            KEYBIND.call(self,event,is_pressed,shift,cntrl)
            return True
        except Exception as e:
            #log.debug('Exception loading Macros:', exc_info=e)
            print 'Error in, or no function for: %s in handler file for-%s'%(KEYBIND.convert(event),key)
            if e:
                print e
            #print 'from %s'% receiver
            return False

    ########################
    # callbacks from STATUS #
    ########################

    #######################
    # callbacks from form #
    #######################

    def edit_clicked(self, mode):
        if self.w.gcoder.width() == 300:
            print 'editing'
            self.w.edit_button.setText('View')
            self.w.gcoder.setGeometry(522,434,500,308)
            self.w.gcoder.editMode()
        elif self.w.gcoder.width() == 500:
            print 'gcode edit'
            self.w.edit_button.setText('Edit')
            self.w.gcoder.setGeometry(522,434,300,256)
            self.w.gcoder.readOnlyMode()
        else:
            print 'unknown'
            

#        print 'mode =',mode
        #if mode == 0:
        #    self.w.gcode_editor.readOnlyMode()
        #else:
        #    self.w.gcode_editor.editMode()
#        self.w.stackedWidget.setCurrentWidget(self.w.GcodeEdit)
#        print self.w.stackedWidget.currentWidget()
#        self.w.gcode_editor.editMode()

    def spin_value_changed(self,value):
        name = 'plasmac.' + self.w.sender().objectName().replace('_','-')
        if name != 'plasmac.cut-amps':
            if name == 'plasmac.arc-max-starts':
                hal.set_p(name,str(int(value)))
                pass
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

    def x_to_home_clicked(self):
        print 'x to home'
        self.goto_home('X')

    def y_to_home_clicked(self):
        print 'y to home'
        self.goto_home('Y')

    def z_to_home_clicked(self):
        print 'z to home'
        self.goto_home('Z')

    def goto_home(self,axis):
        if hal.get_value('halui.program.is-idle'):
            home = self.ini.find('JOINT_' + str(self.ini.find('TRAJ', 'COORDINATES').upper().index(axis)), 'HOME')
#            mode = hal.get_value('halui.mode.is-mdi')
#            if not mode:
            if not hal.get_value('halui.mode.is-mdi'):
                self.cmnd.mode(linuxcnc.MODE_MDI)
            self.cmnd.mdi('G53 G0 ' + axis + home)

    def height_override_changed(self, height):
        self.w.ho_label.setText('%d' % height)
        hal.set_p('plasmac.height-override','%f' %(height))

    def torch_pulse_time_changed(self, time):
        bob = float(time) * 0.1
        print time,type(time)
        self.w.tp_label.setText('%0.1f Sec' % (float(time) * 0.1))
        print 'TORCH PULSE TIME CHANGED'
        print float(time) * 0.1

    def paused_motion_speed_changed(self, speed):
        self.w.pm_label.setText('%s%%' % speed)
        print 'MOTION SPEED CHANGED'
        print float(speed) * 0.1

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

    def hal_scope_clicked(self):
        print 'launch halscope'
        os.system('halscope')

    #####################
    # general functions #
    #####################

#    def mouseDoubleClickEvent(self, event):
#        #name = 'plasmac.' + self.w.sender().objectName().replace('_','-')
#        widget = self.w.sender()
#        print widget
#        #widget = self.childAt(event.pos())
##        if widget is not None and widget.objectName():
##            print('dblclick:', widget.objectName())

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
                               'cut_amps','cut_volts','thc_enable','use_auto_volts',
                               'thc_threshold','pid_p_gain','up_led','down_led',\
                               'cornerlock_enable','cornerlock_threshold',\
                               'kerfcross_enable','kerfcross_threshold','safe_height',\
                               'float_switch_travel','probe_feed_rate','skip_ihs_distance',\
                               'arc_fail_delay','arc_max_starts','restart_delay',\
                               'torch_off_delay','arc_voltage_scale','arc_voltage_offset',\
                               'arc_ok_high','arc_ok_low','setup_feed_rate','pid_i_gain',\
                               'pid_d_gain',\
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
                        widget.setValue(float(self.configDict.get(item)))
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
                elif item == 'torch-pulse-time' or item == 'paused-motion-speed':
                    if item in tmpDict:
                        widget.setValue(float(self.configDict.get(item)))
                    else:
                        widget.setValue(0)
                        print '***', item, 'missing from', self.configFile
#                else:
#                    print getattr(self.w,item.replace('-','_'),None), 'is invalid'
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
                    elif key == 'torchPulseTime' or key == 'pausedMotionSpeed':
                        value = widget.getValue()
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
            #self.w.arc_voltage.show()
            #self.w.aVLabel.setText('Arc Voltage')
            #self.w.height_frame.show()     # HEIGHT OVERRIDE
            if self.oldMode == 1:
                self.w.arc_ok_high.show()
                self.w.aOHLabel.show()
                self.w.arc_ok_low.show()
                self.w.aOHLabel.show()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() + 52)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() + 52)
            else:
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
                self.w.arc_ok_high.show()
                self.w.aOHLabel.show()
                self.w.arc_ok_low.show()
                self.w.aOLLabel.show()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() + 104)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() + 104)
                self.w.pid_i_gain.show()
                self.w.pILabel.show()
                self.w.pid_d_gain.show()
                self.w.pDLabel.show()
                self.w.offsets_frame.resize(self.w.offsets_frame.geometry().width(), self.w.offsets_frame.geometry().height() + 52)
                self.w.run_tab.resize(self.w.run_tab.geometry().width(), self.w.run_tab.geometry().height() + 181)
                self.w.config_tab.resize(self.w.config_tab.geometry().width(), self.w.config_tab.geometry().height() + 181)
                self.w.plasmac_settings_tabs.resize(self.w.plasmac_settings_tabs.geometry().width(), self.w.plasmac_settings_tabs.geometry().height() + 181)


        elif mode == 1:
            if self.oldMode == 0:
                self.w.arc_ok_high.close()
                self.w.aOHLabel.close()
                self.w.arc_ok_low.close()
                self.w.aOHLabel.close()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() - 52)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() - 52)
            else:
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
        elif mode == 2:
            if self.oldMode == 0:
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
                self.w.arc_ok_high.close()
                self.w.aOHLabel.close()
                self.w.arc_ok_low.close()
                self.w.aOLLabel.close()
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() - 104)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() - 104)
                self.w.pid_i_gain.close()
                self.w.pILabel.close()
                self.w.pid_d_gain.close()
                self.w.pDLabel.close()
                self.w.offsets_frame.resize(self.w.offsets_frame.geometry().width(), self.w.offsets_frame.geometry().height() - 52)
                self.w.run_tab.resize(self.w.run_tab.geometry().width(), self.w.run_tab.geometry().height() - 181)
                self.w.config_tab.resize(self.w.config_tab.geometry().width(), self.w.config_tab.geometry().height() - 181)
                self.w.plasmac_settings_tabs.resize(self.w.plasmac_settings_tabs.geometry().width(), self.w.plasmac_settings_tabs.geometry().height() - 181)
            else:
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
                self.w.arc_frame.resize(self.w.arc_frame.geometry().width(), self.w.arc_frame.geometry().height() - 52)
                self.w.offsets_frame.move(self.w.offsets_frame.geometry().left(), self.w.offsets_frame.geometry().top() - 52)
                self.w.pid_i_gain.close()
                self.w.pILabel.close()
                self.w.pid_d_gain.close()
                self.w.pDLabel.close()
                self.w.offsets_frame.resize(self.w.offsets_frame.geometry().width(), self.w.offsets_frame.geometry().height() - 52)
        else:
            pass
        self.oldMode = mode

    ###############################
    # PERIODIC CALLED EVERY 100mS #
    ###############################
    
    def periodic(self):
        self.stat.poll()
        gcodeRaw = []
        for n in self.stat.gcodes:
            if n > 0:
                if n % 10:
                    gcodeRaw.append(float(str(n/10) + '.' + str(n %10)))
                else:
                    gcodeRaw.append(n/10)
        gcodeSorted = sorted(gcodeRaw)
        if 21 in gcodeSorted:
            gCode ='METRIC     '
        else:
            gCode ='INCH     '
        for code in range(len(gcodeSorted)):
            gCode = gCode + 'G' + str(gcodeSorted[code]) + ','
        mCodeRaw = []
        for n in self.stat.mcodes:
            if n > 0: mCodeRaw.append(n)
        mCodeSorted = sorted(mCodeRaw)
        mCode =''
        for code in range(len(mCodeSorted)):
            mCode = mCode + 'M' + str(mCodeSorted[code]) + ','
        self.w.status.setText(gCode[0:-1] + '     ' + mCode[0:-1])

#        if hal.get_value('halui.program.is-idle'):
#            self.builder.get_object('pausedMotionSpeedAdj').set_value(0)
        self.w.plasmac_settings_tabs.setTabEnabled(1, not hal.get_value('plasmac_ui.config_disable'))
        mode = hal.get_value('plasmac.mode')
        if mode != self.oldMode: self.set_mode(mode)
        return True

    #####################
    # KEY BINDING CALLS #
    #####################

    # Machine control
    def on_keycall_ESTOP(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_ESTOP_STATE(STATUS.estop_is_clear())
    def on_keycall_POWER(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_MACHINE_STATE(not STATUS.machine_is_on())
    def on_keycall_HOME(self,event,state,shift,cntrl):
        if state:
            if STATUS.is_all_homed():
                ACTION.SET_MACHINE_UNHOMED(-1)
            else:
                ACTION.SET_MACHINE_HOMING(-1)
    def on_keycall_ABORT(self,event,state,shift,cntrl):
        if state:
            if STATUS.stat.interp_state == linuxcnc.INTERP_IDLE:
                self.w.close()
            else:
                self.cmnd.abort()

    # Linear Jogging
    def on_keycall_XPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 0, 1, shift)

    def on_keycall_XNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 0, -1, shift)

    def on_keycall_YPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 1, 1, shift)

    def on_keycall_YNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 1, -1, shift)

    def on_keycall_ZPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 2, 1, shift)

    def on_keycall_ZNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 2, -1, shift)

    def on_keycall_APOS(self,event,state,shift,cntrl):
        pass
        #self.kb_jog(state, 3, 1, shift, False)

    def on_keycall_ANEG(self,event,state,shift,cntrl):
        pass
        #self.kb_jog(state, 3, -1, shift, linear=False)

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
