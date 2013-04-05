"""
Provides a simple DAQ card simulation, so that software can be tested
"""

import time
import Queue
import numpy as n
import os


from random import choice
	
class SimDaq():

    def __init__(self, logger,usefile="simdaq.txt",createfakerates=True):
        
        # TODO:
        # Modify this in such a way that
        # an arbitrary file can be read and computed...
        
        self.logger = logger
        self._pushed_lines = 0
        self._lines_to_push = 10
        self._simdaq_file = os.path.split(os.path.abspath(__file__))[0] + os.sep + usefile
        self._daq = open(self._simdaq_file)
        self._inWaiting = True 
        self._return_info = False
        
        #self._fakerates = createfakerates
        self._scalars_ch0 = 0
        self._scalars_ch1 = 0
        self._scalars_ch2 = 0
        self._scalars_ch3 = 0
        self._scalars_trigger = 0
        self._scalars_to_return = ''

    def _physics(self):
        """
        This routine will increase the scalars variables using predefined rates
        Rates are drawn from Poisson distributions
        """

        def format_to_8digits(hexstring):
            return hexstring.zfill(8)
        
        
        # draw rates from a poisson distribution,
        self._scalars_ch0 += int(choice(n.random.poisson(12,100)))
        self._scalars_ch1 += int(choice(n.random.poisson(10,100)))
        self._scalars_ch2 += int(choice(n.random.poisson(8,100)))
        self._scalars_ch3 += int(choice(n.random.poisson(11,100)))
        self._scalars_trigger += int(choice(n.random.poisson(2,100)))
        self._scalars_to_return = 'DS S0=' + format_to_8digits(hex(self._scalars_ch0)[2:]) + ' S1=' + format_to_8digits(hex(self._scalars_ch1)[2:]) + ' S2=' + format_to_8digits(hex(self._scalars_ch2)[2:]) + ' S3=' + format_to_8digits(hex(self._scalars_ch3)[2:]) + ' S4=' + format_to_8digits(hex(self._scalars_trigger)[2:])
        self.logger.debug("Scalars to return %s" %self._scalars_to_return)


    def readline(self):
        """
        read dummy pulses from the simdaq file till
        the configured value is reached
        """

        if self._return_info:
            self._return_info = False
            return self._scalars_to_return

        self._pushed_lines += 1
        if self._pushed_lines < self._lines_to_push:
            line = self._daq.readline()
            if not line:
                self._daq = open(self._simdaq_file)
                self.logger.debug("File reloaded")
                line = self._daq.readline()

            return line
        else:
            self._pushed_lines = 0
            self._inWaiting = False
            return self._daq.readline()
            

    def write(self,command):
        """
        Trigger a simulated daq response with command
        """
        self.logger.debug("got the following command %s" %command.__repr__())
        if "DS" in command:
            self._return_info = True

    def inWaiting(self):
        """
        simulate a busy DAQ
        """
        if self._inWaiting:
            time.sleep(0.01)
            self._physics()
            return True

        else:
            self._inWaiting = True
            return False
        
class SimDaqConnection(object):

    def __init__(self, inqueue, outqueue, logger):

        self.logger = logger
        self.port = SimDaq(self.logger)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.running = 1

    def read(self):
        """
        Simulate DAQ I/O
        """
        while self.running:
            
            self.logger.debug("inqueue size is %d" %self.inqueue.qsize())
            while self.inqueue.qsize():
                try:
                    self.port.write(str(self.inqueue.get(0))+"\r")
                except Queue.Empty:
                    self.logger.debug("Queue empty!")
            
            while self.port.inWaiting():
                self.outqueue.put(self.port.readline().strip())
            time.sleep(0.02)


