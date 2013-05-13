"""
Manage the different (physics) widgets
"""

#FIXME make individual widgets and provide an easy api to add more..

# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

#muonic imports
from LineEdit import LineEdit
from MuonicPlotCanvases import ScalarsCanvas,LifetimeCanvas,PulseCanvas
from MuonicDialogs import DecayConfigDialog,PeriodicCallDialog
from MuonicWidgets import createPulseanalyzerWidget,createVelocityWidget
from ..analysis.fit import main as fit

from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time

tr = QtCore.QCoreApplication.translate


def calculate_rate(pulses,lastpulses):
    """
    Get the rates per channel from two lines of pulses 
    """

    # TODO: get rates for a previosly recorded file
    # allthough it would be nice to calculate
    # the rate from pulses
    # first one has to think of doing this event
    # or pulse-wise

    raise NotImplementedError


class TabWidget(QtGui.QTabWidget):
    """
    The TabWidget will provide a tabbed interface.
    All functionality should be represented by tabs in the TabWidget
    """

    def __init__(self, mainwindow, timewindow, logger):

        QtGui.QTabWidget.__init__(self)
        
        self.mainwindow = mainwindow
        self.logger = logger
        self.logger.info("Timewindow is %4.2f" %timewindow)
        self.scalars_monitor  = ScalarsCanvas(self, self.logger)
        self.lifetime_monitor = LifetimeCanvas(self,self.logger)
        self.minsinglepulsewidth = 0
        self.maxsinglepulsewidth = 100000 #inf
        self.mindoublepulsewidth = 0
        self.maxdoublepulsewidth = 100000 #inf

        #self.pulse_monitor    = PulseCanvas(self,self.logger)  

        #self.tab_widget = self.create_tabs(["Muon Rates","Muon Lifetime","DAQ Output"])
        for label in ["Muon Rates","Muon Lifetime"]:
            tab = QtGui.QWidget()
            self.addTab(tab,label)
        
        #vbox = QtGui.QVBoxLayout()
        #vbox.addWidget(self.tab_widget)
        #self.setLayout(vbox)   
        
        # Stuff moved from MuonicOptions:
        self.mudecaymode = False
        self.decay_selfveto = None
        self.decay_mintime = 0.
        self.singlepulsechannel = None
        self.doublepulsechannel = None
        self.vetopulsechannel = None

        ################
        # Rate widget
        ################

        self.holdplot         = False
        self.scalars_result   = False 

        # buttons for restart/clear the plot rate plot   
        self.start_button = QtGui.QPushButton(tr('MainWindow', 'Restart'))
        self.stop_button  = QtGui.QPushButton(tr('MainWindow', 'Stop'))

        QtCore.QObject.connect(self.start_button,
                              QtCore.SIGNAL("clicked()"),
                              self.startClicked
                              )

        QtCore.QObject.connect(self.stop_button,
                              QtCore.SIGNAL("clicked()"),
                              self.stopClicked
                              )

        rate_widget = QtGui.QGridLayout(self.widget(0))
        rate_widget.addWidget(self.scalars_monitor,0,0,1,3)
        ntb = NavigationToolbar(self.scalars_monitor, self)
        rate_widget.addWidget(ntb,1,0)
        rate_widget.addWidget(self.start_button,1,1)
        rate_widget.addWidget(self.stop_button,1,2)

        #################
        # Mudecay widget
        #################

        self.mufit_button = QtGui.QPushButton(tr('MainWindow', 'Fit!'))
        
        QtCore.QObject.connect(self.mufit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.mufitClicked
                              )

        self.muondecaycounter = 0
        self.lastdecaytime    = 'None'
        ntb1 = NavigationToolbar(self.lifetime_monitor, self)

        # activate Muondecay mode with a checkbox
        self.activateMuondecay = QtGui.QCheckBox(self)
        self.activateMuondecay.setText(tr("Dialog", "Check for decayed Muons \n- Warning! this will define your coincidence/Veto settings!", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateMuondecay,
                              QtCore.SIGNAL("clicked()"),
                              self.activateMuondecayClicked
                              )
        self.displayMuons = QtGui.QLabel(self)
        self.lastDecay = QtGui.QLabel(self)
        self.displayMuons.setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.lastDecay.setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
 
        decay_tab = QtGui.QGridLayout(self.widget(1))
        decay_tab.addWidget(self.activateMuondecay,0,0)
        decay_tab.addWidget(self.displayMuons,1,0)
        decay_tab.addWidget(self.lastDecay,2,0)
        decay_tab.addWidget(self.lifetime_monitor,3,0,1,2)
        decay_tab.addWidget(ntb1,4,0)
        decay_tab.addWidget(self.mufit_button,4,1)
        
        self.decaywidget = self.widget(1)
        ########################
        # Pulseanalyzer widget
        ##########################

        # TODO: Encapsule the widgets, so that they can
        # easily included
        # all widget specific properties should go to that widget
        

        
        self.addTab(createPulseanalyzerWidget(logger),"Pulse Analyzer")
        #################
        # DAQ widget
        #################  
        def createDAQWidget():
            tab = QtGui.QWidget()
            self.write_file       = False
            self.label           = QtGui.QLabel(tr('MainWindow','Command'))
            self.hello_edit      = LineEdit()
            self.hello_button    = QtGui.QPushButton(tr('MainWindow','Send'))
            self.file_button     = QtGui.QPushButton(tr('MainWindow', 'Save to File'))
            self.periodic_button = QtGui.QPushButton(tr('MainWindow', 'Periodic Call'))
            QtCore.QObject.connect(self.hello_button,
                                  QtCore.SIGNAL("clicked()"),
                                  self.on_hello_clicked
                                  )
            QtCore.QObject.connect(self.hello_edit,
                                  QtCore.SIGNAL("returnPressed()"),
                                  self.on_hello_clicked
                                  )
            
            QtCore.QObject.connect(self.file_button,
                                    QtCore.SIGNAL("clicked()"),
                                    self.on_file_clicked
                                    )
            QtCore.QObject.connect(self.periodic_button,
                                    QtCore.SIGNAL("clicked()"),
                                    self.on_periodic_clicked
                                    )
            
            self.text_box = QtGui.QPlainTextEdit()
            self.text_box.setReadOnly(True)
            # only 500 lines history
            self.text_box.document().setMaximumBlockCount(500)
            
            daq_layout = QtGui.QGridLayout(tab)
            daq_layout.addWidget(self.text_box,0,0,1, 4)
            daq_layout.addWidget(self.label,1,0)
            daq_layout.addWidget(self.hello_edit,1,1)
            daq_layout.addWidget(self.hello_button,1,2) 
            daq_layout.addWidget(self.file_button,1,2) 
            daq_layout.addWidget(self.periodic_button,1,3)   
            return tab
        
        self.addTab(createDAQWidget(),"DAQ Output")
        self.addTab(createVelocityWidget(logger),"Muon Velocity")
        # give this widget a more common name
        self.velocitywidget = self.widget(4)
        # define the begin of the timeintervall 
        # for the rate calculation
        now = time.time()
        self.mainwindow.lastscalarquery = now
        # start a timer which does something every timewindow seconds
        self.timerEvent(None)
        self.timer = self.startTimer(timewindow*1000)


        
    def startClicked(self):
        """
        restart the rate measurement
        """ 
        self.logger.debug("Restart Button Clicked")
        self.holdplot = False
        self.scalars_monitor.reset()
        
    def stopClicked(self):
        """
        hold the rate measurement plot till buttion is pushed again
        """
        self.holdplot = True

    def mufitClicked(self):
        """
        fit the muon decay histogram
        """
        fitresults = fit(bincontent=n.asarray(self.lifetime_monitor.heights))
        self.lifetime_monitor.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])


    def activateMuondecayClicked(self):
        """
        What should be done if we are looking for mu-decays?
        """
 
        now = datetime.datetime.now()
        if not self.mudecaymode:
            if self.activateMuondecay.isChecked():

                # launch the settings window
                config_window = DecayConfigDialog()
                rv = config_window.exec_()
                if rv == 1:

                    chan0_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_0")).isChecked()
                    chan1_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_1")).isChecked()
                    chan2_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_2")).isChecked()
                    chan3_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_3")).isChecked()
                    chan0_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_0")).isChecked()
                    chan1_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_1")).isChecked()
                    chan2_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_2")).isChecked()
                    chan3_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_3")).isChecked()
                    chan0_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_0")).isChecked()
                    chan1_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_1")).isChecked()
                    chan2_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_2")).isChecked()
                    chan3_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_3")).isChecked()
                    self.decay_selfveto  = config_window.selfveto.isChecked()
                    self.decay_mintime   = int(config_window.mintime.text())
                    if config_window.findChild(QtGui.QGroupBox,QtCore.QString("pulsewidthgroupbox")).isChecked():
                        self.minsinglepulsewidth = config_window.findChild(QtGui.QLineEdit,QtCore.QString("minsinglepulsewidth")).text()
                        self.maxsinglepulsewidth = config_window.findChild(QtGui.QLineEdit,QtCore.QString("maxsinglepulsewidth")).text()
                        self.mindoublepulsewidth = config_window.findChild(QtGui.QLineEdit,QtCore.QString("mindoublepulsewidth")).text()
                        self.maxdoublepulsewidth = config_window.findChild(QtGui.QLineEdit,QtCore.QString("maxdoublepulsewidth")).text()
                    
                    for channel in enumerate([chan0_single,chan1_single,chan2_single,chan3_single]):
                        if channel[1]:
                            self.singlepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset
                # FIXME! 
                    for channel in enumerate([chan0_double,chan1_double,chan2_double,chan3_double]):
                        if channel[1]:
                            self.doublepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset

                    for channel in enumerate([chan0_veto,chan1_veto,chan2_veto,chan3_veto]):
                        if channel[1]:
                            self.vetopulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset

                self.logger.warn("We now activate the Muondecay mode!\n All other Coincidence/Veto settings will be overriden!")

                self.logger.warning("Changing gate width and enabeling pulses") 
                self.logger.info("Looking for single pulse in Channel %i" %(self.singlepulsechannel - 1))
                self.logger.info("Looking for double pulse in Channel %i" %(self.doublepulsechannel - 1 ))
                self.logger.info("Using veto pulses in Channel %i" %(self.vetopulsechannel - 1 ))

                self.mainwindow.outqueue.put("CE") 
                self.mainwindow.outqueue.put("WC 03 04")
                                 
                self.mudecaymode = True
                self.mu_label = QtGui.QLabel(tr('MainWindow','We are looking for decaying muons!'))
                self.mainwindow.statusbar.addWidget(self.mu_label)
                self.logger.warning('Might possibly overwrite textfile with decays')
                self.mainwindow.mu_file = open(self.mainwindow.decayfilename,'w')		
                self.mainwindow.dec_mes_start = now

        else:

            self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
            self.mainwindow.statusbar.removeWidget(self.mu_label)
            self.mudecaymode = False
            mtime = now - self.dec_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days *86400
            self.logger.info("The muon decay measurement was active for %f hours" % mtime)
            newmufilename = self.decayfilename.replace("HOURS",str(mtime))
            shutil.move(self.decayfilename,newmufilename)
     


    #def center(self):
    #    screen = QtGui.QDesktopWidget().screenGeometry()
    #    size = self.geometry()
    #    self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def on_hello_clicked(self):

        """
        send a message to the daq
        """
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.mainwindow.outqueue.put(str(self.hello_edit.displayText()))
            self.hello_edit.add_hist_item(text)
        self.hello_edit.clear()

    def on_file_clicked(self):
        """
        save the raw daq data to a automatically named file
        """       
        self.outputfile = open(self.mainwindow.rawfilename,"w")
        self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%self.rawfilename))
        self.write_file = True
        self.mainwindow.raw_mes_start = datetime.datetime.now()
        self.mainwindow.statusbar.addPermanentWidget(self.file_label)

    def on_periodic_clicked(self):
        """
        issue a command periodically
        """

        periodic_window = PeriodicCallDialog()
        rv = periodic_window.exec_()
        if rv == 1:
            period = periodic_window.time_box.value() * 1000 #We need the period in milliseconds
            command = str(periodic_window.textbox.text())
            commands = command.split('+')
            def periodic_put():
                for c in commands:
                    self.mainwindow.outqueue.put(c)
            self.periodic_put = periodic_put
            self.periodic_call_timer = QtCore.QTimer()
            QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.periodic_put)
            self.periodic_put()
            self.periodic_call_timer.start(period)
            self.periodic_status_label = QtGui.QLabel(tr('MainWindow','%s every %s sec'%(command,period/1000)))
            self.mainwindow.statusbar.addPermanentWidget(self.periodic_status_label)
        else:
            try:
                self.periodic_call_timer.stop()
                self.mainwindow.statusbar.removeWidget(self.periodic_status_label)
            except AttributeError:
                pass

    def timerEvent(self,ev):
        """
        Update the widgets
        """
        # get the scalar information from the card
        self.mainwindow.outqueue.put('DS')

        # we have to know, when we sent the command
        now = time.time()
        self.mainwindow.thisscalarquery = now - self.mainwindow.lastscalarquery
        self.mainwindow.lastscalarquery = now
        # when initiaizing, the timewindow is large,
        # omitting this by requesting values below
        # an arbitrary of 10000
        if self.scalars_result and self.scalars_result[5] < 10000:
            if (not self.holdplot):
                self.scalars_monitor.update_plot(self.scalars_result)

        self.logger.debug("The differcene between two sent 'DS' commands is %4.2f seconds" %self.mainwindow.thisscalarquery)

        self.displayMuons.setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.lastDecay.setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))

        # the mu lifetime histogram 
        if self.mudecaymode:
        
            if self.mainwindow.decay:    

                self.logger.info("Adding decays %s" %self.mainwindow.decay)

                # at the moment we are only using the first decay

                decay_times =  [decay_time[0] for decay_time in self.mainwindow.decay]

                self.lifetime_monitor.update_plot(decay_times)

                # as different processes are in action,
                # hopefully this is sufficent!
                # (as the low decay rates expected, I think so:))

                muondecay = self.mainwindow.decay[0]
                self.mainwindow.mu_file.write('Decay ')
                muondecay_time = muondecay[1].replace(' ','_')
                self.mainwindow.mu_file.write(muondecay_time.__repr__() + ' ')
                self.mainwindow.mu_file.write(muondecay[0].__repr__())
                self.mainwindow.mu_file.write('\n')
                self.mainwindow.decay = []

        # putting this in here prohibits the pulseanalyzer to be activatet immediately (this is in principle bad=
        # but as it has to wait for pulses anyway, this does not matter
        if self.widget(2).findChild(QtGui.QCheckBox,QtCore.QString("activate_pulseanalyzer")).isChecked(): #self.activatePulseanalyzer.isChecked():
            self.widget(2).findChild(PulseCanvas,QtCore.QString("pulse_canvas")).update_plot(self.mainwindow.pulses_to_show)




