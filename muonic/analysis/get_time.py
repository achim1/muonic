#! /usr/bin/env python

import sys

# what frequency is the correct one?
# 41 or 25?
# assuming 41..
#freq = 25.0e6
freq = 41.0e6

def time_to_seconds(time, correction):
    '''
    Convert hhmmss,xxx string int seconds since day start
    '''
#    print time,correction
    tfields = time.split(".")
    t = tfields[0]
    secs_since_day_start = int(t[0:2])*3600+int(t[2:4])*60+int    (t[4:6])
    evt_time = secs_since_day_start + int(tfields[1])/1000.0+int(correction)/1000.0
    #return round(evt_time)
    return evt_time

def get_time(fields,last_onepps_count):
    try:
        trigger_count = int(fields[0],16)
        onepps_count = int(fields[9],16)
    except IndexError:
        return None
    if onepps_count != last_onepps_count:
        last_onepps_count = onepps_count
    time = fields[10]
    correction = fields[15]
    
    line_time = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq

#line_time = seconds + (trigger_count - onepps_coun    t)/freq     
    return line_time


if __name__ == '__main__':

    last_onepps_count = 0
    f = open(sys.argv[1])
    ini = True
    for line in f.readlines():
            line = line.split()
            try:
                    if ini:
                            start = get_time(line,last_onepps_count)
                            ini= False
    
                    stop = get_time(line,last_onepps_count)
            except ValueError:
                    print 'Error',line
                    pass
    print start
    print (stop - start)/3600
