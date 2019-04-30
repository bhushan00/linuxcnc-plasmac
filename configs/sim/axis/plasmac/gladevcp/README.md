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

Usage of the **plasmac.cut-feed-rate** input pin requires remapping of the F word, if not using this set the **plasmac.cut-feed-rate** input pin to 0 which will then use the feed rate from the gcode file.

Cut height can be adjusted on the fly by adding an offset to the **plasmac.height-override** input pin.
This offset is added to the THC voltage target to lower or raise the torch.

Target voltage can be selected from:
- a voltage automatically read from the initial cut height.
- the **plasmac.cut-volts** input pin.

IHS may be disabled with one of two different types:
- Type 0 - If the start of the next cut is less than **plasmac.skip-ihs-distance** from the end of the last cut and THC is enabled.
- Type 1 - If the start of the next cut is less than **plasmac.skip-ihs-distance** from the start of the last cut.
This feature is disabled after any error. For example if there is an arc failure while cutting then IHS will be performed regardless of where the cut is.

Paused Motion allows reversing and forwarding along the current segment while paused.  
Reverse paused motion can only go back as far as the start of the cut the control point is currently on.  
Forward paused motion can continue on through any number of cuts to the end of the gcode program.  

A dry run is available by running the gcode with the torch disabled.

Ohmic Test enables the ohmic probe to test for a shorted torch.
  
***
#### EXAMPLE CONFIGURATIONS  
- metric_plasmac.ini  
- imperial_plasmac.ini  

These example configuration files show examples of how to connect the Gmoccapy GUI with the plasmac HAL component for use in plasma cutting machines.  
The manual page for the plasmac component is accessed by the command 'man.plasmac'  


Filename|Function
---:|---
plasmac_ini|configuration file.
plasmac.hal|hal connections for the plasmac component.
plasmac_???.glade|sample gladevcp panels connecting to the plasmac component.
plasmac_???.hal|hal connections for the panels.
plasmac_???.py|python code for the panels.
machine_name.cfg|configuration settings.
machine_name.mat|material file for cut parameters.
plasmac_feed.ngc|for remapping of the gcode feed rate.
plasmac_gcode.py|removes z axis moves from the opened gcode file.

The .ini files are notated for extra the requirements for these configurations.  
The minimum .ini file requirements for the plasmac component are:  
- [PLASMAC]MODE (only if mode 1 or mode 2)  
- [AXIS_L]MAX_VELOCITY  
- [AXIS_L]MAX_ACCELERATION  
- [AXIS_L]OFFSET_AV_RATIO
  
All other .ini file settings are for the example configurations.  

The .cfg  and .mat files are plain text and may be edited with any text editor.  
Lines beginning with # are ignored in both these files.  

The python directory is for remapping of the F word.  

***  
#### TEST PANEL  

In the test directory there is a simple test panel and associated python file which can be used to test the example configuration as referenced in the ini file.  

***  
#### NGC EXAMPLES  

Example ngc files are in nc_files/plasmac.  

***  
