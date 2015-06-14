onesize = 32

def LargeScreenMPStyle(): 
    """ 
    Large fonts for large screens
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
