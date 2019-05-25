#### PLASMAC

A plasma control component for linuxcnc using the linuxcnc master branch merged with the feature/reverse-run-master2 branch.  

Not dependent on any particular hardware and should work with any hardware that provides the correct I/O.  

No Z axis commands are required in gcode as all required height movements are controlled by this component.  

Should scale correctly for both metric and inch configuraions.  

Three different operating modes:  
- 0 - Use the **plasmac.arc-voltage-in** input pin for both arc-OK and THC.  
- 1 - Use the **plasmac.arc-ok-in** input pin for arc-OK, use the **plasmac.arc-voltage-in** input pin for THC.  
- 2 - Use the **plasmac.arc-ok-in** input pin for arc-OK, use the **plasmac.move-up** and the **plasmac.move-down** input pins for THC, kerf crossing lockout is disabled.  

A spindle on signal (connected to the **plasmac.spindle-on** input pin) begins the sequence of:  
- set feedhold.  
- find top of stock.  
- move up to pierce height.  
- start torch, retry if unsuccessful until too many attempts.  
- wait for pierce delay.  
- move to puddle jump height (if enabled).  
- release feedhold, X/Y motion begins.  
- wait for puddle jump delay (if enabled).  
- move down to cutting height.  
- use THC (if enabled) to adjust torch height using rules for corner lock (if enabled) and kerf crossing (if enabled).  
- when spindle on is removed, turn torch off after delay.  
- move to safe height.  
- return to idle state and wait for next cut.  

Turn torch off, pause program and move to safe height then wait for 'resume' or 'stop' if the following occur:  
- arc is lost.  
- **plasmac.ohmic-probe** input pin is activated.  
- **plasmac.float-switch** input pin is activated.  
- **plasmac.breakaway** input pin is activated.  
- program is paused.  

Turn torch off, move to safe height and stop program if the following occur:  
- program is stopped.  
- minimum height is reached during THC.  
- maximum height is reached during THC.  

