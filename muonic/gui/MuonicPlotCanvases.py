"""
Provide the canvases for plots in muonic
"""

import matplotlib.pyplot as mp
import sys
import pylab as p
import numpy as n
from datetime import datetime

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

class MuonicPlotCanvas(FigureCanvas):
    """
    The base class of all muonic plot canvases
    """
    
    def __init__(self,parent,logger,ymin=0,ymax=10,xmin=0,xmax=10,xlabel="xlabel",ylabel="ylabel",grid=True):
       
        self.logger = logger
        
        self.fig = Figure(facecolor="white",dpi=72)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.1, right=0.75)
  
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)

        # set specific limits for X and Y axes
        #print ymin,ymax
        self.ax.set_ylim(ymin=ymin,ymax=ymax)
        self.ax.set_xlim(xmin=xmin,xmax=xmax)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_autoscale_on(False)
        self.ax.grid(grid)
        
        #store the limits for later 
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        # force a redraw of the Figure
        self.fig.canvas.draw() 
        self.setParent(parent)


    def color(self, string, color="none"):
        """
        output colored strings on the terminal
        """
        colors = { "green": '\033[92m', 'yellow' : '\033[93m', 'red' : '\033[91m', 'blue' : '\033[94m', 'none' : '\033[0m'}
        return colors[color] + string + colors["none"]   


    def update_plot(self):
        """
        Instructions to updated this plot
        implement this individually
        """
        self.logger.warning("Update plot is not implemented for this Canvas!")
        
        
class PulseCanvas(MuonicPlotCanvas):
    """
    Matplotlib Figure widget to display Pulses
    """

    def __init__(self,parent,logger):
        super(PulseCanvas,self).__init__(parent,logger,ymin=0,ymax=1.2,xmin=0,xmax=40,xlabel="time in ns",ylabel="ylabel",grid=True)
        self.ax.yaxis.set_visible(False)   
        self.ax.set_title("Oscilloscope") 
  
    def update_plot(self, pulses):
      
        #do a complete redraw of the plot to avoid memory leak!
        self.ax.clear()

        # set specific limits for X and Y axes
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(ymax=1.5)
        self.ax.grid()
        self.ax.set_xlabel('time in ns')
        self.ax.yaxis.set_visible(False)
        self.ax.set_title("Oscilloscope")
        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)

        # we have only the information that the pulse is over the threshold,
        # besides that we do not have any information about its height
        # TODO: It would be nice to implement the thresholds as scaling factors

        self.pulseheight = 1.0

        colors = ['b','g','r','c']
        labels = ['c0','c1','c2','c3']
        _pulsemax = []
        for chan in enumerate(pulses[1:]):
            for pulse in chan[1]:
                self.ax.plot([pulse[0],pulse[0],pulse[1],pulse[1]],[0,self.pulseheight,self.pulseheight,0],colors[chan[0]],label=labels[chan[0]],lw=2)
                _pulsemax.append(pulse[0])
                _pulsemax.append(pulse[1])

        _pulsemax = max(_pulsemax)*1.2
        # TODO: the trick below does not really work as expected. 
        #if _pulsemax < self.ax.get_xlim()[1]:
        #    _pulsemax = self.ax.get_xlim()[0]
        self.ax.set_xlim(0, _pulsemax)
        try:
            self.ax.legend(loc=1, ncol=5, mode="expand", borderaxespad=0., handlelength=0.5)
        except:
            self.logger.info('An error with the legend occured!')
            self.ax.legend(loc=2)

        self.fig.canvas.draw()
        
        
