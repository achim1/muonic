
import multiprocessing as mult

from SimDaqConnection import SimDaqConnection
from DaqConnection import DaqConnection


class DAQProvider():
    """
    Launch the main part of the GUI and the worker threads. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """

    def __init__(self,opts,logger,root):

        self.outqueue = mult.Queue()
        self.inqueue  = mult.Queue()
            
        self.running = 1
        self.root = root

        # get option parser options
        self.logger = logger
        self.sim = opts.sim

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
        
        

 

