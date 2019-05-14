#! /usr/bin/python

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