class ScalarsCanvas(MuonicPlotCanvas):
    
    def __init__(self,parent,logger):
        
        MuonicPlotCanvas.__init__(self,parent,logger,xlabel="Time in s",ylabel="Rate in Hz")
        self.do_not_show_trigger = False
        #max length of shown = MAXLENGTH*timewindow
        self.MAXLENGTH = 40
        self.reset()
        
    def reset(self):
        """reseting all data"""

        self.ax.clear()
        self.ax.grid()
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        # and disable figure-wide autoscale
        #self.ax.set_autoscale_on(False)
        self.highest=0
        self.lowest=0
        self.now = datetime.now()#.strftime('%d.%m.%Y %H:%M:%S')
        #self.ax.set_xlim(0., 5.2)
        #self.ax.set_ylim(0., 100.2)
        
        self.timewindow = 0
        self.chan0, self.chan1, self.chan2, self.chan3, self.trigger, self.l_time =[], [], [], [], [], []
        self.l_chan0, = self.ax.plot(self.l_time,self.chan0, c='y', label='ch0',lw=3)
        self.l_chan1, = self.ax.plot(self.l_time,self.chan1, c='m', label='ch1',lw=3)
        self.l_chan2, = self.ax.plot(self.l_time,self.chan2, c='c',  label='ch2',lw=3)
        self.l_chan3, = self.ax.plot(self.l_time,self.chan3, c='b', label='ch3',lw=3)
        if not self.do_not_show_trigger:
            self.l_trigger, = self.ax.plot(self.l_time,self.trigger, c='g', label='trg',lw=3)

        self.N0 = 0
        self.N1 = 0
        self.N2 = 0
        self.N3 = 0
        self.NT = 0
        
        self.fig.canvas.draw()

    def update_plot(self, result):

        #do a complete redraw of the plot to avoid memory leak!
        self.ax.clear()

        # set specific limits for X and Y axes
        #self.ax.set_xlim(0., 5.2)
        #self.ax.set_ylim(0., 100.2)
        self.ax.grid()
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        # and disable figure-wide autoscale
        #self.ax.set_autoscale_on(False)
        self.logger.debug("result : %s" %result.__repr__())

        # update lines data using the lists with new data
        self.chan0.append(result[0])
        self.chan1.append(result[1])
        self.chan2.append(result[2])
        self.chan3.append(result[3])
        self.trigger.append(result[4])
        self.timewindow += result[5]
        self.l_time.append(self.timewindow)
        self.N0 += result[6]
        self.N1 += result[7]
        self.N2 += result[8]
        self.N3 += result[9]
        self.NT += result[10]

        self.l_chan0, = self.ax.plot(self.l_time,self.chan0, c='y', label='ch0',lw=2,marker='v')
        self.l_chan1, = self.ax.plot(self.l_time,self.chan1, c='m', label='ch1',lw=2,marker='v')
        self.l_chan2, = self.ax.plot(self.l_time,self.chan2, c='c', label='ch2',lw=2,marker='v')
        self.l_chan3, = self.ax.plot(self.l_time,self.chan3, c='b', label='ch3',lw=2,marker='v')
        if not self.do_not_show_trigger:
            self.l_trigger, = self.ax.plot(self.l_time,self.trigger, c='g', label='trg',lw=2,marker='x')

        try:
            if self.do_not_show_trigger:
                self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., handlelength=2)
            else:
                self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0., handlelength=2)
            
        except:
            self.logger.info('An error with the legend occured!')
            self.ax.legend(loc=2)

        if len(self.chan0) >  self.MAXLENGTH:
            self.chan0.remove(self.chan0[0])
            self.chan1.remove(self.chan1[0])
            self.chan2.remove(self.chan2[0])
            self.chan3.remove(self.chan3[0])
            self.trigger.remove(self.trigger[0])
            self.l_time.remove(self.l_time[0])

      
        self.logger.debug("self.l_chan0: %s" %self.l_chan0.__repr__())
        ma2 = max( max(self.chan0), max(self.chan1), max(self.chan2), 
                   max(self.chan3))
        mi2 = min( min(self.chan0), min(self.chan1), min(self.chan2), 
                       min(self.chan3), min(self.trigger))
        
        if ma2 > self.highest:
            self.highest = ma2
        if mi2 < self.lowest:
            self.lowest = mi2
        
        self.logger.debug("Chan0 to plot: %s", self.chan0.__repr__())
        
        ma = max( max(self.chan0), max(self.chan1), max(self.chan2),max(self.chan3), max(self.trigger)  )
            
        self.ax.set_ylim(0, ma*1.1)
        self.ax.set_xlim(self.l_time[0], self.l_time[-1])

        now2 = datetime.now()
        dt = (now2 - self.now)  
        dt1 = dt.seconds + dt.days * 3600 * 24
        string1 = 'started:\n %s ' % self.now.strftime('%d.%m.%Y %H:%M:%S')

        # we rather calculate the mean rate by dividing
        # total scalars by total time
        try:
            string2 = 'mean rates:\nchannel0 = %.2f Hz \nchannel1 = %.2f Hz \nchannel2 = %.2f Hz \nchannel3 = %.2f Hz \ntrigger = %.3f Hz' % ( (self.N0)/self.timewindow, (self.N1)/self.timewindow , (self.N2)/self.timewindow, (self.N3)/self.timewindow, (self.NT)/self.timewindow )
            if self.do_not_show_trigger:
                string2 = 'mean rates\nchannel0 = %.2f Hz \nchannel1 = %.2f Hz \nchannel2 = %.2f Hz \nchannel3 = %.2f Hz' % ( (self.N0)/self.timewindow, (self.N1)/self.timewindow , (self.N2)/self.timewindow, (self.N3)/self.timewindow )

        except ZeroDivisionError:
            self.logger.debug('Time was Zero!Passing..')
            string2 = ''
            pass

        string3 = 'total scalars:\nN0 = %i \nN1 = %i \nN2 = %i \nN3 = %i \nNT = %i' % (self.N0, self.N1, self.N2, self.N3, self.NT)
        if self.do_not_show_trigger:
            string3 = 'total scalars:\nN0 = %i \nN1 = %i \nN2 = %i \nN3 = %i' % (self.N0, self.N1, self.N2 , self.N3)

        # reduce information for better overview
        string4 = '\ndaq time = %.2f s \nmax rate = %.2f Hz' % (  self.timewindow, ma2 )
                             
        self.ax.text(1.1, -0.1, string1+string4, transform=self.ax.transAxes) 
        self.ax.text(1.1, 0.15, string3, transform=self.ax.transAxes, color='blue') 
        self.ax.text(1.1, 0.65, string2, transform=self.ax.transAxes, color='green') 
                   
        self.fig.canvas.draw()

