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
    """
    Simulation mode reproduces rates from an file, drwan from a Poisson distribution.
    This routine will increase the scalars variables using predefined rates
    Rates are drawn from Poisson distributions
    """

    def __init__(self, logger,usefile="simdaq.txt",createfakerates=True):
                
        self.logger = logger

        self._pushed_lines = 0
        self._lines_to_push = 10
        self._simdaq_file = os.path.split(os.path.abspath(__file__))[0] + os.sep + usefile
        self._daq = open(self._simdaq_file)
        self._inWaiting = True 
        self._return_info = False
        self._cmd_buffer = None
        self._cmd_waiting = False
        
        #self._fakerates = createfakerates
        self._scalars_ch0 = 0
        self._scalars_ch1 = 0
        self._scalars_ch2 = 0
        self._scalars_ch3 = 0
        self._scalars_trigger = 0
        self._scalars_to_return = ''
        self.known_commands = dict({
            'TL':'T0=42  T1=42  T2=42  T3=42',
            'HE':'Help page missing',
            'HE1':'Help page 1 missing',
            'HE2':'Help page 2 missing',
            'HE3':'Help page 3 missing',
            'DC':'DC answer missing',
            'WC':'WC answer missing',
            'TC':'TC answer missing',
            'V1':'V1 answer missing'
            })

    def _physics(self):

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

        if self._cmd_waiting:
            self._cmd_waiting = False
            return self.known_commands.get(self._cmd_buffer)
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
        if len(command) > 1000:
            self.logger.warning("Ignoring command - too long. In case of server: might be an attack.")
            return False
        command = str(command).strip()
        self.logger.debug("got the following command %s" %command.__repr__())
        if command == "DS":
            self._return_info = True
            return True
        if self.known_commands.has_key(command.split(' ',1)[0]):
            self._cmd_buffer = command
            self._cmd_waiting = True
            return True
        else:
            return False

    def inWaiting(self):
        """
        simulate a busy DAQ
        """
        if self._inWaiting:
            time.sleep(0.3)
            self._physics()
            return True
        else:
            self._inWaiting = True
            return False
        
class SimDaqConnection(object):
    """
    Basic class which provides the simulated DAQ. It can be started via the DAQ server or if not zmq is available as stand alone locally
    """

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
            try:
                self.logger.debug("inqueue size is %d" %self.inqueue.qsize())
                while self.inqueue.qsize():
                    try:
                        _msg = str(self.inqueue.get(0))
                        self.outqueue.put(_msg)
                        self.port.write(_msg+"\r")
                    except Queue.Empty:
                        self.logger.debug("Queue empty!")
            except NotImplementedError:
                self.logger.debug("Running Mac version of muonic.")
                while True:
                    try:
                        _msg = str(self.inqueue.get(timeout=0.01))
                        self.outqueue.put(_msg)                    
                        self.port.write(_msg+"\r")
                    except Queue.Empty:
                        pass

            while self.port.inWaiting():
                self.outqueue.put(self.port.readline().strip())
            time.sleep(0.3)

class SimDaqServer(object):
    """
    Server site which simulates the DAQ.
    """

    def __init__(self, port, logger):

        self.logger = logger
        self.port = SimDaq(self.logger)
        self.running = 1
        self.setup_socket(port)
        

    def setup_socket(self,port,adress="127.0.0.1"):
        """
        setup up the socket for the simulated DAQ server
        """
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
            msg = self.socket.recv_string()
            #print msg
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
