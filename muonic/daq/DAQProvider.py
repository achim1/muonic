
import multiprocessing as mult
import logging

from SimDaqConnection import SimDaqConnection
from DaqConnection import DaqConnection


class DAQProvider:
    """
    Launch the main part of the GUI and the worker threads. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """

    def __init__(self,logger=None,root=None,sim=False):

        self.outqueue = mult.Queue()
        self.inqueue  = mult.Queue()
            
        self.running = 1
        self.root = root

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
        # More can be made if necessary
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

        return self.outqueue.get(*args)
        

    def put(self,*args):
        """
        Send information to the daq
        """
        self.inqueue.put(*args)

    def data_available(self):
        """
        is new data from daq available
        """

        return self.outqueue.qsize()

