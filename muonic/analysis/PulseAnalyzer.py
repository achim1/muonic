"""
Get the absolute timing of the pulses
by use of the gps time
Calculate also a non hex representation of
leading and falling edges of the pulses
"""

#TODO: IMPORTANT -> How long is a triggerwindow? If the triggercondition is set, are also "untriggered" pulses written? Or only those which belong to the trigger? 

# for the pulses 
# 8 bits give a hex number
# but only the first 5 bits are used for the pulses time,
# the fifth bit flags if the pulse is considered valid
# the seventh bit should be the triggerflag...

BIT0_4 = 31
BIT5 = 1 << 5
BIT7 = 1 << 7

# For DAQ status
BIT0 = 1 # 1 PPS interrupt pending
BIT1 = 1 << 1 # Trigger interrupt pending
BIT2 = 1 << 2 # GPS data possible corrupted
BIT3 = 1 << 3 # Current or last 1PPS rate not within range

# ticksize of tmc internal clock
# documentation says 0.75, measurement says 1.25
# TODO: find out if tmc is coupled to cpld!
TMC_TICK = 1.25 #nsec
#MAX_TRIGGERWINDOW = 60.0 #nsec
MAX_TRIGGERWINDOW = 9960.0 #nsec for mudecay!
DEFAULT_FREQUENCY = 25.0e6


