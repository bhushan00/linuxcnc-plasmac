#! /usr/bin/python

'''
plasmac_gcode.py

Copyright (C) 2019  Phillip A Carter

Inspired by and some parts copied from the work of John
(islander261 on the LinuxCNC forum) 

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
import sys
import linuxcnc

ini = linuxcnc.ini(os.environ['INI_FILE_NAME'])
infile = sys.argv[1]
materialFile = ini.find('EMC', 'MACHINE').lower() + '_material.cfg'
materialsExist = True

with open(materialFile, 'r') as f_in:
    materialList = [0]
    for line in f_in:
        if not line.startswith('#'):
            if line.startswith('[MATERIAL_NUMBER_') and line.strip().endswith(']'):
                a,b,c = line.split('_')
                t_number = int(c.replace(']',''))
                materialList.append(t_number)
f = open(infile, 'r')

for line in f:
    if 'm190' in line.lower():
        first, last = line.lower().strip().split('p',1)
        material = ''
        for mNumber in last.strip():
            if mNumber in '0123456789':
                material += mNumber
            else:
             break
        if int(material) not in materialList:
            if materialsExist:
                print ';The following materials are missing from:'
                print ';%s' % (materialFile)
            materialsExist = False
            print ';Material #%s' % (material)

if materialsExist:
    f = open(infile, 'r')
    for line in f:
        if line.strip().startswith(';'):
            print line.rstrip()
        elif line.strip().startswith('('):
            print line.rstrip()
        elif not 'z' in line.lower():
            print line.rstrip()
        elif 1 not in [c in line.lower() for c in 'xyabcuvw']:
            print '(%s)' % (line.rstrip())
        else:
            newline = ''
            newz = ''
            removing = 0
            comment = 0
            for bit in line:
                if comment:
                    if bit == ')':
                        comment = 0
                    newline += bit
                elif removing:
                    if bit in '0123456789.- ':
                        newz += bit
                    else:
                        removing = 0
                        if newz:
                            newz = newz.rstrip() + ')'
                        newline += bit
                elif bit == '(':
                    comment = 1
                    newline += bit
                elif bit.lower() == 'z':
                    removing = 1
                    newz += '(' + bit
                else:
                    newline += bit
            print '%s %s'% (newline.rstrip(), newz)
else:
    print 'M2'
