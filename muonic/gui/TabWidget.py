"""
Manage the different (physics) widgets
"""

# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

from LineEdit import LineEdit
from PeriodicCallDialog import PeriodicCallDialog

from ScalarsCanvas import ScalarsCanvas
from LifetimeCanvas import LifetimeCanvas
from PulseCanvas import PulseCanvas
from DecayConfigDialog import DecayConfigDialog


from muonic.analysis import fit

import muonic.analysis.PulseAnalyzer as pa

from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time





tr = QtCore.QCoreApplication.translate

class TabWidget(QtGui.QWidget):
    """
    The TabWidget will provide a tabbed interface.
    All functionality should be represented by tabs in the TabWidget
    """

    def __init__(self, mainwindow, timewindow, logger):

        QtGui.QWidget.__init__(self)
        
        self.mainwindow = mainwindow
        self.logger = logger
        self.logger.info("Timewindow is %4.2f" %timewindow)
        self.setGeometry(0,0, self.mainwindow.reso_w,self.mainwindow.reso_h)
        self.setWindowTitle("Debreate")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.resize(self.mainwindow.reso_w,self.mainwindow.reso_h)
        self.setMinimumSize(self.mainwindow.reso_w,self.mainwindow.reso_h)
        self.center()
        self.write_file       = False
        self.holdplot         = False
        self.scalars_result   = False 
        self.muondecaycounter = 0
        self.lastdecaytime    = 'None'

        # provide the items which should go into the tabs
        self.label = QtGui.QLabel(tr('MainWindow','Command'))
        self.hello_edit = LineEdit()
        self.hello_button = QtGui.QPushButton(tr('MainWindow','Send'))
        self.file_button = QtGui.QPushButton(tr('MainWindow', 'Save to File'))
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

        #create the several tabs 
        tab_widget = QtGui.QTabWidget()
        tab1 = QtGui.QWidget()
        tab2 = QtGui.QWidget()
        tab3 = QtGui.QWidget()
        tab4 = QtGui.QWidget()

        p1_vertical = QtGui.QVBoxLayout(tab1)
        p2_vertical = QtGui.QVBoxLayout(tab2)
        p3_vertical = QtGui.QVBoxLayout(tab3)
        p4_vertical = QtGui.QVBoxLayout(tab4)

        tab_widget.addTab(tab1, "Muon Rates")
        tab_widget.addTab(tab2, "Muon Lifetime")
        tab_widget.addTab(tab3, "PulseAnalyzer")
        tab_widget.addTab(tab4, "DAQ output")
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tab_widget)
        
        self.setLayout(vbox)
       
        self.scalars_monitor  = ScalarsCanvas(self, self.logger)
        self.lifetime_monitor = LifetimeCanvas(self,self.logger)
        self.pulse_monitor    = PulseCanvas(self,self.logger)

        # buttons for restart/clear the plot     
        self.start_button = QtGui.QPushButton(tr('MainWindow', 'Restart'))
        self.stop_button = QtGui.QPushButton(tr('MainWindow', 'Stop'))

        # button for performing a mu lifetime fit
        self.mufit_button = QtGui.QPushButton(tr('MainWindow', 'Fit!'))
        
        QtCore.QObject.connect(self.mufit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.mufitClicked
                              )

        QtCore.QObject.connect(self.start_button,
                              QtCore.SIGNAL("clicked()"),
                              self.startClicked
                              )

        QtCore.QObject.connect(self.stop_button,
                              QtCore.SIGNAL("clicked()"),
                              self.stopClicked
                              )

        # pack theses widget into the vertical box
        p1_vertical.addWidget(self.scalars_monitor)

        # instantiate the navigation toolbar
        p1_h_box = QtGui.QHBoxLayout()
        ntb = NavigationToolbar(self.scalars_monitor, self)
        p1_h_box.addWidget(ntb)
        p1_h_box.addWidget(self.start_button)
        p1_h_box.addWidget(self.stop_button)
        p1_second_widget = QtGui.QWidget()
        p1_second_widget.setLayout(p1_h_box)
        p1_vertical.addWidget(p1_second_widget)

        ntb1 = NavigationToolbar(self.lifetime_monitor, self)

        # mudecay tab..
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
 
        p2_vertical.addWidget(self.activateMuondecay)
        p2_vertical.addWidget(self.displayMuons)
        p2_vertical.addWidget(self.lastDecay)
        p2_vertical.addWidget(self.lifetime_monitor)

        p2_h_box = QtGui.QHBoxLayout()
        p2_h_box.addWidget(ntb1)
        p2_h_box.addWidget(self.mufit_button)
        p2_second_widget = QtGui.QWidget()
        p2_second_widget.setLayout(p2_h_box)
        p2_vertical.addWidget(p2_second_widget)

        ntb2 = NavigationToolbar(self.pulse_monitor, self)

        # the pulseanalyzer tab
        self.activatePulseanalyzer = QtGui.QCheckBox(self)
        self.activatePulseanalyzer.setText(tr("Dialog", "Show the last triggered pulses \n in the time interval", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activatePulseanalyzer,
                              QtCore.SIGNAL("clicked()"),
                              self.activatePulseanalyzerClicked
                              )
        p3_vertical.addWidget(self.activatePulseanalyzer)
        p3_vertical.addWidget(self.pulse_monitor)
        p3_vertical.addWidget(ntb2)

        # define the begin of the timeintervall 
        # for the rate calculation
        now = time.time()
        self.mainwindow.lastscalarquery = now
        # start a timer which does something every timewindow seconds
        self.timerEvent(None)
        self.timer = self.startTimer(timewindow*1000)

        p4_vertical.addWidget(self.text_box)
        daq_widget = QtGui.QWidget()
        h_box = QtGui.QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addWidget(self.hello_edit)
        h_box.addWidget(self.hello_button)
        h_box.addWidget(self.file_button)
        h_box.addWidget(self.periodic_button)
        daq_widget.setLayout(h_box)
        p4_vertical.addWidget(daq_widget)
        
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
        fitresults = fit.main(bincontent=n.asarray(self.lifetime_monitor.heights))
        self.lifetime_monitor.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])

    def activateMuondecayClicked(self):
        """
        What should be done if we are looking for mu-decays?
        """
 
        now = datetime.datetime.now()
        if not self.mainwindow.options.mudecaymode:
            if self.activateMuondecay.isChecked():

                # launch the settings window
                config_window = DecayConfigDialog()
                rv = config_window.exec_()
                if rv == 1:

                    chan0_single = config_window.singleChan0.isChecked()
                    chan1_single = config_window.singleChan1.isChecked()
                    chan2_single = config_window.singleChan2.isChecked()
                    chan3_single = config_window.singleChan3.isChecked()
                    chan0_double = config_window.doubleChan0.isChecked()
                    chan1_double = config_window.doubleChan1.isChecked()
                    chan2_double = config_window.doubleChan2.isChecked()
                    chan3_double = config_window.doubleChan3.isChecked()
                    chan0_veto   = config_window.vetoChan0.isChecked()
                    chan1_veto   = config_window.vetoChan1.isChecked()
                    chan2_veto   = config_window.vetoChan2.isChecked()
                    chan3_veto   = config_window.vetoChan3.isChecked()

                    for channel in enumerate([chan0_single,chan1_single,chan2_single,chan3_single]):
                        if channel[1]:
                            self.mainwindow.options.singlepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset
                # FIXME! 
                    for channel in enumerate([chan0_double,chan1_double,chan2_double,chan3_double]):
                        if channel[1]:
                            self.mainwindow.options.doublepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset

                    for channel in enumerate([chan0_veto,chan1_veto,chan2_veto,chan3_veto]):
                        if channel[1]:
                            self.mainwindow.options.vetopulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset


                self.logger.warn("We now activate the Muondecay mode!\n All other Coincidence/Veto settings will be overriden!")

                self.logger.warning("Changing gate width and enabeling pulses") 
                self.mainwindow.outqueue.put("CE") 
                self.mainwindow.outqueue.put("WC 03 04")
                                 
                self.mainwindow.options.mudecaymode = True
                self.mu_label = QtGui.QLabel(tr('MainWindow','We are looking for decaying muons!'))
                self.mainwindow.statusbar.addWidget(self.mu_label)
                self.logger.warning('Might possibly overwrite textfile with decays')
                self.mainwindow.mu_file = open(self.mainwindow.options.decayfilename,'w')		
                self.mainwindow.options.dec_mes_start = now

        else:

            self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
            self.mainwindow.statusbar.removeWidget(self.mu_label)
            self.mainwindow.options.mudecaymode = False
            mtime = now - self.mainwindow.options.dec_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days *86400
            self.logger.info("The muon decay measurement was active for %f hours" % mtime)
            newmufilename = self.mainwindow.options.decayfilename.replace("HOURS",str(mtime))
            shutil.move(self.mainwindow.options.decayfilename,newmufilename)
     
    def activatePulseanalyzerClicked(self):
        """
        set-up the pulseanalyzer widget
        """

        if self.activatePulseanalyzer.isChecked():
            self.mainwindow.options.showpulses = True
            self.logger.info("PulseAnalyzer active %s" %self.mainwindow.options.showpulses.__repr__())
        else:
            self.mainwindow.options.showpulses = False
            self.logger.info("PulseAnalyzer active %s" %self.mainwindow.options.showpulses.__repr__())


    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

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
        self.outputfile = open(self.mainwindow.options.rawfilename,"w")
        self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%self.mainwindow.options.rawfilename))
        self.write_file = True
        self.mainwindow.options.raw_mes_start = datetime.datetime.now()
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
            if not self.holdplot:
                self.scalars_monitor.update_plot(self.scalars_result)

        self.logger.debug("The differcene between two sent 'DS' commands is %4.2f seconds" %self.mainwindow.thisscalarquery)

        self.displayMuons.setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.lastDecay.setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))

        # the mu lifetime histogram 
        if self.mainwindow.options.mudecaymode:
        
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

        if self.mainwindow.options.showpulses:
            self.pulse_monitor.update_plot(self.mainwindow.pulses_to_show)

