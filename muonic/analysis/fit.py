"""
Script for performing a fit to a histogramm of recorded 
time differences for the use with QNet
"""


import scipy.optimize as optimize
import numpy
import pylab
import sys
#import optimalbins

def main(bincontent=None,binning = (0,10,21), fitrange = None):

    def decay(p,x):
        return p[0]*numpy.exp(-x/p[1])+p[2]
    
    def error(p,x,y):
        return decay(p,x)-y
    
    if bincontent is None:
    
        nbins = 10
        xmin = 1.0
        xmax = 20.0
    

        times = [float(l) for l in open(sys.argv[1]).readlines() if xmin<float(l)<xmax]
        print len(times),"decay times"

	    #nbins = optimalbins.optbinsize(times,1,80)    
	    #print nbins, 'Optimalbins selects nbins'    
       

        #nbins = optimalbins.optbinsize(times,1,30)
        print "Nbins:",nbins
        
        bin_edges = numpy.linspace(binning[0],binning[1],binning[2])
        bin_centers = bin_edges[:-1] + 0.5*(bin_edges[1]-bin_edges[0])
        
        hist,edges = numpy.histogram(times,bin_edges)
        
        #hist=hist[:-1]
        p0 = numpy.array([200,2.0,5])
        
        output = optimize.leastsq(error,p0,args=(bin_centers,hist),full_output=1)
        p = output[0]
        covar = output[1]
        
        print "Fit parameters:",p
        print "Covariance matrix:",covar
        
        chisquare=0.
        deviations=error(p,bin_centers,hist)
        for i,d in enumerate(deviations):
            chisquare += d*d/decay(p,bin_centers[i])
        
        params = {'legend.fontsize': 13}
        pylab.rcParams.update(params)
        
        fitx=numpy.linspace(xmin,xmax,100)
        pylab.plot(bin_centers,hist,"b^",fitx,decay(p,fitx),"b-")
        pylab.ylim(0,max(hist)+100)
        pylab.xlabel("Decay time in microseconds")
        pylab.ylabel("Events in time bin")
        # pylab.legend(("Data","Fit: (%4.2f +- %4.2f) microsec,chisq/ndf=%4.2f"%(p[1],numpy.sqrt(covar[1][1]),chisquare/(nbins-len(p)))))
        pylab.legend(("Data","Fit: (%4.2f) microsec,chisq/ndf=%4.2f"%(p[1]),chisquare/(nbins-len(p))))

	pylab.grid()
        pylab.savefig("fit.png")
        
    else:

        # this is then used for the mudecaywindow
        # in muonic
        # we have to adjust the bins
        # to the values of the used histogram
        if len(bincontent) == 0:
            print 'WARNING: Empty bins.'
            return None
    
        bins = numpy.linspace(binning[0],binning[1],binning[2])
        bin_centers = bins[:-1] + 0.5*(bins[1]-bins[0])
        if fitrange is not None:
            if fitrange[0] < binning[0]:
                fitrange = (binning[0], fitrange[1])
            if fitrange[1] > binning[1]:
                fitrange = (fitrange[0],binning[1])
            bin_mask = [(bin_centers <= fitrange[1]) & (bin_centers >= fitrange[0])]
            bin_centers_ = numpy.asarray([x for x in bin_centers if (x <= fitrange[1] and x >= fitrange[0])])
            if len(bin_centers_) < 3:
                print 'WARNING: fit range too small. Skipping fitting. Try with larger fit range.'
                return None
            else:
                bin_centers = bin_centers_
                bincontent = bincontent[bin_mask]

        # we cut the leading edge of the distribution away for the fit 
        glob_max = max(bincontent)
        cut = 0
        for i in enumerate(bincontent):
            if i[1] == glob_max:
                cut = i[0]

        cut_bincontent  = bincontent[cut:]        
        cut_bincenter   = bin_centers[cut]
        cut_bincenters  = bin_centers[cut:]


        # maybe something for the future..
        #nbins = optimalbins.optbinsize(cut_bincontent,1,20)       
        #fit_bins        = n.linspace(cut_bincenter,20,nbins)
        #fit_bin_centers = fit_bins[:-1] + 0.5*(fit_bins[1]-fit_bins[0])
        #fit_bincontent  = n.zeros(len(fit_bin_centers))

        ## the bincontent must be redistributed to fit_bincontent

        #for binindex_fit in xrange(len(fit_bincontent)):
        #    for binindex,content in enumerate(bincontent):
        #        if bin_centers[binindex] <= fit_bin_centers[binindex_fit]:
        #            fit_bincontent[binindex_fit] += content

        p0 = numpy.array([200,2.0,5])

        #output = optimize.leastsq(error,p0,args=(fit_bin_centers,fitbincontent),full_output=1)

        output = optimize.leastsq(error,p0,args=(cut_bincenters,cut_bincontent),full_output=1)

        p = output[0]
        covar = output[1]
        
        print "Fit parameters:",p
        print "Covariance matrix:",covar
        
        chisquare=0.
        deviations=error(p,cut_bincenters,cut_bincontent)
        for i,d in enumerate(deviations):
            chisquare += d*d/decay(p,cut_bincenters[i])
        
        params = {'legend.fontsize': 13}
        pylab.rcParams.update(params)
        
        #nbins = 84
        nbins = len(bins)
        xmin = cut_bincenters[0]
        xmax = cut_bincenters[-1]

        fitx=numpy.linspace(xmin,xmax,100)

        #return (bin_centers,bincontent,fitx,decay,p,covar,chisquare,nbins)
        return (cut_bincenters,cut_bincontent,fitx,decay,p,covar,chisquare,nbins)
     

