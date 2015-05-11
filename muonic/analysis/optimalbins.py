#implemented after http://arxiv.org/abs/physics/0605197

import numpy
import scipy.special

gammaln = scipy.special.gammaln

def optbinsize(data,minbins,maxbins):
    
    N = len(data)
    logp = [0]*(maxbins+1)

    for nbins in xrange(minbins,maxbins+1):
        hist,edges = numpy.histogram(data,bins=nbins)
        part1 = N*numpy.log(nbins) + gammaln(nbins/2.) - gammaln(N+nbins/2.)
        part2 = -nbins * gammaln(0.5) + numpy.sum(gammaln(hist+0.5))
        logp[nbins] = part1 + part2

    maximum = max(logp)
    optbins = logp.index(maximum)
    return optbins

# vim: ai ts=4 sts=4 et sw=4