class PulseExtractor:
    """
    get the pulses out of a daq line
    speed is important here
    """

    def __init__(self,pulsefile=''):
        """
        if a pulsefile is given, all the extracte pulses
        will be written into it
        """
 
        #TODO change to dictionaries, they might allthoug be faster
        
        self.re      = {"ch0" : [], "ch1" : [], "ch2" : [], "ch3" : [] }
        self.fe      = {"ch0" : [], "ch1" : [], "ch2" : [], "ch3" : [] }
        self.last_re = {"ch0" : [], "ch1" : [], "ch2" : [], "ch3" : [] }
        self.last_fe = {"ch0" : [], "ch1" : [], "ch2" : [], "ch3" : [] }

        # ini will be False if we have seen the first 
        # trigger
        # store items if Events are longer than one line
        self.ini                 = True
        self.lastonepps          = 0
        self.lasttriggertime     = 0
        self.trigger_count       = 0
        self.lasttime            = 0


        # store the actual value of
        # the trigger counter
        # to correct trigger counter rollover
        self.lasttriggercount = 0

        # TODO find a generic way to account
        # for the fact that the default
        # cna be either 25 or 41 MHz
        # variables for DAQ frequency calculation
        self.lastfrequencypolltime = 0
        self.lastfrequencypolltriggers = 0
        self.calculatedfrequency = DEFAULT_FREQUENCY
        self.lastoneppspoll      = 0
        self.passedonepps        = 0 
        self.prevlast_onepps     = 0

        #self.debug_freq = open('frequency.txt','w')
        #self.debug_freq.write('#  sec (le (nsec), fe(nsec)) chan0 chan1 chan2 chan3 \n')
        if pulsefile:
            self.pulsefile = open(pulsefile,'w')           
        else:
            self.pulsefile = False

    def _calculate_edges(self,line,counter_diff=0):
        """
        get the leading and falling edges of the pulses
        Use counter diff for getting pulse times in subsequent 
        lines of the triggerflag
        """
        
        rising_edges  = {"ch0" : int(line[1],16), "ch1" : int(line[3],16), "ch2" : int(line[5],16), "ch3" :int(line[7],16)}
        falling_edges  = {"ch0" : int(line[2],16), "ch1" : int(line[4],16), "ch2" : int(line[6],16), "ch3" :int(line[8],16)}


        for ch in ["ch0","ch1","ch2","ch3"]:
            re = rising_edges[ch]
            fe = falling_edges[ch]
            if (re & BIT5):
                self.re[ch].append(counter_diff + (re & BIT0_4)*TMC_TICK ) 
            if (fe & BIT5):
                self.fe[ch].append(counter_diff + (fe & BIT0_4)*TMC_TICK ) 



    def _order_and_cleanpulses(self):
        """
        Remove pulses which have a 
        leading edge later in time than a 
        falling edge and do a bit of sorting
        Remove also single leading or falling edges
        NEW: We add virtual falling edges!
        """
        pulses  = {"ch0" : [], "ch1" : [], "ch2" : [], "ch3" : [] }


        for ch in ["ch0","ch1","ch2","ch3"]:
            
            for index,re in enumerate(self.last_re[ch]):
                # add the virtual falling edge if necessary
                try:
                    fe = self.last_fe[ch][index]
                    if fe < re:
                        fe = MAX_TRIGGERWINDOW 
                except IndexError:
                    fe = MAX_TRIGGERWINDOW
                    
                pulses[ch].append((re,fe))

           # self.pulses[ch] = [(re,fe) for re,fe in self.last_re[ch],self.last_fe[ch])
           # for i in self.pulses[ch]:
           #     if not i[0] < i[1]:
           #         #self.chan0.remove(i)
           #         self.pulses[ch] = (i[0],MAX_TRIGGERWINDOW)
        return pulses

    def _get_evt_time(self,time,correction,trigger_count,onepps):
        """
        Get the absolute event time in seconds since day start
        If gps is not available, only relative eventtime based on counts
        is returned
        """
        tfields = time.split(".")
        t = tfields[0]

        secs_since_day_start = int(t[0:2])*3600+int(t[2:4])*60+int(t[4:6])

        # FIXME: Why tfields[1]/1000?
        gps_time = float(secs_since_day_start + int(tfields[1])/1000.0+int(correction)/1000.0)

        line_time = gps_time + float((trigger_count - onepps)/self.calculatedfrequency)
        return line_time


    def extract(self,line):
        """
        Analyze subsequent lines (one per call)
        and check if pulses are related to triggers
        For each new trigger,
        return the set of pulses which belong to that trigger,
        otherwise return None
        """

        line = line.split()

        onepps        = int(line[9],16)
        trigger_count = int(line[0],16)
        time          = line[10]

        # correct for triggercount rollover
        if trigger_count < self.lasttriggercount:
            trigger_count += int(0xFFFFFFFF) # counter offset

        self.trigger_count = trigger_count
        
        switched_onepps = False
        if onepps != self.lastonepps:
            self.passedonepps += 1
            # poll every x lines for the frequency
            # check for onepps counter rollover
            if onepps < self.lastonepps:
                onepps += int(0xFFFFFFFF)
        
            switched_onepps = True
            
            # calculate the frequency every x onepps
            if not self.passedonepps%5:
                self.calculatedfrequency = (onepps - self.lastoneppspoll)/float(self.passedonepps)
                self.passedonepps = 0
                self.lastoneppspoll = onepps
                # check if calculatedfrequency is sane,
                # assuming the daq frequency is somewhat stable
                if not 0.5*self.calculatedfrequency < DEFAULT_FREQUENCY < 1.5*self.calculatedfrequency:
                    self.calculatedfrequency = DEFAULT_FREQUENCY

       
            if time == self.lasttime: 
            # correcting for delayed onepps swicth
                linetime = self._get_evt_time(line[10],line[15],trigger_count,self.lastonepps)
            else:
                linetime = self._get_evt_time(line[10],line[15],trigger_count,onepps)


        else:
            linetime = self._get_evt_time(line[10],line[15],trigger_count,onepps)

        # storing the last two onepps switches
        self.prevlast_onepps = self.lastonepps
        self.lastonepps = onepps

        self.lasttime = time

        if int(line[1],16) & BIT7: # a triggerflag!
            self.ini = False
             
            # a new trigger! we have to evaluate the last one and get the new pulses
        
            self.last_re = self.re
            self.last_fe = self.fe
            pulses = self._order_and_cleanpulses()
            extracted_pulses = (self.lasttriggertime,pulses["ch0"],pulses["ch1"],pulses["ch2"],pulses["ch3"])
            if self.pulsefile:
                self.pulsefile.write(extracted_pulses.__repr__() + '\n')

            # as the pulses for the last event are done, reinitialize data structures
            # for the next event
            self.lasttriggertime = linetime
            self.re = {"ch0" : [], "ch1" : [], "ch2" : [], "ch3" : [] }
            self.fe = {"ch0" : [], "ch1" : [], "ch2" : [], "ch3" : [] }

            # calculate edges of the new pulses
            self._calculate_edges(line)
            self.lasttriggercount = trigger_count 
        
            return extracted_pulses
        
        else:    
            # we do have a previous trigger and are now adding more pulses to the event
            #print 'notrigger',line
        
            if self.ini:
                self.lastonepps = int(line[9],16)
                
            else:
                counter_diff = 0
                counter_diff = (self.trigger_count - self.lasttriggercount)
                #print counter_diff, counter_diff > int(0xffffffff)
                if counter_diff > int(0xffffffff):
                    counter_diff -= int(0xffffffff)
        
                counter_diff = counter_diff/self.calculatedfrequency
                
                #print counter_diff,counter_diff*1e9,' edges diff'
       
                 
                self._calculate_edges(line,counter_diff=counter_diff*1e9)
        # end of if triggerflag

        self.lasttriggercount = trigger_count 


    def close_file(self):
        self.pulsefile.close()          



