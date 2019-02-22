#! /usr/bin/python

import sys

infile = sys.argv[1]
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
