#! /usr/bin/env python

"""
Script for performing a fit to a histogramm of recorded 
time differences for the use with QNet
"""


import scipy.optimize as optimize
import numpy
import pylab
import sys
import optimalbins
import datetime
import os
import shutil
import time
from subprocess import Popen


def main(bincontent=None):

    def decay(p,x):
        return (p[0]/(numpy.sqrt(6.28)*p[1])*numpy.exp(-0.5*pow((x-p[1])/p[2],2)))
    def error(p,x,y):
        return decay(p,x)-y
    
    if bincontent == None:
    
        xmin = 1.0
        xmax = 5.0 
        nbins = float(sys.argv[2])
        times = [float(l) for l in open(sys.argv[1]).readlines() if 0 < float(l)]
        
        print len(times),"decay times"
        print "Nbins:",nbins
        date = time.gmtime()
        bin_edges = numpy.linspace(xmin,xmax,nbins)
        bin_centers = bin_edges[:-1] + 0.5*(bin_edges[1]-bin_edges[0])
        hist,edges = numpy.histogram(times,bin_edges)
        p0 = numpy.array([200.0,2.0,5.0])
        
        output = optimize.leastsq(error,p0,args=(bin_centers,hist),full_output=1)
        p = output[0]
        covar = output[1]
        
        print "Fit parameters:",p
        print "Covariance matrix:",covar
        
        chisquare=0.
        deviations=error(p,bin_centers,hist)
        for i,d in enumerate(deviations):
            chisquare += d*d/decay(p,bin_centers[i])
        
        params = {'legend.fontsize': 10}
        params = {'legend.textsize': 4}
        pylab.rcParams.update(params)
        
        fitx=numpy.linspace(xmin,xmax,100)
        pylab.plot(bin_centers,hist,"b^",fitx,decay(p,fitx),"b-")
        pylab.xlim(1.0,5.0)
        #pylab.ylim(0,max(hist)+2000)
        #pylab.ylim(0,max(hist)+60)
        pylab.xlabel("Velocity [$10^8$ m/s]")
        pylab.ylabel("Events")
        pylab.legend(("Data","Velocity: (%4.2f $\pm$ %4.2f) $10^8$ m/s ,   $\chi^2$/ndf=%4.2f"%(p[1],numpy.sqrt(covar[1][1]),chisquare/(nbins-len(p)))))
        #pylab.errorbar()
        pylab.grid()

        # this is hard-coded! There must be a better solution...
        # if you change here, you have to change in setup.py!
        datapath = os.getenv('HOME') + os.sep + 'muonic_data'


        date = datetime.datetime.now()
        pylab.savefig(os.path.join(datapath,"muon_velocity_%s.png" %(%date.strftime('%Y-%m-%d_%H-%M-%S'))))
        pylab.savefig(os.path.join(datapath,"muon_velocity_%s.pdf" %(%date.strftime('%Y-%m-%d_%H-%M-%S'))))
        p=Popen("eog " + os.path.join(datapath,"muon_velocity%s.png" %(%date.strftime('%Y-%m-%d_%H-%M-%S'))), shell=True) 

   
    else:

    
        bins = numpy.linspace(0,20,84)
        bin_centers = bins[:-1] + 0.5*(bins[1]-bins[0])

        p0 = numpy.array([200.0,2.0,5.0])
        #p0 = numpy.array([3.0,0.0,100.0])

        #try: 
        print bincontent

        output = optimize.leastsq(error,p0,args=(bin_centers,bincontent),full_output=1)
        #except:
        #    print "Fit failed!"
        #    return

        p = output[0]
        covar = output[1]
        
        print "Fit parameters:",p
        print "Covariance matrix:",covar
        
        chisquare=0.
        deviations=error(p,bin_centers,bincontent)
        for i,d in enumerate(deviations):
            chisquare += d*d/decay(p,bin_centers[i])
        
        params = {'legend.fontsize': 13}
        pylab.rcParams.update(params)
        
        nbins = 84
        xmin = bin_centers[0]
        xmax = bin_centers[-1]

        fitx=numpy.linspace(xmin,xmax,100)

        return (bin_centers,bincontent,fitx,decay,p,covar,chisquare,nbins)
        
   

if __name__ == '__main__':
    main()
