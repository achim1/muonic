"""
Provides a simple DAQ card simulation, so that software can be tested
"""

import time
import Queue
import numpy as n
import os

try:
	import zmq
except ImportError:
	print "no zmq installed..."
	
from random import choice
	
class SimDaq():

    def __init__(self, logger,usefile="simdaq.txt",createfakerates=True):
        
        # TODO:
        # Modify this in such a way that
        # an arbitrary file can be read and computed...
        
        self.logger = logger
        self.ini = True

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
        if self.ini:
            self.ini = False
            return "T0=42  T1=42  T2=42  T3=42"

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
            time.sleep(0.1)
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
                    #print self.inqueue.get(0)
                    self.port.write(str(self.inqueue.get(0))+"\r")
                except Queue.Empty:
                    self.logger.debug("Queue empty!")
            
            while self.port.inWaiting():
                self.outqueue.put(self.port.readline().strip())
            time.sleep(0.02)

class SimDaqServer(object):

    def __init__(self, port, logger):

        self.logger = logger
        self.port = SimDaq(self.logger)
        self.running = 1
        self.setup_socket(port)
        

    def setup_socket(self,port,adress="127.0.0.1"):
        #port = "5556"
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.bind("tcp://%s:%s" %(adress, port))
        self.socket_adress = adress
        self.socket_port = port

    def serve(self):
        while True:
            self.read()
		
    def read(self):
        """
        Simulate DAQ I/O
        """
        while self.running:
            
            #self.logger.debug("inqueue size is %d" %self.inqueue.qsize())
            msg = self.socket.recv_string()
            print msg
            try:
                    #print self.inqueue.get(0)
                self.port.write(str(msg)+"\r")
            except Queue.Empty:
                self.logger.debug("Queue empty!")
            
            while self.port.inWaiting():
                self.socket.send_string(self.port.readline().strip())
            time.sleep(0.02)

if __name__ == "__main__":
    
    import logging
    logger = logging.getLogger()
    x = SimDaqServer("5556",logger)
    x.serve()
