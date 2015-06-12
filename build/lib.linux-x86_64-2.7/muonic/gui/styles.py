# common axis labels

import matplotlib
import pylab as p
import numpy as n
onesize = 32


fluxunits = r"GeVcm$^{-2}$s$^{-1}$sr$^{-1}$"
fluxunits_meter = r"GeVm$^{-2}$s$^{-1}$sr$^{-1}$"
logenergy = r"$\log_{10}(E/$GeV$)$"

##############################################

def EnergyMult(mult,energies,values):
   return values*((10**energies)**(mult -1))

##############################################

def EnergyMultLog(mult,energies,values):
    (10**energies*n.log(10))*(values*((10**energies)**(mult -1)))

##############################################
 
def RCSettings(): 
    """ 
    Set some global matplotlib RC settings 
    """ 
    from pylab import rc
    rc("lines",linewidth=2,markersize=10)
    rc("axes",titlesize=onesize,labelsize=onesize)
    rc("grid",linewidth=1.0)
    rc("xtick",labelsize=onesize)
    rc("xtick.major",size=7)
    rc("xtick.minor",size=5)
    rc("ytick",labelsize=onesize)
    rc("ytick.major",size=7)
    rc("ytick.minor",size=5)
    rc("grid",linewidth=1.2)
    #rc("font",serif="Palatino")
    fontprops = dict()
    fontprops["size"] = onesize
    fontprops["family"] = "TeX Gyre Pagella" # this is Palatino

    rc("font",**fontprops)
    rc("legend",fontsize=onesize,markerscale=1,numpoints=1)

    rc("ps" ,useafm = True)
    rc("pdf" , use14corefonts = True)
    rc("text",usetex=True) 
    rc("xtick",labelsize=onesize)
    rc("ytick",labelsize=onesize)
    rc("font",size =  onesize)
 
######################################################## 
 
def Thesisize(plot,log=False,leftxtickinvisible=True,logbase=100,ytoplabelinvisible=False,ybotlabelinvisible=False):
    """
    Adjust some parameters of the axis
    for thesis plots
    """

    #plot.grid()
    plot.tick_params(axis='both', which='major', labelsize=onesize)
    plot.tick_params(axis='both', which='minor', labelsize=onesize)
    #yticks = plot.yaxis.get_major_ticks()
    #p.setp(plot.get_xticklabels()[-1], visible=False)
    if log:
        yloc = matplotlib.ticker.LogLocator(base=logbase)
        plot.yaxis.set_major_locator(yloc)
    #yticks[0] .label1.set_visible(False)
    #yticks[-1].label1.set_visible(False)
    #xticks = plot.xaxis.get_major_ticks()
    #xticks[0] .label1.set_visible(False)
    #xticks[-1].label1.set_visible(False)
    #if leftxtickinvisible:
    plot.set_xticklabels(plot.get_xticks(), **fontprops)
    plot.set_yticklabels(plot.get_yticks(), **fontprops)
    #for label in plot.get_xticklabels() :
    #    label.set_fontproperties(**fontprops)
    try:
        p.setp(plot.get_xticklabels()[0], visible=leftxtickinvisible)
        p.setp(plot.get_yticklabels()[-1], visible=ytoplabelinvisible)
        p.setp(plot.get_yticklabels()[0], visible=ybotlabelinvisible)
    except Exception as e:
        print (e)
        print ("Can not get ticklabels, there might not be any, so this is propably fine")
    return plot



 
############################################## 
 
def RCPresentationSettings():
    """
    Set the rc object to optimized settings
    for a presentation
    """

    from pylab import rc

    #rc("figure",dpi=600)
    #rc("savefig",dpi=600)
    return None