# trigger on a set of extracted pulses and look for decayed muons

class DecayTriggerThorough:
    """
    We demand a second pulse in the same channel where the muon got stuck
    Should operate for a 10mu sec triggerwindow
    """   

    def __init__(self,logger):
        self.triggerwindow = 10000 # 10 musec set at DAQ -> in ns since
                                   # TMC info is in nsec
        self.logger = logger
        self.logger.info("Initializing decay trigger, setting triggerwindow to %i" %self.triggerwindow)

    def trigger(self,triggerpulses,single_channel = 2, double_channel = 3, veto_channel = 4,selfveto=False,mindecaytime=0):
        """
        Trigger on a certain combination of single and doublepulses
        """ 
        #print single_channel, double_channel, veto_channel,mindecaytime

        ttp = triggerpulses       

        pulses1 = len(ttp[single_channel]) # single pulse 
        pulses2 = len(ttp[double_channel]) # double pulse
        pulses3 = len(ttp[veto_channel])   # veto pulses
        time    = ttp[0]

        decaytime = 0

        # reject events with too few pulses
        # in some setups good value will be three
        # (single pulse + double pulse required)
        # and no hits in the veto channel3
        # change this if only one channel is available

        if (pulses1 + pulses2 < 2) or pulses3:
            # reject event if it has to few pulses
            # or veto pulses
            self.logger.debug("Rejecting decay with singlepulses %s, doublepulses %s and vetopulses %s" %(pulses1.__repr__(),pulses2.__repr__(),pulses3.__repr__()))
            return None

        # check if the muon entered the first channel and
        # decayed there
        # use the selfveto flag to reject the event
        # if there are pulses in the "doublepulsechannel"
        # this makes sense if the muon decayed in the first
        # channel
        # ..


        if (pulses1 >= 1) and ((not selfveto) or (not pulses2 )):
            # RE2 - LE1
            decaytime = ttp[single_channel][-1][1] - ttp[single_channel][0][0]
        
        # or it might have entered the second channel
        # then we do not want to have more than one
        # hit in the first    
        # again: use selfveto to adjust the behavior
        if (pulses2 == 2) and ((pulses1 == 1) or (not selfveto)):
            # subtract rising edges, falling edges might be virtual
            decaytime = ttp[double_channel][-1][0] - ttp[double_channel][0][0]
             


        # perform sanity checks
        if (decaytime > mindecaytime) and (decaytime < self.triggerwindow):
            self.logger.debug("Decay with decaytime %d found " %decaytime)
            return decaytime



if __name__ == '__main__':

    	
    import sys 

    data = open(sys.argv[1])
    extractor = PulseExtractor()
    while True:
        line = data.readline()
        if not line:
            break
        try:
            extractor.extract(line)
            #print extractor.extract(line)
        except (ValueError,IndexError):
            pass 



