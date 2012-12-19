import matplotlib.pyplot as mp
import sys
import pylab as p
import numpy as n


# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui

# Matplotlib Figure object
from matplotlib.figure import Figure

# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt4agg \
import FigureCanvasQTAgg as FigureCanvas

# import the NavigationToolbar Qt4Agg widget
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar


class LifetimeCanvas(FigureCanvas):
    """
    A simple histogram for the use with mu lifetime
    measurement
    """
    
    
    def __init__(self,parent,logger):
       
        self.logger = logger
        self.logger.debug("Lifetimemonitor started")

        # first image setup
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)


        # set specific limits for X and Y axes
        self.ax.set_ylim(ymin=0)
        self.ax.set_xlabel('time between pulses (microsec)')
        self.ax.set_ylabel('events')

        # make a fixed binning from 0 to 20 microseconds
        self.binning = n.linspace(0,20,84)
        self.bincontent   = self.ax.hist(n.array([]), self.binning, fc='b', alpha=0.25)[0]
        self.hist_patches = self.ax.hist(n.array([]), self.binning, fc='b', alpha=0.25)[2]
         
        # force a redraw of the Figure
        self.fig.canvas.draw()
 
        self.setParent(parent)
        self.heights = []


    def update_plot(self, decaytimes):
        """
        decaytimes must be a list of the last decays
        """

        # avoid memory leak
        self.ax.clear()

        # we have to do some bad hacking here,
        # because the p histogram is rather
        # simple and it is not possible to add
        # two of them...
        # however, since we do not want to run into a memory leak
        # and we also be not dependent on dashi (but maybe
        # sometimes in the future?) we have to do it
        # by manipulating rectangles...

        # we want to find the non-empty bins
        # tmphist is compatible with the decaytime hist...


        tmphist = self.ax.hist(decaytimes, self.binning, fc='b', alpha=0.25)[0]

        for histbin in enumerate(tmphist):
            if histbin[1]:
                self.hist_patches[histbin[0]].set_height(self.hist_patches[histbin[0]].get_height() + histbin[1])
            else:
                pass

        # we want to get the maximum for the ylims
        # self.heights contains the bincontent!

        self.heights = []
        for patch in self.hist_patches:
            self.heights.append(patch.get_height())

        self.logger.debug('lifetimemonitor heights %s' %self.heights.__repr__())
        self.ax.set_ylim(ymax=max(self.heights)*1.1)
        self.ax.set_ylim(ymin=0)
        self.ax.set_xlabel('time between pulses (microsec)')
        self.ax.set_ylabel('events')
        
        # always get rid of unused stuff
        del tmphist

        # some beautification
        self.ax.grid()
 
        # we now have to pass our new patches 
        # to the figure we created..            
        self.ax.patches = self.hist_patches      
        self.fig.canvas.draw()

    def show_fit(self,bin_centers,bincontent,fitx,decay,p,covar,chisquare,nbins):

        #self.ax.clear()

        self.ax.plot(bin_centers,bincontent,"b^",fitx,decay(p,fitx),"b-")
        self.ax.set_ylim(0,max(bincontent)*1.2)
        self.ax.set_xlabel("Decay time in microseconds")
        self.ax.set_ylabel("Events in time bin")
        try:
            self.ax.legend(("Data","Fit: (%4.2f +- %4.2f) $\mu$s \n chisq/ndf=%4.2f"%(p[1],n.sqrt(covar[1][1]),chisquare/(nbins-len(p)))),loc=1)
        except TypeError:
            self.logger.warn('Covariance Matrix is None, could not calculate fit error!')
            self.ax.legend(("Data","Fit: (%4.2f) $\mu$s \n chisq/ndf=%4.2f"%(p[1],chisquare/(nbins-len(p)))),loc=1)
            
        
        self.fig.canvas.draw()



