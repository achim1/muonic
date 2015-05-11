#  script to convert daq raw files to muonic pulsefiles
#
# output format (relative time,[(re0_channel0,fe0_channel0),(re1_channel0,fe1_channel0),...],[(..],[..],[..])
# -> each channel is represented by a list of leading/falling edge tuples of the recorded pulses
#
#

import sys
import re

from muonic.analysis.PulseAnalyzer import PulseExtractor

pe = PulseExtractor()

f = open(sys.argv[1])

converted_file = open("converted.txt","w")

goodpattern = re.compile("^[a-zA-Z0-9+-.,:()=$/#?!%_@*|~' ]*[\n\r]*$") # match against this to supress daq garbage

for line in f.readlines():
    if goodpattern.match(line) is None:
        continue

    try:
        pulses = pe.extract(line)
    except Exception as e:
        print line,"Failed to convert",e
        continue
    
    if pulses is not None:
        converted_file.write(pulses.__repr__() + "\n")
    



