"""
Provide the different physics widgets
"""


# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

#muonic imports
from LineEdit import LineEdit
from MuonicPlotCanvases import ScalarsCanvas,LifetimeCanvas,PulseCanvas
from MuonicDialogs import DecayConfigDialog,PeriodicCallDialog, VelocityConfigDialog
from ..analysis.fit import main as fit

from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time

tr = QtCore.QCoreApplication.translate

def createPulseanalyzerWidget(logger): # not used yet
    """
    Provide a widget which is able to show a plot of triggered pulses
    """        
    widget = QtGui.QWidget()
    activatePulseanalyzer = QtGui.QCheckBox(widget)
    activatePulseanalyzer.setText(tr("Dialog", "Show the last triggered pulses \n in the time interval", None, QtGui.QApplication.UnicodeUTF8))
    activatePulseanalyzer.setObjectName("activate_pulseanalyzer")
    p3_vertical = QtGui.QVBoxLayout(widget)
    pulsecanvas = PulseCanvas(widget,logger)
    pulsecanvas.setObjectName("pulse_canvas")
    ntb2 = NavigationToolbar(pulsecanvas, widget)
    p3_vertical.addWidget(activatePulseanalyzer)
    p3_vertical.addWidget(pulsecanvas)
    p3_vertical.addWidget(ntb2)         
    return widget

def createVelocityWidget(logger):

    def activateVelocityClicked():
        """
        Perform extra actions when the checkbox is clicked
        """
        upper_channel = 0
        lower_channel = 1
        config_dialog = VelocityConfigDialog()
        rv = config_dialog.exec_()
        if rv == 1:
            for chan,ch_label in enumerate(["0","1","2","3"]):
                if config_dialog.findChild(QtGui.QRadioButton,QtCore.QString("uppercheckbox_" + ch_label )).isChecked():
                    upper_channel = chan
                    
            for chan,ch_label in enumerate(["0","1","2","3"]):
                if config_dialog.findChild(QtGui.QRadioButton,QtCore.QString("lowercheckbox_" + ch_label )).isChecked():
                    lower_channel = chan
                    
        widget.upper_channel = upper_channel
        widget.lower_channel = lower_channel   
            
        #return upper_channel,lower_channel
                                        
                    
        #now = datetime.datetime.now()
        #if not self.mainwindow.options.mudecaymode:
        #    if self.activateMuondecay.isChecked():
        #
        #        # launch the settings window
        #        config_window = DecayConfigDialog()
        #        rv = config_window.exec_()
        #        if rv == 1:
        #
        #            chan0_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_0")).isChecked()
        #            chan1_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_1")).isChecked()
        #            chan2_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_2")).isChecked()
        #            chan3_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_3")).isChecked()
        #            chan0_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_0")).isChecked()
        #            chan1_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_1")).isChecked()
        #            chan2_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_2")).isChecked()
        #            chan3_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_3")).isChecked()
        #            chan0_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_0")).isChecked()
        #            chan1_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_1")).isChecked()
        #            chan2_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_2")).isChecked()
        #            chan3_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_3")).isChecked()
        #            self.mainwindow.options.decay_selfveto  = config_window.selfveto.isChecked()
        #            self.mainwindow.options.decay_mintime   = int(config_window.mintime.text())
        #            
        #            for channel in enumerate([chan0_single,chan1_single,chan2_single,chan3_single]):
        #                if channel[1]:
        #                    self.mainwindow.options.singlepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset
        #        # FIXME! 
        #            for channel in enumerate([chan0_double,chan1_double,chan2_double,chan3_double]):
        #                if channel[1]:
        #                    self.mainwindow.options.doublepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset
        #
        #            for channel in enumerate([chan0_veto,chan1_veto,chan2_veto,chan3_veto]):
        #                if channel[1]:
        #                    self.mainwindow.options.vetopulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset
        #
        #        self.logger.warn("We now activate the Muondecay mode!\n All other Coincidence/Veto settings will be overriden!")
        #
        #        self.logger.warning("Changing gate width and enabeling pulses") 
        #        self.logger.info("Looking for single pulse in Channel %i" %(self.mainwindow.options.singlepulsechannel - 1))
        #        self.logger.info("Looking for double pulse in Channel %i" %(self.mainwindow.options.doublepulsechannel - 1 ))
        #        self.logger.info("Using veto pulses in Channel %i" %(self.mainwindow.options.vetopulsechannel - 1 ))
        #
        #        self.mainwindow.outqueue.put("CE") 
        #        self.mainwindow.outqueue.put("WC 03 04")
        #                         
        #        self.mainwindow.options.mudecaymode = True
        #        self.mu_label = QtGui.QLabel(tr('MainWindow','We are looking for decaying muons!'))
        #        self.mainwindow.statusbar.addWidget(self.mu_label)
        #        self.logger.warning('Might possibly overwrite textfile with decays')
        #        self.mainwindow.mu_file = open(self.mainwindow.options.decayfilename,'w')        
        #        self.mainwindow.options.dec_mes_start = now
        #
        #else:
        #
        #    self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
        #    self.mainwindow.statusbar.removeWidget(self.mu_label)
        #    self.mainwindow.options.mudecaymode = False
        #    mtime = now - self.mainwindow.options.dec_mes_start
        #    mtime = round(mtime.seconds/(3600.),2) + mtime.days *86400
        #    self.logger.info("The muon decay measurement was active for %f hours" % mtime)
        #    newmufilename = self.mainwindow.options.decayfilename.replace("HOURS",str(mtime))
        #    shutil.move(self.mainwindow.options.decayfilename,newmufilename)

    widget = QtGui.QWidget()
    activateVelocity = QtGui.QCheckBox(widget)
    activateVelocity.setText(tr("Dialog", "Measure muon velocity", None, QtGui.QApplication.UnicodeUTF8))
    activateVelocity.setObjectName("activate_velocity")


    layout = QtGui.QVBoxLayout(widget)
    #pulsecanvas = PulseCanvas(widget,logger)
    #pulsecanvas.setObjectName("pulse_canvas")
    #ntb2 = NavigationToolbar(pulsecanvas, widget)
    layout.addWidget(activateVelocity)
    #p3_vertical.addWidget(pulsecanvas)
    #p3_vertical.addWidget(ntb2)         
    QtCore.QObject.connect(activateVelocity,
                           QtCore.SIGNAL("clicked()"),
                           activateVelocityClicked
                           )
    return widget
