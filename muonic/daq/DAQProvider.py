
import multiprocessing as mult
import logging
import re
import Queue

try:
    import zmq
except ImportError:
    print "no zmq installed..."

from SimDaqConnection import SimDaqConnection,SimDaqServer
from DaqConnection import DaqConnection,DaqServer

class DAQIOError(IOError):
    pass


class DAQProvider:
    """
    Launch the main part of the GUI and the worker threads. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self,logger=None,sim=False):

        self.outqueue = mult.Queue()
        self.inqueue  = mult.Queue()
            
        self.running = 1
        self.good_pattern = re.compile("^[a-zA-Z0-9+-.,:()=$/#?!%_@*|~' ]*[\n\r]*$")
        # get option parser options
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        self.sim = sim

        if self.sim:
            self.daq = SimDaqConnection(self.inqueue, self.outqueue, self.logger)

        else:
            self.daq = DaqConnection(self.inqueue, self.outqueue, self.logger)
        
        # Set up the thread to do asynchronous I/O
        # Set daemon flag so that the threads finish when the main app finishes
        self.readthread = mult.Process(target=self.daq.read,name="pREADER")
        self.readthread.daemon = True
        self.readthread.start()
        if not self.sim:
            self.writethread = mult.Process(target=self.daq.write,name="pWRITER")
            self.writethread.daemon = True
            self.writethread.start()
        
    def get(self,*args):
        """
        Get something from the daq
        """
        line = None
        try:
            line = self.outqueue.get(*args)
        except Queue.Empty:
            raise DAQIOError("Queue is empty")
        
        if self.good_pattern.match(line) is None:
            # Do something more sensible here,     like stopping the DAQ
            # then wait until service is restar    ted?
            self.logger.warning("Got garbage from the DAQ: %s"%line.rstrip('\r\n'))
            return None
        return line
        
    def put(self,*args):
        """
        Send information to the daq
        """
        self.inqueue.put(*args)

    def data_available(self):
        """
        check if there is new data from daq available
        """
        size = None
        try:
            size = self.outqueue.qsize()
        except NotImplementedError:
            self.logger.debug("Running Mac version of muonic.")
            size = not self.outqueue.empty()
        return size

class DAQClient(DAQProvider):
    """
    ZMQ Client site of the DAQ hadling.
    """
    def __init__(self,port,logger=None,root=None):
           
        self.running = 1
        self.root = root
        self.good_pattern = re.compile("^[a-zA-Z0-9+-.,:()=$/#?!%_@*|~' ]*[\n\r]*$")
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        self.setup_socket(port)
     
    def setup_socket(self,port):
        """
        Setup the ZMQ socket
        """
        #port = "5556"
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://127.0.0.1:%s" % port)
        self.socket_port = port 
        
    def get(self,*args):
        """
        Get something from the daq
        """
        line = None
        try:
            line = self.socket.recv_string()
        except Queue.Empty:
            raise DAQIOError("Queue is empty")
        
        if self.good_pattern.match(line) is None:
            # Do something more sensible here,     like stopping the DAQ
            # then wait until service is restar    ted?
            self.logger.warning("Got garbage from the DAQ: %s"%line.rstrip('\r\n'))
            return None
            #raise DAQIOError("Queue contains garbage!")
        
        return line
        

    def put(self,*args):
        """
        Send information to the daq
        """
        self.socket.send_string(*args)

    def data_available(self):
        """
        is new data from daq available
        """
        return self.socket.poll(200)
