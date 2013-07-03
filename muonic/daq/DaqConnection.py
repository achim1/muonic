#! /usr/bin/env python

import Queue
import serial
import os
import subprocess 

try:
    import zmq
except ImportError:
    print "No zmq installed..."


import os.path as pth
from time import sleep

class DaqConnection(object):

    def __init__(self, inqueue, outqueue, logger):

        self.inqueue = inqueue
        self.outqueue = outqueue
        self.running = 1
        self.logger = logger

        try:
            self.port = self.get_port()
        except serial.SerialException, e:
            self.logger.fatal("SerialException thrown! Value:" + e.message.__repr__())
            raise SystemError, e

    def get_port(self):
        """
        check out which device (/dev/tty) is used for DAQ communication
        """
        connected = False
        while not connected:
            #which_tty_daq = os.path.split(os.path.abspath(__file__))[0] + os.sep + "which_tty_daq"

            try:
                dev = subprocess.Popen(["which_tty_daq"], stdout=subprocess.PIPE).communicate()[0]
            except OSError: # using package script
                which_tty_daq = os.path.abspath('./bin/which_tty_daq')
                if not os.path.exists(which_tty_daq):
                    raise OSError("Can not find binary which_tty_daq")
                dev = subprocess.Popen([which_tty_daq], stdout=subprocess.PIPE).communicate()[0]

            dev = "/dev/" + dev
            dev = dev.rstrip('\n')
            self.logger.info("Daq found at %s",dev)
            self.logger.info("trying to connect...")
            try:
                port = serial.Serial(port=dev, baudrate=115200,
                                     bytesize=8,parity='N',stopbits=1,
                                     timeout=0.5,xonxoff=True)
                connected = True
            except serial.SerialException, e:
                self.logger.error(e)
                self.logger.error("Waiting 5 seconds")
                sleep(5)

        self.logger.info("Successfully connected to serial port")
        return port



    def read(self):
        """
        Get data from the DAQ. Read it from the provided Queue.
        """
        min_sleeptime = 0.01 # seconds
        max_sleeptime = 0.2 # seconds
        sleeptime = min_sleeptime #seconds
        while self.running:
#            data = self.port.read(1)
#            n = self.port.inWaiting()
#            if n > 0:
#                data += self.port.read(n)
#            for line in data.split('\n'):
#                self.outqueue.put(line)
            try:
                if self.port.inWaiting():
                    while self.port.inWaiting():
                        self.outqueue.put(self.port.readline().strip())
                    sleeptime = max(sleeptime/2, min_sleeptime)
                else:
                    sleeptime = min(1.5 * sleeptime, max_sleeptime)
                sleep(sleeptime)

            except IOError:
                self.logger.error("IOError")
                self.port.close()
                self.port = self.get_port()
                # this has to be implemented in the future
                # for now, we assume that the card does not forget
                # its settings, only because the USB connection is
                # broken
                #self.setup_daq.setup(self.commandqueue)
            except OSError:
                self.logger.error("IOError")
                self.port.close()
                self.port = self.get_port()
                #self.setup_daq.setup(self.commandqueue)



    def write(self):
        """
        Put messages from the inqueue which is filled by the DAQ
        """

        while self.running:
            while self.inqueue.qsize():
                try:
                    self.port.write(str(self.inqueue.get(0))+"\r")
                except Queue.Empty:
                    pass
            
            sleep(0.1)


class DaqServer(DaqConnection):
    
    # FIXME make constructors consistent
    def __init__(self, port,logger):


        self.running = 1
        self.logger = logger
        self.setup_socket(port)
        try:
            self.port = self.get_port()
        except serial.SerialException, e:
            self.logger.fatal("SerialException thrown! Value:" + e.message.__repr__())
            raise SystemError, e

    
    
    def setup_socket(self,port,adress="127.0.0.1"):
        #port = "5556"
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket_port = port
        self.socket_adress = adress
        self.socket.bind("tcp://%s:%s" %(adress,port))

    def serve(self):
        while True:
            self.read()
            self.write()

    def read(self):
        """
        Get data from the DAQ. Read it from the provided Queue.
        """
        min_sleeptime = 0.01 # seconds
        max_sleeptime = 0.2 # seconds
        sleeptime = min_sleeptime #seconds
        while self.running:
#            data = self.port.read(1)
#            n = self.port.inWaiting()
#            if n > 0:
#                data += self.port.read(n)
#            for line in data.split('\n'):
#                self.outqueue.put(line)
            try:
                if self.port.inWaiting():
                    while self.port.inWaiting():
                        self.socket.send(self.port.readline().strip())
                    sleeptime = max(sleeptime/2, min_sleeptime)
                else:
                    sleeptime = min(1.5 * sleeptime, max_sleeptime)
                sleep(sleeptime)

            except IOError:
                self.logger.error("IOError")
                self.port.close()
                self.port = self.get_port()
                # this has to be implemented in the future
                # for now, we assume that the card does not forget
                # its settings, only because the USB connection is
                # broken
                #self.setup_daq.setup(self.commandqueue)
            except OSError:
                self.logger.error("IOError")
                self.port.close()
                self.port = self.get_port()
                #self.setup_daq.setup(self.commandqueue)

    def write(self):
        """
        Put messages from the inqueue which is filled by the DAQ
        """

        while self.running:
            msg = self.socket.recv_string()
            self.port.write(str(msg)+"\r")
            sleep(0.1)



if __name__ == "__main__":
    
    import logging
    logger = logging.getLogger()
    x = DaqServer("5556",logger)
    x.serve()
