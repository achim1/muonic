"""
Provides the main window for the gui part of muonic
"""

from PyQt4 import QtGui
from PyQt4 import QtCore

import numpy as n

import datetime

import os
import shutil
import time


# muonic imports
from ..analysis import PulseAnalyzer as pa
from ..daq.DAQProvider import DAQIOError

from MuonicSettings import MuonicConstants, MuonicSettings
from MuonicDialogs import ConfigDialog,HelpDialog,DecayConfigDialog,PeriodicCallDialog,AdvancedDialog
from MuonicMenus import MuonicMenus
from MuonicPlotCanvases import ScalarsCanvas,LifetimeCanvas,PulseCanvas
from MuonicWidgets import VelocityWidget,PulseanalyzerWidget,DecayWidget,DAQWidget,RateWidget, GPSWidget, StatusWidget

tr = QtCore.QCoreApplication.translate

class MainWindow(QtGui.QMainWindow):
    """
    The main application
    """
    def __init__(self, daq, logger, opts,  win_parent = None):

        QtGui.QMainWindow.__init__(self, win_parent)
        self.daq = daq
        self.logger  = logger
        self.settings = MuonicSettings(self.logger)
        self.constants = MuonicConstants()

        # we have to ensure that the DAQcard does not sent
        # any automatic status reports every x seconds
        self.daq.put('ST 0')

        self.setWindowTitle(QtCore.QString("muonic"))
        self.statusbar = QtGui.QMainWindow.statusBar(self)
        self.muonic_menus = MuonicMenus(parent=self)

        # we chose a global format for naming the files -> decided on 18/01/2012
        # we use GMT times
        # " Zur einheitlichen Datenbezeichnung schlage ich folgendes Format vor:
        # JJJJ-MM-TT_y_x_vn.dateiformat (JJJJ-Jahr; MM-Monat; TT-Speichertag bzw.
        # Beendigung der Messung; y: G oder L ausw?hlen, G steht f?r **We add R for rate P for pulses and RW for RAW **
        # Geschwindigkeitsmessung/L f?r Lebensdauermessung; x-Messzeit in Stunden;
        # v-erster Buchstabe Vorname; n-erster Buchstabe Familienname)."
 
        self.now = datetime.datetime.now()
        self.filename = os.path.join(self.settings.muonic_setting('data_path'),self.settings.muonic_setting('muonic_filenames') %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"R",opts.user[0],opts.user[1]) )
        self.rawfilename = os.path.join(self.settings.muonic_setting('data_path'),self.settings.muonic_setting('muonic_filenames') %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"RAW",opts.user[0],opts.user[1]) )
        self.raw_mes_start = False

        self.decayfilename = os.path.join(self.settings.muonic_setting('data_path'),self.settings.muonic_setting('muonic_filenames') %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"L",opts.user[0],opts.user[1]) )
        self.pulse_mes_start = None
        self.writepulses = False
        if self.writepulses:
                self.daq.put('CE')
                self.pulsefilename = os.path.join(self.settings.muonic_setting('data_path'),self.settings.muonic_setting('muonic_filenames') %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"P",opts.user[0],opts.user[1]) )
                self.pulse_mes_start = self.now
        else:
                self.pulsefilename = ''
                self.pulse_mes_start = False
        self.statusline = self.settings.muonic_setting('status_line')
        self.channel_counts = [0,0,0,0,0] #[trigger,ch0,ch1,ch2,ch3]
        self.daq.put('TL')
        time.sleep(0.5) #give the daq some time to ract
        self.threshold_ch = []

        self.channelcheckbox = []
        self.vetocheckbox = []
        self.coincidencecheckbox = []
        for i in range(4):
            self.channelcheckbox.append(True)
            self.vetocheckbox.append(False)
            self.coincidencecheckbox.append(False)
            self.threshold_ch.append(300)

        self.coincidencecheckbox[0] = True
        
        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_thresholds_from_queue(msg)

            except DAQIOError:
                self.logger.debug("Queue empty!")

        self.coincidence_time = 0.

        self.daq.put('DC')
        time.sleep(0.5) #give the daq some time to ract
        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_channels_from_queue(msg)

            except DAQIOError:
                self.logger.debug("Queue empty!")
                
        self.pulseextractor = pa.PulseExtractor(pulsefile=self.pulsefilename) 
        self.pulses = None

        # prepare fields for scalars 
        self.scalars_ch0_previous = 0
        self.scalars_ch1_previous = 0
        self.scalars_ch2_previous = 0
        self.scalars_ch3_previous = 0
        self.scalars_trigger_previous = 0
        self.scalars_time = 0
        # define the begin of the timeintervall 
        # for the rate calculation
        now = time.time()
        self.thisscalarquery = now
        self.lastscalarquery = now
        self.query_daq_for_scalars()
        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_scalars_from_queue(msg)
            except DAQIOError:
                self.logger.debug("Queue empty!")
        
        # A timer to periodically call processIncoming and check what is in the queue
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.processIncoming)
        
        self.tabwidget = QtGui.QTabWidget(self)
        #pal = QtGui.QPalette()
        #pal.setColor(QtGui.QPalette.Window, QtGui.QColor(0,222,0))
        #self.tabwidget.setPalette(pal)
        self.tabwidget.mainwindow = self.parentWidget()

        self.timewindow = 5.0
        self.logger.info("Timewindow is %4.2f" %self.timewindow)

        self.tabwidget.addTab(RateWidget(logger,parent = self),"Muon Rates")
        self.tabwidget.ratewidget = self.tabwidget.widget(0)

        self.tabwidget.addTab(PulseanalyzerWidget(logger,parent = self),"Pulse Analyzer")
        self.tabwidget.pulseanalyzerwidget = self.tabwidget.widget(1)

        self.tabwidget.addTab(DecayWidget(logger,parent = self),"Muon Decay")
        self.tabwidget.decaywidget = self.tabwidget.widget(2)
      
        self.tabwidget.addTab(VelocityWidget(logger,parent = self),"Muon Velocity")
        self.tabwidget.velocitywidget = self.tabwidget.widget(3)

        self.tabwidget.addTab(StatusWidget(logger,parent=self),"Status")
        self.tabwidget.statuswidget = self.tabwidget.widget(4)

        self.tabwidget.addTab(DAQWidget(logger,parent=self),"DAQ Output")
        self.tabwidget.daqwidget = self.tabwidget.widget(5)

        self.tabwidget.addTab(GPSWidget(logger,parent=self),"GPS Output")
        self.tabwidget.gpswidget = self.tabwidget.widget(6)

        # widgets which shuld be dynmacally updated by the timer should be in this list
        self.tabwidget.dynamic_widgets = [self.tabwidget.decaywidget,self.tabwidget.pulseanalyzerwidget,self.tabwidget.velocitywidget,self.tabwidget.ratewidget]
        self.widgetupdater = QtCore.QTimer()
        QtCore.QObject.connect(self.widgetupdater,
                           QtCore.SIGNAL("timeout()"),
                           self.widgetUpdate)
 
        self.setCentralWidget(self.tabwidget)
        # provide buttons to exit the application
        exit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/24x24/actions/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')

        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()') )

        # prepare the config menu
        config = QtGui.QAction(QtGui.QIcon(''),'Channel Configuration', self)
        config.setStatusTip('Configure the Coincidences and channels')
        self.connect(config, QtCore.SIGNAL('triggered()'), self.muonic_menus.config_menu)

        # prepare the advanced config menu
        advanced = QtGui.QAction(QtGui.QIcon(''),'Advanced Configurations', self)
        advanced.setStatusTip('Advanced configurations')
        self.connect(advanced, QtCore.SIGNAL('triggered()'), self.muonic_menus.advanced_menu)       

        # prepare the threshold menu
        thresholds = QtGui.QAction(QtGui.QIcon(''),'Thresholds', self)
        thresholds.setStatusTip('Set trigger thresholds')
        self.connect(thresholds, QtCore.SIGNAL('triggered()'), self.muonic_menus.threshold_menu)
               
        # helpmenu
        helpdaqcommands = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'DAQ Commands', self)
        self.connect(helpdaqcommands, QtCore.SIGNAL('triggered()'), self.muonic_menus.help_menu)

        # sphinx-documentation
        sphinxdocs = QtGui.QAction(QtGui.QIcon('icons/blah.png'), 'Technical documentation', self)
        self.connect(sphinxdocs,QtCore.SIGNAL('triggered()'),self.muonic_menus.sphinxdoc_menu)
        
        # manual
        manualdocs = QtGui.QAction(QtGui.QIcon('icons/blah.png'), 'Manual', self)
        self.connect(manualdocs,QtCore.SIGNAL('triggered()'),self.muonic_menus.manualdoc_menu)
   
        # about
        aboutmuonic = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'About muonic', self)
        self.connect(aboutmuonic, QtCore.SIGNAL('triggered()'), self.muonic_menus.about_menu)
        
        # create the menubar and fill it with the submenus
        menubar  = self.menuBar()
        filemenu = menubar.addMenu(tr('MainWindow','&File'))
        filemenu.addAction(exit)
        settings = menubar.addMenu(tr('MainWindow', '&Settings'))
        settings.addAction(config)
        settings.addAction(thresholds)
        settings.addAction(advanced)

        helpmenu = menubar.addMenu(tr('MainWindow','&Help'))
        helpmenu.addAction(helpdaqcommands)
        helpmenu.addAction(sphinxdocs)
        helpmenu.addAction(manualdocs)
        helpmenu.addAction(aboutmuonic)

        self.processIncoming()
        self.timer.start(1000)
        self.widgetupdater.start(self.timewindow*1000) 

    def query_daq_for_scalars(self):
        """
        Send a "DS" message to DAQ and record the time when this is done
        """
        self.lastscalarquery = self.thisscalarquery
        self.daq.put("DS")
        self.thisscalarquery = time.time()

    def get_scalars_from_queue(self,msg):
        """
        Explicitely scan a message for scalar informatioin
        Returns True if found, else False
        """
        if len(msg) >= 2 and msg[0]=='D' and msg[1] == 'S':                    
            self.scalars = msg.split()
            time_window = self.thisscalarquery - self.lastscalarquery
            self.logger.debug("Time window %s" %time_window)
            errors = False

            for item in self.scalars:
                if ("S0" in item) & (len(item) == 11):
                    self.scalars_ch0 = int(item[3:],16)
                elif ("S1" in item) & (len(item) == 11):
                    self.scalars_ch1 = int(item[3:],16)
                elif ("S2" in item) & (len(item) == 11):
                    self.scalars_ch2 = int(item[3:],16)
                elif ("S3" in item) & (len(item) == 11):
                    self.scalars_ch3 = int(item[3:],16)
                elif ("S4" in item) & (len(item) == 11):
                    self.scalars_trigger = int(item[3:],16)
                elif ("S5" in item) & (len(item) == 11):
                    self.scalars_time = float(int(item[3:],16))
                #else:
                    #self.logger.debug("unknown item detected: %s" %item.__repr__())
                
            self.scalars_diff_ch0 = self.scalars_ch0 - self.scalars_ch0_previous 
            self.scalars_diff_ch1 = self.scalars_ch1 - self.scalars_ch1_previous 
            self.scalars_diff_ch2 = self.scalars_ch2 - self.scalars_ch2_previous 
            self.scalars_diff_ch3 = self.scalars_ch3 - self.scalars_ch3_previous 
            self.scalars_diff_trigger = self.scalars_trigger - self.scalars_trigger_previous 
            
            self.scalars_ch0_previous = self.scalars_ch0
            self.scalars_ch1_previous = self.scalars_ch1
            self.scalars_ch2_previous = self.scalars_ch2
            self.scalars_ch3_previous = self.scalars_ch3
            self.scalars_trigger_previous = self.scalars_trigger
            
            return True
        else:
            return False 
                
    def get_thresholds_from_queue(self,msg):
        """
        Explicitely scan message for threshold information
        Return True if found, else False
        """
        if msg.startswith('TL') and len(msg) > 9:
            msg = msg.split('=')
            self.threshold_ch = []
            for i in range(3):
                self.threshold_ch.append(int(msg[1][:-2]))
            self.threshold_ch.append(int(msg[4]     ))
            self.logger.debug("Got Thresholds %i %i %i %i" %(self.threshold_ch[0],self.threshold_ch[1],self.threshold_ch[2],self.threshold_ch[3]))
            return True
        else:
            return False
        
    def get_channels_from_queue(self,msg):
        """
        Explicitely scan message for channel information
        Return True if found, else False

        DC gives :
        DC C0=23 C1=71 C2=0A C3=00
        
        Which has the meaning:

        MM - 00 -> 8bits for channel enable/disable, coincidence and veto
        |7   |6   |5          |4          |3       |2       |1 |0       |
        |veto|veto|coincidence|coincidence|channel3|channel2|channel1|channel0|
        ---------------------------bits-------------------------------------
        Set bits for veto:
        ........................
        00 - ch0 is veto
        01 - ch1 is veto
        10 - ch2 is veto
        11 - ch3 is veto
        ........................
        Set bits for coincidence
        ........................
        00 - singles
        01 - twofold
        10 - threefold
        11 - fourfold
        """
        if msg.startswith('DC ') and len(msg) > 25:
            msg = msg.split(' ')
            self.coincidence_time = msg[4].split('=')[1]+ msg[3].split('=')[1]
            msg = bin(int(msg[1][3:], 16))[2:].zfill(8)
            vetoconfig = msg[0:2]
            coincidenceconfig = msg[2:4]
            channelconfig = msg[4:8]

            self.coincidence_time = int(self.coincidence_time, 16)*10
            for i in range(3):
                self.vetocheckbox[i] = False
            self.vetocheckbox[3] = True

            if str(channelconfig[3]) == '0':
                self.channelcheckbox[0] = False
            else:
                self.channelcheckbox[0] = True

            if str(channelconfig[2]) == '0':
                self.channelcheckbox[1] = False
            else:
                self.channelcheckbox[1] = True

            if str(channelconfig[1]) == '0':
                self.channelcheckbox[2] = False
            else:
                self.channelcheckbox[2] = True
            if str(channelconfig[0]) == '0':
                self.channelcheckbox[3] = False
            else:
                self.channelcheckbox[3] = True
            if str(coincidenceconfig) == '00':
                self.coincidencecheckbox[0] = True
            else:
                self.coincidencecheckbox[0] = False
            if str(coincidenceconfig) == '01':
                self.coincidencecheckbox[1] = True
            else:
                self.coincidencecheckbox[1] = False
            if str(coincidenceconfig) == '10':
                self.coincidencecheckbox[2] = True
            else:
                self.coincidencecheckbox[2] = False

            if str(coincidenceconfig) == '11':
                self.coincidencecheckbox[3] = True
            else:
                self.coincidencecheckbox[3] = False

            if str(vetoconfig) == '00':
                self.vetocheckbox[3] = False
            else:
                if str(vetoconfig) == '01': self.vetocheckbox[0] = True
                if str(vetoconfig) == '10': self.vetocheckbox[1] = True
                if str(vetoconfig) == '11': self.vetocheckbox[2] = True
            
            self.logger.debug('Coincidence timewindow %s ns' %(str(self.coincidence_time)))
            self.logger.debug("Got channel configurations: %i %i %i %i" %(self.channelcheckbox[0],self.channelcheckbox[1],self.channelcheckbox[2],self.channelcheckbox[3]))
            self.logger.debug("Got coincidence configurations: %i %i %i %i" %(self.coincidencecheckbox[0],self.coincidencecheckbox[1],self.coincidencecheckbox[2],self.coincidencecheckbox[3]))
            self.logger.debug("Got veto configurations: %i %i %i %i" %(self.vetocheckbox[3],self.vetocheckbox[0],self.vetocheckbox[1],self.vetocheckbox[2]))

            return True
        else:
            return False

    def processIncoming(self):
        """
        Handle all the messages currently in the daq 
        and pass the result to the corresponding widgets
        """
        while self.daq.data_available():

            try:
                msg = self.daq.get(0)

            except DAQIOError:
                self.logger.debug("Queue empty!")
                return None

            self.tabwidget.daqwidget.text_box.appendPlainText(str(msg))
            if (self.tabwidget.gpswidget.is_active() and self.tabwidget.gpswidget.isEnabled()):
                if len(self.tabwidget.gpswidget.gps_dump) <= self.tabwidget.gpswidget.read_lines:
                    self.tabwidget.gpswidget.gps_dump.append(msg)
                if len(self.tabwidget.gpswidget.gps_dump) == self.tabwidget.gpswidget.read_lines:
                    self.tabwidget.gpswidget.calculate()
                continue

            if self.tabwidget.statuswidget.isVisible() and self.tabwidget.statuswidget.is_active():
                self.tabwidget.statuswidget.update()

            if msg.startswith('DC') and len(msg) > 2 and self.tabwidget.decaywidget.is_active():
                try:
                    split_msg = msg.split(" ")
                    self.tabwidget.decaywidget.previous_coinc_time_03 = split_msg[4].split("=")[1]
                    self.tabwidget.decaywidget.previous_coinc_time_02 = split_msg[3].split("=")[1]
                except:
                    self.logger.debug('Wrong DC command.')

            if self.tabwidget.daqwidget.write_file:
                try:
                    if not self.statusline:
                        fields = msg.rstrip("\n").split(" ")
                        if ((len(fields) == 16) and (len(fields[0]) == 8)):
                            self.tabwidget.daqwidget.outputfile.write(str(msg)+'\n')
                        else:
                            self.logger.debug("Not writing line '%s' to file because it does not contain trigger data" %msg)
                    else:
                        self.tabwidget.daqwidget.outputfile.write(str(msg)+'\n')

                except ValueError:
                    self.logger.warning('Trying to write on closed file, captured!')

            if self.get_thresholds_from_queue(msg):
                continue

            if self.get_channels_from_queue(msg):
                continue

            if msg.startswith('ST') or len(msg) < 50:
                continue
            
            if self.get_scalars_from_queue(msg):
                time_window = self.thisscalarquery - self.lastscalarquery
                rates = (self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window, self.scalars_diff_trigger/time_window, time_window, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_trigger)
                self.tabwidget.ratewidget.calculate(rates)
                
                if self.tabwidget.ratewidget.data_file_write:
                    try:
                        self.tabwidget.ratewidget.data_file.write('%f %f %f %f %f %f %f %f %f %f \n' % (self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window,self.scalars_diff_trigger/time_window,time_window))
                        self.logger.debug("Rate plot data was written to %s" %self.tabwidget.ratewidget.data_file.__repr__())
                    except ValueError:
                        self.logger.warning("ValueError, Rate plot data was not written to %s" %self.tabwidget.ratewidget.data_file.__repr__())
                continue
            
            elif (self.tabwidget.decaywidget.is_active() or self.tabwidget.pulseanalyzerwidget.is_active() or self.pulsefilename or self.tabwidget.velocitywidget.is_active()):#self.showpulses or self.pulsefilename) :
                self.pulses = self.pulseextractor.extract(msg)
                if self.pulses != None:
                    self.tabwidget.pulseanalyzerwidget.calculate(self.pulses)

                    self.channel_counts[0] += 1                         
                    for channel,pulses in enumerate(self.pulses[1:]):
                        if pulses:
                            for pulse in pulses:
                                self.channel_counts[channel + 1] += 1
               
                    if self.tabwidget.velocitywidget.is_active():
                        self.tabwidget.velocitywidget.calculate(self.pulses)

                    if self.tabwidget.decaywidget.is_active():
                        self.tabwidget.decaywidget.calculate(self.pulses)
                continue
            
    def widgetUpdate(self):
        """
        Update the widgets every readout interval. It querys for scalers
        """
        self.query_daq_for_scalars()
        for widg in self.tabwidget.dynamic_widgets:
            if widg.is_active():
                widg.update()

    def closeEvent(self, ev):
        """
        Is triggered when the window is closed, we have to reimplement it
        to provide our special needs for the case the program is ended.
        """
        self.logger.info('Attempting to close Window!')
        reply = QtGui.QMessageBox.question(self, 'Attention!',
                'Do you really want to exit?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            now = datetime.datetime.now()

            if self.tabwidget.daqwidget.write_file:
                self.tabwidget.daqwidget.write_file = False
                mtime = now - self.raw_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The raw data was written for %f hours" % mtime)
                newrawfilename = self.rawfilename.replace("HOURS",str(mtime))
                shutil.move(self.rawfilename,newrawfilename)
                self.tabwidget.daqwidget.outputfile.close()

            if self.tabwidget.decaywidget.is_active():

                mtime = now - self.tabwidget.decaywidget.dec_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The muon decay measurement was active for %f hours" % mtime)
                newmufilename = self.decayfilename.replace("HOURS",str(mtime))
                shutil.move(self.decayfilename,newmufilename)

            if self.pulsefilename:
                old_pulsefilename = self.pulsefilename
                # no pulses shall be extracted any more, 
                # this means changing lots of switches
                self.pulsefilename = False
                self.showpulses = False
                self.pulseextractor.close_file()
                mtime = now - self.pulse_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The pulse extraction measurement was active for %f hours" % mtime)
                newpulsefilename = old_pulsefilename.replace("HOURS",str(mtime))
                shutil.move(old_pulsefilename,newpulsefilename)
              
            self.tabwidget.ratewidget.data_file_write = False
            self.tabwidget.ratewidget.data_file.close()
            mtime = now - self.tabwidget.ratewidget.rate_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
            self.logger.info("The rate measurement was active for %f hours" % mtime)
            newratefilename = self.filename.replace("HOURS",str(mtime))
            shutil.move(self.filename,newratefilename)
            time.sleep(0.5)
            self.tabwidget.writefile = False
            try:
                self.tabwidget.decaywidget.mu_file.close()
            except AttributeError:
                pass

            self.emit(QtCore.SIGNAL('lastWindowClosed()'))
            self.close()

        else:
            ev.ignore()
