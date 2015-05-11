#!/usr/bin/env python

import sys
import gzip

#IMPORTANT
# The order of the szintillators is 0->2->1
######

files = sys.argv[1:]

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
#    print time,correction
    tfields = time.split(".")
    t = tfields[0]
    secs_since_day_start = int(t[0:2])*3600+int(t[2:4])*60+int(t[4:6])
    evt_time = secs_since_day_start + int(tfields[1])/1000.0+int(correction)/1000.0
    return round(evt_time)

for filename in files:

    muon = {0:False,1:False,2:False,"Time":0.}
    freq = 25e6 # 25 MHz
    last_onepps = 0
    last_muon = 0
    wait_fe0 = False
    time_ch0 = 0.
    wait_fe1 = False
    time_ch1 = 0.
    wait_fe2 = False
    time_ch2 = 0.

    #buffer_ch0 = []
    #buffer_ch1 = []
    #buffer_ch2 = []

    muon_start = 0.

    nmuons = 0
    last_pulse = 0.
    decay_start_time_ch2 = 0.
    decay_waiting_ch2 = False
    decay_start_time_ch1 = 0.
    decay_waiting_ch1 = False
    last_seconds = 0.
    last_time = 0.
    last_triggercount = 0
    switched_onepps = False
    last_onepps = 0
    onepps_count = 0

    if filename.endswith('.gz'):
        f = gzip.open(filename)
    else:
        f = open(filename)
    for line in f:
        print line
        fields = line.rstrip("\n").split(" ")
        # Ignore malformed lines
        if len(fields) != 16:
            continue
        #Ignore everything that is not trigger data
        if len(fields[0]) != 8:
            continue
        # Check if GPS data is valid
        #if fields[12] != "A":
        #    print "GPS data not valid"
        #    continue
        #Another check, sometimes lines are mixed,
        #try if we can convert the last field to an int
        try:
            int(fields[len(fields)-1])
        except ValueError:
            continue
        #Check if error bits are set
        #if fields[14] != "0":
        #    print "Error:",fields
        #    continue
        trigger_count = int(fields[0],16)
        onepps_count = int(fields[9],16)

#    re_0 = (fields[1] != "00") and not fields[1] == "80"
        re_0 = (fields[1] != "00")
        fe_0 = (fields[2] != "00")
        re_1 = (fields[3] != "00")
        fe_1 = (fields[4] != "00")
        re_2 = (fields[5] != "00")
        fe_2 = (fields[6] != "00")
        if last_onepps != onepps_count:
            if onepps_count > last_onepps:
                freq  = float(onepps_count - last_onepps)
            else:
                freq = float(0xFFFFFFFF + onepps_count - last_onepps)
#        print "Freq:",freq
            prevlast_onepps = last_onepps
            last_onepps = onepps_count
            switched_onepps = True
        time = fields[10]
        correction = fields[15]
        seconds = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq
        if time == last_time and switched_onepps:
            print "Correcting delayed onepps switch:",seconds,line
            seconds = time_to_seconds(time,correction)+(trigger_count - prevlast_onepps)/freq
        else:
            last_time = time
            switched_onepps = False
        
        if trigger_count < last_triggercount and not switched_onepps:
            print "Correcting trigger count rollover:",seconds,line
            seconds += int(0xFFFFFFFF)/freq
        else:
            last_triggercount = trigger_count
        
        if last_seconds > seconds:
            print "Wrong event order",seconds,line
            continue

        last_seconds = seconds
        print "seconds",seconds

        pulse_ch0 = False
        pulse_ch1 = False
        pulse_ch2 = False
        
        if re_0:
            wait_fe0 = True
            time_ch0 = seconds
        if time_ch0 - seconds > 50e-9:
            wait_f0 = False
        if fe_0 and wait_fe0:
            print "Pulse ch0",seconds,line
            pulse_ch0 = True
            wait_fe0 = False
        if re_1:
            wait_fe1 = True
            time_ch1 = seconds
        if time_ch1 - seconds > 50e-9:
            wait_f1 = False
        if fe_1 and wait_fe1:
            print "Pulse ch1",seconds,line
            pulse_ch1 = True
            wait_fe1 = False
        if re_2:
            wait_fe2 = True
            time_ch2 = seconds
        if time_ch2 - seconds > 50e-9:
            wait_f2 = False
        if fe_2 and wait_fe2:
            print "Pulse ch2",seconds,line
            pulse_ch2 = True
            wait_fe2 = False
            
        # ch1 is the downmost channel!!!!!!!!!
        if decay_waiting_ch1 and seconds - decay_start_time_ch1 > 20e-6:
            print "No decay",seconds,decay_start_time_ch1
            decay_waiting_ch1 = False
        if decay_waiting_ch1:
            if pulse_ch0 or pulse_ch2:
                decay_waiting_ch1 = False
                muon[0] = False
                muon[1] = False
                muon[2] = False
                print "Deleting decay"
            elif pulse_ch1:
                print "Decay ch1 %10.8f microseconds"%(1e6*(seconds - decay_start_time_ch1),)
                muon[0] = False
                muon[1] = False
                muon[2] = False
                decay_waiting_ch1 = False
                continue

        if decay_waiting_ch2 and seconds - decay_start_time_ch2 > 20e-6:
            print "No decay ch2",seconds,decay_start_time_ch2
            decay_waiting_ch2 = False
        if decay_waiting_ch2:
            if pulse_ch0:
                decay_waiting_ch2 = False
                muon[0] = False
                muon[1] = False
                muon[2] = False
                print "Deleting decay"
            elif pulse_ch2 and not pulse_ch1:
                print "Decay ch2 upper %10.8f microseconds"%(1e6*(seconds - decay_start_time_ch2),)
                muon[0] = False
                muon[1] = False
                muon[2] = False
                decay_waiting_ch2 = False
                continue
            elif pulse_ch1:
                if seconds - muon['Time'] > 100e-9:
                    print "Decay ch2 lower %10.8f microseconds"%(1e6*(seconds - decay_start_time_ch2),)
                    muon[0] = False
                    muon[1] = False
                    muon[2] = False
                    decay_waiting_ch2 = False
                    continue

        if pulse_ch0 or pulse_ch1 or pulse_ch2:
            if seconds - muon['Time'] < 200e-9:
                muon[0] = muon[0] or pulse_ch0
                muon[1] = muon[1] or pulse_ch1
                muon[2] = muon[2] or pulse_ch2
            else:
                muon['Time'] = seconds
                muon[0] = pulse_ch0
                muon[1] = pulse_ch1
                muon[2] = pulse_ch2

            if muon[0] and muon[1] and muon[2]:
                print "MUON through",seconds
                nmuons += 1
                decay_waiting_ch1 = True
                print "DeltaT:",seconds - decay_start_time_ch1
                decay_start_time_ch1 = seconds
                print "Decay waiting ch1",seconds
                muon[0] = False
                muon[1] = False
                muon[2] = False
                if decay_start_time_ch2:
                    print "Deleting decay ch2 because of throughgoing muon"
                    decay_start_time_ch2 = False
            
            if muon[0] and muon[2] and not muon[1]:
                print "MUON stuck"
                decay_waiting_ch2 = True
                decay_start_time_ch2 = seconds
                print "Decay waiting ch2",seconds

    print "NMUONS:",file,nmuons
        
print nmuons

# vim: ai ts=4 sts=4 et sw=4
