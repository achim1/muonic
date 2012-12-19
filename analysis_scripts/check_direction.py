#! /usr/bin/env python

"""
Calculating the fraction of upgoing events
CAUTION: Assuming chan0 is the uppermost and
         chan1 is below chan0
"""

import numpy as n
import pylab as p
import sys

f = open(sys.argv[1])

directions = []

for line in f.readlines():


    try:
        line = line.split()
        directions.append(float(line[3][2:-1]) - float(line[1][2:-1]))
    except:
        pass

up = 0
down = 0

for item in directions:
    if item > 0:
        down += 1
    else:
        up += 1

print "Upgoing events:", up
print "Downgoing events:", down
print "Fraction of upgoing events:", float(up)/(up+down)