class MuonicHistCanvas(MuonicPlotCanvas):
    """
    A base class for all canvases with a histogram
    """
     
    def __init__(self,parent,logger,binning,histcolor="b",**kwargs): 
        #super(MuonicHistCanvas,self).__init__(self,parent,logger,**kwargs)
        MuonicPlotCanvas.__init__(self,parent,logger,**kwargs)
        self.binning = binning
        self.bincontent   = self.ax.hist(n.array([]), self.binning, fc=histcolor, alpha=0.25)[0]
        self.hist_patches = self.ax.hist(n.array([]), self.binning, fc=histcolor, alpha=0.25)[2]
        self.heights = []
        self.underflow = 0 #FIXME the current implementation does not know about outliers
        self.overflow  = 0 #FIXME the current implementation does not know about outliers
        self.dimension = r"$\mu$s"
        
        
    def update_plot(self,data):    

        if not data:
            return None

        # avoid memory leak
        self.ax.clear()

        _max_xval = self.ax.get_xlim()[1]
        if not data is None:
            if len(data) > 0:
                _max_xval = 1.2*max(data)

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
        tmphist = self.ax.hist(data, self.binning, fc="b", alpha=0.25)[0]

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

        self.logger.debug('Histogram patch heights %s' %self.heights.__repr__())
        self.ax.set_ylim(ymax=max(self.heights)*1.1)
        self.ax.set_ylim(ymin=0)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        if _max_xval < self.ax.get_xlim()[1] or _max_xval*5. > self.ax.get_xlim()[1]:
            _max_xval = self.ax.get_xlim()[1]
        self.ax.set_xlim(xmax=_max_xval)
        
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
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        try:
            self.ax.legend(("Data","Fit: (%4.2f +- %4.2f) %s  \n chisq/ndf=%4.2f"%(p[1],n.sqrt(covar[1][1]),self.dimension,chisquare/(nbins-len(p)))),loc=1)
        except TypeError:
            self.logger.warn('Covariance Matrix is None, could not calculate fit error!')
            self.ax.legend(("Data","Fit: (%4.2f) %s \n chisq/ndf=%4.2f"%(p[1],self.dimension,chisquare/(nbins-len(p)))),loc=1)
                   
        self.fig.canvas.draw()


class LifetimeCanvas(MuonicHistCanvas):
    """
    A simple histogram for the use with mu lifetime
    measurement
    """
    
    def __init__(self,parent,logger):       
        MuonicHistCanvas.__init__(self,parent,logger,n.linspace(0,10,21),xlabel="time between pulses (microseconds)",ylabel="events")

     
class VelocityCanvas(MuonicHistCanvas):  
    
    def __init__(self,parent,logger): 
        #super(VelocityCanvas,self).__init__(self,parent,logger,binning=n.linspace(0.7,1.3,20),xmin=0.8,xmax=1.2,ymin=0,ymax=2,ylabel="events",xlabel="muon velocity (c)") 
        MuonicHistCanvas.__init__(self,parent,logger,n.linspace(0.,2,20),xmin=0.7,xmax=1.3,ymin=0,ymax=2,ylabel="events",xlabel="muon velocity (c)") 
        self.dimension = r"$c$"
        
class PulseWidthCanvas(MuonicHistCanvas):     

    def __init__(self,parent,logger,histcolor="r"): 
        #super(VelocityCanvas,self).__init__(self,parent,logger,binning=n.linspace(0.7,1.3,20),xmin=0.8,xmax=1.2,ymin=0,ymax=2,ylabel="events",xlabel="muon velocity (c)") 
        MuonicHistCanvas.__init__(self,parent,logger,n.linspace(0.,100,50),histcolor=histcolor,xmin=0.,xmax=100,ymin=0,ymax=2,ylabel="events",xlabel="pulsewidth (ns)") 
        self.ax.set_title("Pulsewidths")
        
    def update_plot(self,data):
        super(PulseWidthCanvas,self).update_plot(data)
        self.ax.set_title("Pulsewidths")
        
        
