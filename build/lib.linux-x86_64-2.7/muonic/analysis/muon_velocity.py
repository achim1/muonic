#!/usr/bin/env python

import sys
import gzip

#IMPORTANT
# The order of the szintillators is 0->2->1
######

#files = sys.argv[1]
files = ("../../../CosmicCode/2012-7-13_7-27-29_RAW_HOURS_Current")
BIT0_4 = 31
BIT5 = 1 << 5
BIT7 = 1 << 7

# For DAQ status
BIT0 = 1 # 1 PPS interrupt pending
BIT1 = 1 << 1 # Trigger interrupt pending
BIT2 = 1 << 2 # GPS data possible corrupted
BIT3 = 1 << 3 # Current or last 1PPS rate not within range

def time_to_seconds(time, correction):
    '''
    Convert hhmmss,xxx string int seconds since day start
    '''
    #print time,correction
    tfields = time.split(".")
    t = tfields[0]
    secs_since_day_start = int(t[0:2])*3600+int(t[2:4])*60+int(t[4:6])
    evt_time = secs_since_day_start + int(tfields[1])/1000.0+int(correction)/1000.0
    return round(evt_time)
    counter  = 0.0 
    

for filename in files:
    
    counter  = 0.0 
    muon = {0:False,1:False,2:False,"Time":0.}
    freq = 25e6 # 25 MHz
    last_onepps = 0
    muon_start = 0.
    nmuons = 0
    last_seconds = 0.
    last_time = 0.
    last_triggercount = 0
    switched_onepps = False
    last_onepps = 0
    onepps_count = 0
    re_previous = 0.0
    
    counter_previous = 0.0
    trigger_count_previous = 0.0
    onepps_count_previous = 0.0
    line_current = ""
    if filename.endswith('.gz'):
        f = gzip.open(filename)
    else:
        f = open(sys.argv[1])
       
for line in f:
   
    counter = counter + 1
    if counter == 1000:
        break
    fields = line.rstrip("\n").split(" ")
        # Ignore malformed lines
    if len(fields) != 16:
        continue
        #Ignore everything that is not trigger data
    if len(fields[0]) != 8:
        continue
  
    try:
        int(fields[len(fields)-1])
    except ValueError:
        continue
       
    ch0 = float(sys.argv[2])
    ch1 = float(sys.argv[3])
    ch2 = float(sys.argv[4])
    ch3 = float(sys.argv[5])
        
    trigger_count = int(fields[0],16)
    onepps_count = int(fields[9],16)
   
    re_a = 0
    re_b = 0
 
    if ch0==1 and ch1==2 and ch2==0 and ch3==0:
        re_a  = int(fields[1],16)*1.25
        re_b  = int(fields[3],16)*1.25
        
    if ch0==1 and ch1==0 and ch2==2 and ch3==0:
        re_a  = int(fields[1],16)*1.25
        re_b  = int(fields[5],16)*1.25

    if ch0==1 and ch1==0 and ch2==0 and ch3==2:
        re_a  = int(fields[1],16)*1.25
        re_b  = int(fields[7],16)*1.25

    if ch0==0 and ch1==1 and ch2==2 and ch3==0:
        re_a  = int(fields[3],16)*1.25
        re_b  = int(fields[5],16)*1.25

    if ch0==0 and ch1==1 and ch2==0 and ch3==2:
        re_a  = int(fields[3],16)*1.25
        re_b  = int(fields[7],16)*1.25

    if ch0==0 and ch1==0 and ch2==1 and ch3==2:
        re_a  = int(fields[5],16)*1.25
        re_b  = int(fields[7],16)*1.25

    #Vice versa! Important for offset measurements 

    if ch0==2 and ch1==1 and ch2==0 and ch3==0:
        re_b  = int(fields[1],16)*1.25
        re_a  = int(fields[3],16)*1.25
        
    if ch0==2 and ch1==0 and ch2==1 and ch3==0:
        re_b  = int(fields[1],16)*1.25
        re_a  = int(fields[5],16)*1.25

    if ch0==2 and ch1==0 and ch2==0 and ch3==1:
        re_b  = int(fields[1],16)*1.25
        re_a  = int(fields[7],16)*1.25

    if ch0==0 and ch1==2 and ch2==1 and ch3==0:
        re_b  = int(fields[3],16)*1.25
        re_a  = int(fields[5],16)*1.25

    if ch0==0 and ch1==2 and ch2==0 and ch3==1:
        re_b  = int(fields[3],16)*1.25
        re_a  = int(fields[7],16)*1.25

    if ch0==0 and ch1==0 and ch2==2 and ch3==1:
        re_b  = int(fields[5],16)*1.25
        re_a  = int(fields[7],16)*1.25

    time = fields[10]
    correction = (fields[15])
        
    if re_b > 0.0 and re_a==0 and re_previous>0 and line_current != line:
        upper = float(time_to_seconds(time_previous,correction_previous)+(trigger_count_previous-onepps_count_previous)+re_previous)
        lower = float(time_to_seconds(time,correction)+(trigger_count-onepps_count)+re_b)
        distance = float(sys.argv[6])
        if (lower-upper) < 0.0:
            velocity = distance/(abs(lower-upper)*pow(10,-2))
            if velocity > 0.0:
                print "velocity muon %10.8f meterperseconds"%(velocity,)
        
    if re_a > 0.0 and re_b==0:
        re_previous = re_a
        time_previous = time
        correction_previous = correction
        trigger_count_previous = trigger_count
        onepps_count_previous = onepps_count
        
    if last_onepps != onepps_count:
        if onepps_count > last_onepps:
            freq  = float(onepps_count - last_onepps)
        else:
            freq = float(0xFFFFFFFF + onepps_count - last_onepps)
                #print "Freq:",freq
            prevlast_onepps = last_onepps
            last_onepps = onepps_count
            switched_onepps = True
                # vim: ai ts=4 sts=4 et sw=4
                
    
