#### EXAMPLE CONFIGURATIONS  
\- metric_plasmac.ini  
\- imperial_plasmac.ini  

These example configuration files show examples of how to connect gmoccapy with the plasmac component for use in plasma cutting machines.  
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
\- [PLASMAC]MODE (only if mode 1 or mode 2)  
\- [AXIS_L]MAX_VELOCITY  
\- [AXIS_L]MAX_ACCELERATION  
\- [AXIS_L]OFFSET_AV_RATIO  
All other .ini file settings are for the example configurations.  

The .cfg  and .mat files are plain text and may be edited with any text editor.  
Lines beginning with # are ignored in both these files.  

The python directory is for remapping of the F word.  

Paused Motion allows reversing and forwarding along the current segment while paused.  
Reverse paused motion can only go back as far as the start of the cut the control point is currently on.  
Forward paused motion can continue on through any number of cuts to the end of the gcode program.  

Dry Run runs the gcode without starting the torch. .

***  
#### TEST PANEL  

In the test directory there is a simple test panel and associated python file which can be used to test the example configuration as referenced in the ini file.  

***  
#### NGC EXAMPLES  

Example ngc files are in nc_files/plasmac.  

***  
