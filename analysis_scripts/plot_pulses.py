#! /usr/bin/env python

"""
Script for histograming the pulseswidth
Usage python plot_pulses.py PULSEFILE
"""

import numpy as n
import pylab as p
import sys

f = open(sys.argv[1])

chan0 = []
chan1 = []

for line in f.readlines():

    
    try:
        line = line.split()
        fe0 = line[2].split(')')[0]
        fe1 = line[4].split(')')[0]
        re0 = line[1].split('(')[1][:-1]
        re1 = line[3].split('(')[1][:-1]
        chan0.append(float(fe0) - float(re0))
        chan1.append(float(fe1) - float(re1))
    except:
        pass

print chan0, 'Pulsewidths chan0'
print chan1, 'Pulsewidths chan1'

xmax = max([max(chan0),max(chan1)])
pulsebins = n.linspace(0,xmax,xmax+1)
hist0 = n.histogram(n.array(chan0),bins=pulsebins)
hist1 = n.histogram(n.array(chan1),bins=pulsebins)

#print xmax
#print pulsebins

baredges0 = n.linspace(0,hist0[1][-1],len(hist0[0]))
baredges1 = n.linspace(0,hist1[1][-1],len(hist1[0]))
p.ylim(ymax=1.2*max([max(hist0[0]),max(hist1[0])])) 
p.bar(baredges0,hist0[0],width=pulsebins[1]-pulsebins[0],color='b',label='chan0')
p.bar(baredges1,hist1[0],width=pulsebins[1]-pulsebins[0],color='r',alpha=0.5,label='chan1')
p.grid()
p.legend()
p.xlabel('Pulsewidth in ns')
p.ylabel('Events')
p.show()

