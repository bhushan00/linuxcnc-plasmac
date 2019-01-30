#! /usr/bin/python

import sys

infile = sys.argv[1]
f = open(infile, 'r')
for line in f:
    if line.startswith(';'):
        print line.rstrip()
    elif line.startswith('('):
        print line.rstrip()
    elif not 'z' in line.lower():
        print line.rstrip()
    else:
        if not 'x' in line.lower()\
        and not 'y' in line.lower()\
        and not 'a' in line.lower()\
        and not 'b' in line.lower()\
        and not 'c' in line.lower()\
        and not 'u' in line.lower()\
        and not 'v' in line.lower()\
        and not 'w' in line.lower():
            print '(%s)' % (line.rstrip())
            pass
        else:
            newline = ''
            newz = ''
            removing = 0
            for bit in line:
                if removing:
                    if bit in '0123456789.- ':
                        newz += bit
                    else:
                        removing = 0
                        if newz:
                            newz += ')'
                        newline += bit
                elif bit.lower() == 'z':
                    removing = 1
                    newz += '(Z'
                else:
                    newline += bit
            print '%s %s'% (newline.rstrip(), newz)
