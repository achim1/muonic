#!/usr/bin/env python

import sys
import gzip

#####################################################
#This is coincident level 0!!
#Order of scintillators is irrelevent!
#####################################################

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
#   print time,correction
    tfields = time.split(".")
    t = tfields[0]
    secs_since_day_start = int(t[0:2])*3600+int(t[2:4])*60+int(t[4:6])
    evt_time = secs_since_day_start + int(tfields[1])/1000.0+int(correction)/1000.0
    return round(evt_time)
    #filename = sys.argv[1]
    f = open(sys.argv[1])
    

for filename in files:
    ch0 = float(sys.argv[2]) #0 or 1
    ch1 = float(sys.argv[3]) #0 or 1
    ch2 = float(sys.argv[4]) #0 or 1
    ch3 = float(sys.argv[5]) #0 or 1
    dpch0 = float(sys.argv[6]) #0 or 1
    dpch1 = float(sys.argv[7]) #0 or 1
    dpch2 = float(sys.argv[8]) #0 or 1
    dpch3 = float(sys.argv[9]) #0 or 1
    
    
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
    wait_fe3 = False
    time_ch3 = 0.

    muon_start = 0.

    nmuons = 0
    last_pulse = 0.
    decay_start_time_ch0 = 0.
    decay_waiting_ch0 = False
    decay_start_time_ch1 = 0.
    decay_waiting_ch1 = False
    decay_start_time_ch2 = 0.
    decay_waiting_ch2 = False
    decay_start_time_ch3 = 0.
    decay_waiting_ch3 = False
    
    
    last_seconds = 0.
    last_time = 0.
    last_triggercount = 0
    switched_onepps = False
    last_onepps = 0
    onepps_count = 0
    counter = 0.0
   

    if filename.endswith('.gz'):
        f = gzip.open(filename)
    else:
        f = open(sys.argv[1])
    for line in f:
        
        fields = line.rstrip("\n").split(" ")
        #print "fields: ",fields
        #print "line: ",line
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
 
        trigger_count = int(fields[0],16)
        onepps_count = int(fields[9],16)
    
        re_0 = (fields[1] >= "00")
        re_1 = (fields[3] >= "00")
        re_2 = (fields[5] >= "00")
        re_3 = (fields[7] >= "00")
        fe_0 = (fields[2] >= "00")
        fe_1 = (fields[4] >= "00")
        fe_2 = (fields[6] >= "00")
        fe_3 = (fields[8] >= "00")

        #check the single pulse for channel

        if (ch0==1 and fields[1] == "00"):
            continue
        if (ch1==1 and fields[3] == "00"):
            continue
        if (ch2==1 and fields[5] == "00"):
            continue
        if (ch3==1 and fields[7] == "00"):
            continue
        if (ch0==1 and ch1==1 and (fields[1] == "00" or fields[3] == "00")):
            continue
        if (ch0==1 and ch2==1 and (fields[1] == "00" or fields[5] == "00")):
            continue
        if (ch0==1 and ch3==1 and (fields[1] == "00" or fields[7] == "00")):
            continue
        if (ch1==1 and ch2==1 and (fields[3] == "00" or fields[5] == "00")):
            continue
        if (ch1==1 and ch3==1 and (fields[3] == "00" or fields[7] == "00")):
            continue
        if (ch2==1 and ch3==1 and (fields[5] == "00" or fields[7] == "00")):
            continue
        if (ch0==1 and ch1==1 and ch2==1 and (fields[1] == "00" and fields[3] == "00" or fields[5] == "00")):
            continue
        if (ch1==1 and ch2==1 and ch3==1 and (fields[3] == "00" and fields[5] == "00" or fields[7] == "00")):
            continue
        
        #check for double pulse

        if fields[1] >= "80":
            for line in f:
                fields_next = line.rstrip("\n").split(" ")
                #define the different options
                
                if 0==0: 
                #current analysis for one event. Note, that one event can be described by more than one line!
                    if last_onepps != onepps_count:
                        if onepps_count > last_onepps:
                            freq  = float(onepps_count - last_onepps)
                        else:
                            freq = float(0xFFFFFFFF + onepps_count - last_onepps)
           
                        prevlast_onepps = last_onepps
                        last_onepps = onepps_count
                        switched_onepps = True

                    time = fields[10]
                    correction = fields[15]
                    seconds0 = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq
                    seconds1 = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq
                    seconds2 = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq
                    seconds3 = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq
                             
                    if time == last_time and switched_onepps:
                        print "Correcting delayed onepps switch:",seconds0,line
                        seconds0 = time_to_seconds(time,correction)+(trigger_count - prevlast_onepps)/freq
                        seconds1 = time_to_seconds(time,correction)+(trigger_count - prevlast_onepps)/freq
                        seconds2 = time_to_seconds(time,correction)+(trigger_count - prevlast_onepps)/freq
                        seconds3 = time_to_seconds(time,correction)+(trigger_count - prevlast_onepps)/freq
                    else:
                        last_time = time
                        switched_onepps = False
        
                    if trigger_count < last_triggercount and not switched_onepps:
                        print "Correcting trigger count rollover:",seconds0,line
                        seconds0 += int(0xFFFFFFFF)/freq
                        seconds1 += int(0xFFFFFFFF)/freq
                        seconds2 += int(0xFFFFFFFF)/freq
                        seconds3 += int(0xFFFFFFFF)/freq

                    else:
                        last_triggercount = trigger_count
        
                    #if last_seconds > seconds0:
                     #   print "Wrong event order",seconds0,line
                      #  continue
		
                    last_seconds = seconds0
                    print "seconds0:",seconds0
                    print "decay_start_time_ch0: ",decay_start_time_ch0
                    print "decay_start_time_ch1: ",decay_start_time_ch1
                    print "decay_start_time_ch2: ",decay_start_time_ch2
                    print "decay_start_time_ch3: ",decay_start_time_ch3
                    print "difference: ",seconds0-decay_start_time_ch0
                    
                    pulse_ch0 = False
                    pulse_ch1 = False
                    pulse_ch2 = False
                    pulse_ch3 = False

                    #single channel++++++++++++++++++++++++++++

                    if dpch0==1 and (seconds0 !=decay_start_time_ch1 ) and (seconds0 != decay_start_time_ch2) and (seconds0 != decay_start_time_ch3) :
                        print "dpch0"
                        print "Decay ch0 %10.8f microseconds"%(1e6*(seconds0 - decay_start_time_ch0),)
                        if decay_waiting_ch0:
                            if re_0:
                                wait_fe0 = True
                                time_ch0 = seconds0
                            if time_ch0 - seconds0 > 50e-9:
                                wait_f0 = False
                                decay_waiting_ch0 = False
                            if fe_0 and wait_fe0:
                                print "Pulse ch0",seconds0,line
                                pulse_ch0 = True
                                wait_fe0 = False
                            if decay_waiting_ch0 and seconds0 - decay_start_time_ch0 > 20:
                                print "No decay",seconds0,decay_start_time_ch0, seconds0 - decay_start_time_ch0
                                decay_waiting_ch0 = False
                            else:
                                decay_waiting_ch0 = False   
                                print "Decay ch0 %10.8f ch0microseconds"%((seconds0 - decay_start_time_ch0),)
                        else:
                            decay_waiting_ch0 = False
                    else: 
                        print "no decay in channel 0"
                        
                    if dpch1==1 and (seconds1 != decay_start_time_ch0) and (seconds1 != decay_start_time_ch2) and (seconds1 != decay_start_time_ch3) :
                        
                        if  decay_waiting_ch1:
                            if re_1:
                                wait_fe1 = True
                                time_ch1 = seconds1
                            if time_ch1 - seconds1 > 50e-9:
                                wait_f1 = False
                            if fe_1 and wait_fe1:
                                print "Pulse ch1",seconds1,line
                                pulse_ch1 = True
                                wait_fe1 = False
                            if decay_waiting_ch1 and seconds1 - decay_start_time_ch1 > 20:
                                print "No decay",seconds1,decay_start_time_ch1,seconds1 - decay_start_time_ch1
                                decay_waiting_ch1 = False
                            else:
                                decay_waiting_ch1 = False           
                                print "Decay ch1 %10.8f ch1microseconds"%((seconds1 - decay_start_time_ch1),)
                                
                        else:
                            decay_waiting_ch1 = False    
                            
                    else: 
                        print "no decay in channel 1"
                
                    if dpch2==1 and (seconds2 != decay_start_time_ch0) and (seconds2 != decay_start_time_ch1) and (seconds2 != decay_start_time_ch3):
                        if  decay_waiting_ch2:
                            if re_2:
                                wait_fe2 = True
                                time_ch2 = seconds2
                            if time_ch2 - seconds2 > 50e-9:
                                wait_f2 = False
                                decay_waiting_ch2 = False
                            if fe_2 and wait_fe2:
                                print "Pulse ch2",seconds2,line
                                pulse_ch2 = True
                                wait_fe2 = False
                            if decay_waiting_ch2 and seconds2 - decay_start_time_ch2 > 20:
                                print "No decay",seconds2,decay_start_time_ch2, seconds2 - decay_start_time_ch2
                                decay_waiting_ch2 = False
                            else:
                                decay_waiting_ch2 = False           
                                print "Decay ch2 %10.8f ch2microseconds"%((seconds2 - decay_start_time_ch2),)
                    
                        else:
                            decay_waiting_ch2 = False
        
                    else: 
                        print "no decay in channel 2"

                    if dpch3==1 and (seconds3 != decay_start_time_ch0) and (seconds3 != decay_start_time_ch1) and (seconds3 != decay_start_time_ch2) :     
                        if  decay_waiting_ch3:
                            if re_3:
                                wait_fe3 = True
                                seconds3 = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq
                                time_ch3 = seconds3
                            if time_ch3 - seconds3 > 50e-9:
                                wait_f3 = False
                            if fe_3 and wait_fe3:
                                print "Pulse ch3",seconds3,line
                                pulse_ch3 = True
                                wait_fe3 = False
                            if decay_waiting_ch3 and seconds3 - decay_start_time_ch3 > 20:
                                print "No decay",seconds3,decay_start_time_ch3,seconds3 - decay_start_time_ch3
                                decay_waiting_ch3 = False
                            else:
                                decay_waiting_ch3 = False            
                                print "Decay ch3 %10.8f ch3microseconds"%((seconds3 - decay_start_time_ch3),)
                        else:
                            decay_waiting_ch3 = False
                    else: 
                        print "no decay in channel 3"
                
                    if re_0 and dpch0==1:
                        wait_fe0 = True
                        time_ch0 = seconds0
                        if time_ch0 - seconds0 > 50e-9:
                            wait_f0 = False
                        if fe_0 and wait_fe0:
                            print "Pulse ch0",seconds0,line
                            decay_start_time_ch0 = 0
                            decay_start_time_ch0 = seconds0
                            decay_waiting_ch0 = True
                            pulse_ch0 = True
                            wait_fe0 = False
                        else:
                            decay_waiting_ch0 = False
                             
                    if re_1 and dpch1==1:
                        wait_fe1 = True
                        time_ch1 = seconds1
                        if time_ch1 - seconds1 > 50e-9:
                            wait_f1 = False
                        if fe_1 and wait_fe1:
                            #print "Pulse ch1",seconds1,line
                            decay_start_time_ch1 = 0
                            decay_start_time_ch1 = seconds1
                            decay_waiting_ch1 = True
                            pulse_ch1 = True
                            wait_fe1 = False
                        else:
                            decay_waiting_ch1 = False
                
                            
                    if re_2 and dpch2==1:
                        wait_fe2 = True
                        time_ch2 = seconds2
                        if time_ch2 - seconds2 > 50e-9:
                            wait_f2 = False
                        if fe_2 and wait_fe2:
                            print "Pulse ch2",seconds2,line
                            decay_start_time_ch2 = seconds2
                            decay_waiting_ch2 = True
                            pulse_ch2 = True
                            wait_fe2 = False
                        else:
                            decay_waiting_ch2 = False
                            
                            
                    if re_3 and dpch3==1:
                        wait_fe3 = True
                        time_ch3 = seconds3
                        if time_ch3 - seconds3 > 50e-9:
                            wait_f3 = False
                        if fe_3 and wait_fe3:
                            print "Pulse ch2",seconds3,line
                            decay_start_time_ch3 = seconds3
                            decay_waiting_ch3 = True
                            pulse_ch3 = True
                            wait_fe3 = False
                        else:
                            decay_waiting_ch3 = False
                            
                        #seconds0=decay_start_time_ch0 
                        #seconds1=decay_start_time_ch1
                        #seconds2=decay_start_time_ch2
                        #seconds3=decay_start_time_ch3

                if fields_next[1]>= "80":
                    previous_fe_0 = fe_0
                    previous_re_1 = re_1
                    previous_fe_1 = fe_1
                    previous_re_2 = re_2
                    previous_fe_2 = fe_2
                    previous_re_3 = re_3
                    previous_fe_3 = fe_3
                    break
            