Safe height may be reduced if torch height (during THC moves) plus safe height would exceed the maximum height.  
The minimum allowed reduced safe height is Pierce Height plus 1mm (0.04").  
If safe height is reduced an error message is sent.  

Usage of the **plasmac.cut-feed-rate** input pin requires that a gcode file contain the feedrate command:  
**F#<_hal[plasmac.cut-feed-rate]>**  
This reads the feed rate from the cut parameters on the Run tab and sets the value the component needs for THC calculations.  
If you don't want to do it this way then use a standard **Fnnn** to set the feed rate but you will need to set the Cut Feed Rate in the run to zero and plasmac will use **motion.requested−vel** for calculations.  
If you use **Fnnn** and leave Cut Feed Rate then plasmac uses Cut Feed Rate for THC so if **Fnnn** is less than Cut Feed Rate then THC will be in corner locked mode.  

Cut height can be adjusted on the fly by adding an offset to the **plasmac.height-override** input pin.  
This offset either positive or negative is added to the THC voltage target to lower or raise the torch.  

Target voltage can be selected from:  
- a voltage automatically read from the initial cut height.  
- the **plasmac.cut-volts** input pin.  

IHS may be skipped in one of two different ways:  
If THC is disabled then skip IHS if start of cut less than **plasmac.skip-ihs-distance** from last succesful probe.  
If THC is enabled then skip IHS if start of cut less than **plasmac.skip-ihs-distance** from end of last cut.  
This feature is disabled after any error. For example if there is an arc failure while cutting then IHS will be performed regardless of where the cut is.

Paused Motion allows reversing and forwarding along the current segment while paused.  
Reverse paused motion can only go back as far as the start of the cut the control point is currently on.  
Forward paused motion can continue on through any number of cuts to the end of the gcode program.  

A dry run is available by running the gcode with the torch disabled.  

Ohmic Test enables the ohmic probe to test for a shorted torch.  

***
#### MATERIAL HANDLING
Material handling has nothing at all to do with the LinuxCNC tool table. In fact **M6 Tn** commands should not be used with these configs.  
There is a material file with its name is derived from **[EMC]MACHINE** in the in file, so a machine named METRIC_PLASMAC would have a material file named metric_plasmac_material.cfg
  
It is not a requirement that you use a material file, if required you can change the cut parameters manually in the Run tab. It is also not a requirement to use the automatic material changes, just omit them from the gcode file.

For manual material handling all you need in the gcode is:  
**F#<_hal[plasmac.cut-feed-rate]>**  
**M3 S1**  
.  
.  
**M5**  

For automatic material handling in your gcode you need:  
NOTE: the M66 MUST be after the M190 and the F MUST be after the M66  
**M190 Pn**  
**M66 P3 L3 Q1**  
**F#<_hal[plasmac.cut-feed-rate]>**  
**M3 S1**  
.  
.  
**M5**  
M190 Pn changes the material to number n  
M66 P3 L3 Q1 waits for change to be confirmed  

NOTE: If you use Fnn rather than F#<_hal[plasmac.cut-feed-rate]> then if the value of nn is less than 99.9% of the cut-feed-rate parameter in the Run tab then THC will be locked out.  

Material numbers do not need to be consecutive nor do they need to be in numerical order.  
The maximum allowed material number is 99999 for no particular reason.  

When a material is changed it only changes the cut parameters in the Run tab, LinuxCNC knows nothing of the material nor does plasmac know anything about LinuxCNC tool. (i.e. it does NOT do a tool change)  

To use cutter compensation you will need to use G41.1, G42.1 and G40 with the cut file parameter hal pin **#<_hal[plasmac_run.kerf-width-f]>** like so:  
- **G41.1 D#<_hal[plasmac_run.kerf-width-f>** ; for left of programmed path  
- **G42.1 D#<_hal[plasmac_run.kerf-width-f>** for right of programmed path  
- **G40** to turn compensation off  

Materials can be selected manually with the either the Cut Parameters combobox or via MDI with M190 Pn.  

There is a python program named materialverter.py in the Gmoccapy folder to convert SheetCam tooltables to the plasmac format.  
If there are requests for other conversion types I would be happy to have a crack at them.

***
#### EXAMPLE CONFIGURATIONS  
- metric_plasmac.ini  
- imperial_plasmac.ini  

These example configuration files show examples of how to connect the Gmoccapy GUI with the plasmac HAL component for use in plasma cutting machines.  
The manual page for the plasmac component is accessed by the command 'man.plasmac'  

Files in the example configurations are:
Filename|Function (units = metric or imperial)
---:|---
units_plasmac_ini|configuration file.
plasmac.hal|hal connections for the plasmac component.
plasmac_xxx.glade|a gladevcp panel connecting to the plasmac component.
plasmac_xxx.hal|hal connections for the panel.
plasmac_xxx.py|python code for the panel.
units_startup.ngc|startup gcode commands.
plasmac_gcode.py|removes z axis moves from the opened gcode file
plasmac_axis.py|python code to customise the Axis GUI
materialverter.py|tool table file converter
configurator.py|configure a new or upgrade an existing plasmac configuration

The configurator copies the required files from above plus:  
Filename|Function ({MACHINE} = name of machine in ini file)
---:|---
{MACHINE}_connections.hal|connections to your i/o hal pins.

After running a new working configuration the first time the following will be created:  
Filename|Function ({MACHINE} = name of machine in ini file)
---:|---
{MACHINE}_config.cfg|configuration settings for the config tab.
{MACHINE}_run.cfg|configuration settings for the run tab.
{MACHINE}_material.cfg|material file for cut parameters.
plasmac_stats.var|saved statistics.


The .ini files are notated for extra the requirements for these configurations.
The .cfg files are plain text and may be edited with any text editor.  

The minimum .ini file requirements for the plasmac component are:
- [PLASMAC]MODE (only if mode 1 or mode 2)  
- [AXIS_L]MAX_VELOCITY  
- [AXIS_L]MAX_ACCELERATION  
- [AXIS_L]OFFSET_AV_RATIO  

***  
#### TEST PANEL  

There is a ./test directory which has a simple test panel and associated python file which can be used to test the example configuration as referenced in the ini file.  
These can be commented out or deleted from the ini file and the directory can be deleted.

***  
#### NGC EXAMPLES  

Example ngc files are in nc_files/plasmac.  

***
#### NOTES
This component and related sim configs are under active development and are being tested by several users

***  
#### INSTALLING A WORKING CONFIGURATION  

The easiest way to install a complete configuration is:  
- make a working configuration for your base machine, this could be done manually or with pncconf for a machine using Mesa hardware or stepconf for a machine using the parallel port.  
- make a note of the HAL pin connections for machine.  
- make a git clone of this repo.  
- run configurator.py in the configs/by_machine/plasmac directory of the git clone.  
- select New.  
You should end up with a working configuration.  

***  
#### UPGRADING A WORKING CONFIGURATION  
The easiest way to upgrade an existing configuration is:  
- cd to your git clone  
- git pull  
- make  
- run configurator.py in the configs/by_machine/plasmac directory of the git clone.  
- select Upgrade  
You should end up with an upgraded working configuration.  

***
#### LICENSE
plasmac and all its related software is released under GPLv2.  