def gaussian_fit(bincontent,binning = (0,2,10), fitrange = None):

    def gauss(p,x):
        return (1/((p[0]*numpy.sqrt(2*numpy.pi))))*numpy.exp(-0.5*(((x - p[1])/p[0])**2)) 
    
    def error(p,x,y):
        return gauss(p,x)-y
    
    if len(bincontent) == 0:
        print 'WARNING: Empty bins.'
        return None
    
    # this is then used for the mudecaywindow
    # in muonic
    # we have to adjust the bins
    # to the values of the used histogram

    bins = numpy.linspace(binning[0],binning[1],binning[2])
    bin_centers = bins[:-1] + 0.5*(bins[1]-bins[0])

    if fitrange is not None:
        if fitrange[0] < binning[0]:
            fitrange = (binning[0], fitrange[1])
        if fitrange[1] > binning[1]:
            fitrange = (fitrange[0],binning[1])
        bin_mask = [(bin_centers <= fitrange[1]) & (bin_centers >= fitrange[0])]
        bin_centers_ = numpy.asarray([x for x in bin_centers if (x <= fitrange[1] and x >= fitrange[0])])
        if len(bin_centers_) < 3:
            print 'WARNING: fit range too small. Skipping fitting. Try with larger fit range.'
            return None
        else:
            bin_centers = bin_centers_
            bincontent = bincontent[bin_mask]


    # we cut the leading edge of the distribution away for the fit
    #glob_max = max(bincontent)
    #cut = 0
    #for i in enumerate(bincontent):
    #    if i[1] == glob_max:
    #        cut = i[0]


    cut_bincontent  = bincontent#[cut:]        
    cut_bincenter   = bin_centers#[cut]
    cut_bincenters  = bin_centers#[cut:]


    # maybe something for the future..
    #nbins = optimalbins.optbinsize(cut_bincontent,1,20)       
    #fit_bins        = n.linspace(cut_bincenter,20,nbins)
    #fit_bin_centers = fit_bins[:-1] + 0.5*(fit_bins[1]-fit_bins[0])
    #fit_bincontent  = n.zeros(len(fit_bin_centers))

    ## the bincontent must be redistributed to fit_bincontent

    #for binindex_fit in xrange(len(fit_bincontent)):
    #    for binindex,content in enumerate(bincontent):
    #        if bin_centers[binindex] <= fit_bin_centers[binindex_fit]:
    #            fit_bincontent[binindex_fit] += content

    p0 = numpy.array([20,1.0,5])

    #output = optimize.leastsq(error,p0,args=(fit_bin_centers,fitbincontent),full_output=1)
    output = optimize.leastsq(error,p0,args=(cut_bincenters,cut_bincontent),full_output=1)

    p = output[0]
    covar = output[1]
    
    print "Fit parameters:",p
    print "Covariance matrix:",covar
    
    chisquare=0.
    deviations=error(p,cut_bincenters,cut_bincontent)
    for i,d in enumerate(deviations):
        chisquare += d*d/gauss(p,cut_bincenters[i])
    
    params = {'legend.fontsize': 13}
    pylab.rcParams.update(params)
    
    #nbins = 84
    nbins = len(bins)
    xmin = cut_bincenters[0]
    xmax = cut_bincenters[-1]

    fitx=numpy.linspace(xmin,xmax,100)

    #return (bin_centers,bincontent,fitx,decay,p,covar,chisquare,nbins)
    return (cut_bincenters,cut_bincontent,fitx,gauss,p,covar,chisquare,nbins)
     

if __name__ == '__main__':
    main()
