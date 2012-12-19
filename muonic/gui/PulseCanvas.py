# for command-line arguments
import pylab as p
import numpy as n
from datetime import datetime

# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui

# Matplotlib Figure object
from matplotlib.figure import Figure
import matplotlib.patches as patches

# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt4agg \
import FigureCanvasQTAgg as FigureCanvas

# import the NavigationToolbar Qt4Agg widget
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

class PulseCanvas(FigureCanvas):
    """Matplotlib Figure widget to display Pulses"""


    def __init__(self, parent, logger):   
                
        self.logger = logger       
        
        # first image setup
        self.fig = Figure(facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.1, right=0.6)

        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)

        # set specific limits for X and Y axes
        self.ax.set_xlim(0, 40)
        self.ax.set_ylim(ymax=1.2)
        self.ax.grid()
        self.ax.set_xlabel('time in ns')

        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)
	

        # force a redraw of the Figure
        self.fig.canvas.draw()
        self.setParent(parent)
                     
    def color(self, string, color="none"):
        """output colored strings on the terminal"""
        colors = { "green": '\033[92m', 'yellow' : '\033[93m', 'red' : '\033[91m', 'blue' : '\033[94m', 'none' : '\033[0m'}
        return colors[color] + string + colors["none"]   


    def update_plot(self, pulses):

        
        #do a complete redraw of the plot to avoid memory leak!
        self.ax.clear()

        # set specific limits for X and Y axes
        self.ax.set_xlim(0, 40)
        self.ax.set_ylim(ymax=1.2)
        self.ax.grid()
        self.ax.set_xlabel('time in ns')

        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)

        # we have only the information that the pulse is over the threshold,
        # besides that we do not have any information about its height
        # TODO: It would be nice to implement the thresholds as scaling factors

        self.pulseheight = 1.0

        colors = ['b','g','r','c']
        labels = ['c0','c1','c2','c3']

        for chan in enumerate(pulses[1:]):
            for pulse in chan[1]:
                self.ax.plot([pulse[0],pulse[0],pulse[1],pulse[1]],[0,self.pulseheight,self.pulseheight,0],colors[chan[0]],label=labels[chan[0]],lw=2)
            

        try:
            self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0., handlelength=0.5)
        except:
            self.logger.info('An error with the legend occured!')
            self.ax.legend(loc=2)

        self.fig.canvas.draw()
        

