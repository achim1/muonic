"""
Provides the main window for the gui part of muonic
"""

# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

# numpy
import numpy as n

# stdlib imports
import datetime

import os
import shutil
import time
import webbrowser


# muonic imports
from ..analysis import PulseAnalyzer as pa
from ..daq.DAQProvider import DAQIOError
from ..__version__ import __version__,__source_location__,\
__docs_hosted_at__
from .styles import LargeScreenMPStyle

from .MuonicDialogs import ThresholdDialog,ConfigDialog,HelpDialog,DecayConfigDialog,PeriodicCallDialog,AdvancedDialog
from .MuonicPlotCanvases import ScalarsCanvas,LifetimeCanvas,PulseCanvas
from .MuonicWidgets import VelocityWidget,PulseanalyzerWidget,DecayWidget,DAQWidget,RateWidget, GPSWidget, StatusWidget

DOCPATH  = (os.path.dirname(os.path.abspath(__file__)) + os.sep + '..' + os.sep + 'docs' + os.sep + 'html')
# this is hard-coded! There must be a better solution...
# if you change here, you have to change in setup.py!
DATAPATH = os.getenv('HOME') + os.sep + 'muonic_data'

if not os.path.isdir(DATAPATH):
    os.mkdir(DATAPATH, 761)

#from TabWidget import TabWidget

tr = QtCore.QCoreApplication.translate

class MainWindow(QtGui.QMainWindow):
    """
    The main application
    """

    def __init__(self, daq, logger, opts,  win_parent = None):
        QtGui.QMainWindow.__init__(self, win_parent)
        self.daq = daq
        self.opts = opts
        self.DATAPATH = DATAPATH
        self.daq_msg = False # try to establish upstream compatibility
                             # B. introduced a DAQMessage here, but I think
                             # this is overkill
                             # however, making it a member allows to distribute
                             # it more easily to daughter widgets

        # we have to ensure that the DAQcard does not sent
        # any automatic status reports every x seconds
        #FIXME: there was an option for that!
        self.nostatus = opts.nostatus
        if self.nostatus:
            self.daq.put('ST 0')

        self.setWindowTitle(QtCore.QString("muonic") )
        self.statusbar = QtGui.QMainWindow.statusBar(self)
        self.logger  = logger
        desktop = QtGui.QDesktopWidget()
        screen_size = QtCore.QRectF(desktop.screenGeometry(desktop.primaryScreen()))
        screen_x = screen_size.x() + screen_size.width()
        screen_y = screen_size.y() + screen_size.height()
        self.logger.info("Screen with size %i x %i detected!" %(screen_x,screen_y))

        # FIXME: make it configurable
        # now simply set to 1600 x 1200
        if screen_x * screen_y >= 1920000:
            LargeScreenMPStyle()
        self.date = time.gmtime()
        # put the file in the data directory
        # we chose a global format for naming the files -> decided on 18/01/2012
        # we use GMT times
        # " Zur einheitlichen Datenbezeichnung schlage ich folgendes Format vor:
        # JJJJ-MM-TT_y_x_vn.dateiformat (JJJJ-Jahr; MM-Monat; TT-Speichertag bzw.
        # Beendigung der Messung; y: G oder L ausw?hlen, G steht f?r **We add R for rate P for pulses and RW for RAW **
        # Geschwindigkeitsmessung/L f?r Lebensdauermessung; x-Messzeit in Stunden;
        # v-erster Buchstabe Vorname; n-erster Buchstabe Familienname)."
        # TODO: consistancy....        
 
        # the time when the rate measurement is started
        self.now = datetime.datetime.now()
        self.filename = os.path.join(DATAPATH,"%s_%s_HOURS_%s%s" %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"R",opts.user[0],opts.user[1]) )
        self.rawfilename = os.path.join(DATAPATH,"%s_%s_HOURS_%s%s" %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"RAW",opts.user[0],opts.user[1]) )
        self.raw_mes_start = False

        self.decayfilename = os.path.join(DATAPATH,"%s_%s_HOURS_%s%s" %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"L",opts.user[0],opts.user[1]) )
        self.pulse_mes_start = None
        self.writepulses = False
        if self.writepulses:
                self.daq.put('CE')
                self.pulsefilename = os.path.join(DATAPATH,"%s_%s_HOURS_%s%s" %(self.now.strftime('%Y-%m-%d_%H-%M-%S'),"P",opts.user[0],opts.user[1]) )
                self.pulse_mes_start = self.now
        else:
                self.pulsefilename = ''
                self.pulse_mes_start = False

        self.daq.put('TL') # get the thresholds
        time.sleep(0.5) #give the daq some time to ract
        self.threshold_ch0 = 300
        self.threshold_ch1 = 300
        self.threshold_ch2 = 300
        self.threshold_ch3 = 300

        self.channelcheckbox_0 = True
        self.channelcheckbox_1 = True
        self.channelcheckbox_2 = True
        self.channelcheckbox_3 = True
        self.coincidencecheckbox_0 = True
        self.coincidencecheckbox_1 = False
        self.coincidencecheckbox_2 = False
        self.coincidencecheckbox_3 = False
        self.vetocheckbox = False
        self.vetocheckbox_0 = False
        self.vetocheckbox_1 = False
        self.vetocheckbox_2 = False
        
        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_thresholds_from_queue(msg)

            except DAQIOError:
                self.logger.debug("Queue empty!")

        self.coincidence_time = 0.

        self.daq.put('DC') # get the channelconfig
        time.sleep(0.5) #give the daq some time to ract
        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_channels_from_queue(msg)

            except DAQIOError:
                self.logger.debug("Queue empty!")
                
        # the pulseextractor for direct analysis
        self.pulseextractor = pa.PulseExtractor(pulsefile=self.pulsefilename) 
        self.pulses = None

        # A timer to periodically call processIncoming and check what is in the queue
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.processIncoming)
        
        #tab widget to hold the different physics widgets
        self.tabwidget = QtGui.QTabWidget(self)
        #pal = QtGui.QPalette()
        #pal.setColor(QtGui.QPalette.Window, QtGui.QColor(0,222,0))
        #self.tabwidget.setPalette(pal)
        #this is a stupid comment for getting upload permission ;)  
        self.tabwidget.mainwindow = self.parentWidget()

        self.timewindow = opts.timewindow #5.0
        self.logger.info("Timewindow is %4.2f" %self.timewindow)

        self.tabwidget.addTab(RateWidget(logger,parent = self),"Muon Rates")
        self.tabwidget.ratewidget = self.tabwidget.widget(0)

        self.tabwidget.addTab(PulseanalyzerWidget(logger,parent = self),"Pulse Analyzer")
        self.tabwidget.pulseanalyzerwidget = self.tabwidget.widget(1)

        self.tabwidget.addTab(DecayWidget(logger,parent = self),"Muon Decay")
        self.tabwidget.decaywidget = self.tabwidget.widget(2)
      
        self.tabwidget.addTab(VelocityWidget(logger, parent = self),"Muon Velocity")
        self.tabwidget.velocitywidget = self.tabwidget.widget(3)

        self.tabwidget.addTab(StatusWidget(logger,parent=self),"Status")
        self.tabwidget.statuswidget = self.tabwidget.widget(4)

        self.tabwidget.addTab(DAQWidget(logger,parent=self),"DAQ Output")
        self.tabwidget.daqwidget = self.tabwidget.widget(5)

        self.tabwidget.addTab(GPSWidget(logger,parent=self),"GPS Output")
        self.tabwidget.gpswidget = self.tabwidget.widget(6)

        # widgets which should be calculated in processIncoming.
        # The widget is only calculated when it is set to active (True)
        #  via widget.active
        # only widgets which need pulses go here
        self.tabwidget.pulse_widgets = [self.tabwidget.pulseanalyzerwidget,\
                                            self.tabwidget.velocitywidget,\
                                            self.tabwidget.decaywidget]
        # the others go in this list
        self.tabwidget.nopulse_widget = [self.tabwidget.ratewidget]

        # widgets which shuld be dynmacally updated by the timer should be in this list
        self.tabwidget.dynamic_widgets = [self.tabwidget.decaywidget,\
                                          self.tabwidget.pulseanalyzerwidget,\
                                          self.tabwidget.velocitywidget,\
                                          self.tabwidget.ratewidget]

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
        self.connect(config, QtCore.SIGNAL('triggered()'), self.config_menu)

        # prepare the advanced config menu
        advanced = QtGui.QAction(QtGui.QIcon(''),'Advanced Configurations', self)
        advanced.setStatusTip('Advanced configurations')
        self.connect(advanced, QtCore.SIGNAL('triggered()'), self.advanced_menu)       

        # prepare the threshold menu
        thresholds = QtGui.QAction(QtGui.QIcon(''),'Thresholds', self)
        thresholds.setStatusTip('Set trigger thresholds')
        self.connect(thresholds, QtCore.SIGNAL('triggered()'), self.threshold_menu)
               
        # helpmenu
        helpdaqcommands = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'DAQ Commands', self)
        self.connect(helpdaqcommands, QtCore.SIGNAL('triggered()'), self.help_menu)

        # sphinx-documentation
        sphinxdocs = QtGui.QAction(QtGui.QIcon('icons/blah.png'), 'Technical documentation', self)
        self.connect(sphinxdocs,QtCore.SIGNAL('triggered()'),self.sphinxdoc_menu)
        
        # manual
        manualdocs = QtGui.QAction(QtGui.QIcon('icons/blah.png'), 'Manual', self)
        self.connect(manualdocs,QtCore.SIGNAL('triggered()'),self.manualdoc_menu)
   
        # about
        aboutmuonic = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'About muonic', self)
        self.connect(aboutmuonic, QtCore.SIGNAL('triggered()'), self.about_menu)
        
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

    #the individual menus
    def threshold_menu(self):
        """
        Shows the threshold dialogue
        """
        # get the actual Thresholds...
        self.daq.put('TL')
        # wait explicitely till the thresholds get loaded
        self.logger.info("loading threshold information..")
        time.sleep(1.5)
        threshold_window = ThresholdDialog(self.threshold_ch0,self.threshold_ch1,self.threshold_ch2,self.threshold_ch3)
        rv = threshold_window.exec_()
        if rv == 1:
            commands = []
            for ch in ["0","1","2","3"]:
                val = threshold_window.findChild(QtGui.QSpinBox,QtCore.QString("thr_ch_" + ch)).value()
                commands.append("TL " + ch + " " + str(val))
                
            for cmd in commands:
                self.daq.put(cmd)
                self.logger.info("Set threshold of channel %s to %s" %(cmd.split()[1],cmd.split()[2]))

        self.daq.put('TL')
  
    def config_menu(self):
        """
        Show the config dialog
        """
        gatewidth = 0.
        # get the actual channels...
        self.daq.put('DC')
        # wait explicitely till the channels get loaded
        self.logger.info("loading channel information...")
        time.sleep(1)

        config_window = ConfigDialog(self.channelcheckbox_0,self.channelcheckbox_1,self.channelcheckbox_2,self.channelcheckbox_3,self.coincidencecheckbox_0,self.coincidencecheckbox_1,self.coincidencecheckbox_2,self.coincidencecheckbox_3,self.vetocheckbox,self.vetocheckbox_0,self.vetocheckbox_1,self.vetocheckbox_2)
        rv = config_window.exec_()
        if rv == 1:
            
            chan0_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_0")).isChecked() 
            chan1_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_1")).isChecked() 
            chan2_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_2")).isChecked() 
            chan3_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_3")).isChecked() 
            singles = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_0")).isChecked() 
            if singles:
                self.tabwidget.ratewidget.do_not_show_trigger = True
            else:             
                self.tabwidget.ratewidget.do_not_show_trigger = False
            
            twofold   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_1")).isChecked() 
            threefold = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_2")).isChecked() 
            fourfold  = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_3")).isChecked() 

            veto    = config_window.findChild(QtGui.QGroupBox,QtCore.QString("vetocheckbox")).isChecked()
            vetochan1 = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_0")).isChecked()
            vetochan2 = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_1")).isChecked()
            vetochan3 = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_2")).isChecked()
            
            tmp_msg = ''
            if veto:
                if vetochan1:
                    tmp_msg += '01'
                elif vetochan2:
                    tmp_msg += '10'
                elif vetochan3:
                    tmp_msg += '11'
                else:
                    tmp_msg += '00' 
            else:
                tmp_msg += '00'
    
            coincidence_set = False
            for coincidence in [(singles,'00'),(twofold,'01'),(threefold,'10'),(fourfold,'11')]:
                if coincidence[0]:
                    tmp_msg += coincidence[1]
                    coincidence_set = True
            
            # else case, just in case
            if not coincidence_set:
                tmp_msg += '00'
    
            # now calculate the correct expression for the first
            # four bits
            self.logger.debug("The first four bits are set to %s" %tmp_msg)
            msg = 'WC 00 ' + hex(int(''.join(tmp_msg),2))[-1].capitalize()
    
            channel_set = False
            enable = ['0','0','0','0']
            for channel in enumerate([chan3_active,chan2_active,chan1_active,chan0_active]):
                if channel[1]:
                    enable[channel[0]] = '1'
                    channel_set = True
            
            if not channel_set:
                msg += '0'
                
            else:
                msg += hex(int(''.join(enable),2))[-1].capitalize()
            
            self.daq.put(msg)
            self.logger.info('The following message was sent to DAQ: %s' %msg)

            self.logger.debug('channel0 selected %s' %chan0_active)
            self.logger.debug('channel1 selected %s' %chan1_active)
            self.logger.debug('channel2 selected %s' %chan2_active)
            self.logger.debug('channel3 selected %s' %chan3_active)
            self.logger.debug('coincidence singles %s' %singles)
            self.logger.debug('coincidence twofold %s' %twofold)
            self.logger.debug('coincidence threefold %s' %threefold)
            self.logger.debug('coincidence fourfold %s' %fourfold)
        self.daq.put('DC')
           
    def advanced_menu(self):
        """
        Show a config dialog for advanced options, ie. gatewidth, interval for the rate measurement, options for writing pulsefile and the nostatus option
        """
        gatewidth = 0.
        # get the actual channels...
        self.daq.put('DC')
        # wait explicitely till the channels get loaded
        self.logger.info("loading channel information...")
        time.sleep(1)

        adavanced_window = AdvancedDialog(self.coincidence_time,self.timewindow,self.nostatus)
        rv = adavanced_window.exec_()
        if rv == 1:
            _timewindow = float(adavanced_window.findChild(QtGui.QDoubleSpinBox,QtCore.QString("timewindow")).value())
            _gatewidth = bin(int(adavanced_window.findChild(QtGui.QSpinBox,QtCore.QString("gatewidth")).value())/10).replace('0b','').zfill(16)
            _nostatus = adavanced_window.findChild(QtGui.QCheckBox,QtCore.QString("nostatus")).isChecked()
            
            _03 = format(int(_gatewidth[0:8],2),'x').zfill(2)
            _02 = format(int(_gatewidth[8:16],2),'x').zfill(2)
            tmp_msg = 'WC 03 '+str(_03)
            self.daq.put(tmp_msg)
            tmp_msg = 'WC 02 '+str(_02)
            self.daq.put(tmp_msg)
            if _timewindow < 0.01 or _timewindow > 10000.:
                      self.logger.warning("Timewindow too small or too big, resetting to 5 s.")
                      self.timewindow = 5.0
            else:
                self.timewindow = _timewindow
            self.widgetupdater.start(self.timewindow*1000)
            self.nostatus = not _nostatus

            self.logger.debug('Writing gatewidth WC 02 %s WC 03 %s' %(_02,_03))
            self.logger.debug('Setting timewindow to %.2f ' %(_timewindow))
            self.logger.debug('Switching nostatus option to %s' %(_nostatus))

        self.daq.put('DC')
             
    def help_menu(self):
        """
        Show a simple help menu
        """
        help_window = HelpDialog()
        help_window.exec_()
        
    def about_menu(self):
        """
        Show a link to the online documentation
        """
        QtGui.QMessageBox.information(self,
                  "about muonic",
                  "version: %s\n source located at: %s"%(__version__,__source_location__))

    def sphinxdoc_menu(self):
        """
        Show the sphinx documentation that comes with muonic in a
        browser
        """
        #docs = (os.path.join(DOCPATH,"index.html"))
        docs = __docs_hosted_at__
        self.logger.debug("Opening docs from %s" %docs)
        success = webbrowser.open(docs)
        if not success:
            self.logger.warning("Can not open webbrowser! Browse to %s to see the docs" %docs)

    def manualdoc_menu(self):
        """
        Show the manual that comes with muonic in a pdf viewer
        """
        docs = (os.path.join(DOCPATH,"manual.pdf"))

        self.logger.info("opening docs from %s" %docs)
        success = webbrowser.open(docs)
        if not success:
            self.logger.warning("Can not open PDF reader!")


                
    def get_thresholds_from_queue(self,msg):
        """
        Explicitely scan message for threshold information
        Return True if found, else False
        """
        if msg.startswith('TL') and len(msg) > 9:
            msg = msg.split('=')
            self.threshold_ch0 = int(msg[1][:-2])
            self.threshold_ch1 = int(msg[2][:-2])
            self.threshold_ch2 = int(msg[3][:-2])
            self.threshold_ch3 = int(msg[4]     )
            self.logger.debug("Got Thresholds %i %i %i %i" %(self.threshold_ch0,self.threshold_ch1,self.threshold_ch2,self.threshold_ch3))
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
            
            self.vetocheckbox_0 = False
            self.vetocheckbox_1 = False
            self.vetocheckbox_2 = False
            self.vetocheckbox = True

            if str(channelconfig[3]) == '0':
                self.channelcheckbox_0 = False
            else:
                self.channelcheckbox_0 = True

            if str(channelconfig[2]) == '0':
                self.channelcheckbox_1 = False
            else:
                self.channelcheckbox_1 = True

            if str(channelconfig[1]) == '0':
                self.channelcheckbox_2 = False
            else:
                self.channelcheckbox_2 = True
            if str(channelconfig[0]) == '0':
                self.channelcheckbox_3 = False
            else:
                self.channelcheckbox_3 = True
            if str(coincidenceconfig) == '00':
                self.coincidencecheckbox_0 = True
            else:
                self.coincidencecheckbox_0 = False
            if str(coincidenceconfig) == '01':
                self.coincidencecheckbox_1 = True
            else:
                self.coincidencecheckbox_1 = False
            if str(coincidenceconfig) == '10':
                self.coincidencecheckbox_2 = True
            else:
                self.coincidencecheckbox_2 = False

            if str(coincidenceconfig) == '11':
                self.coincidencecheckbox_3 = True
            else:
                self.coincidencecheckbox_3 = False


            if str(vetoconfig) == '00':
                self.vetocheckbox = False
            else:
                if str(vetoconfig) == '01': self.vetocheckbox_0 = True
                if str(vetoconfig) == '10': self.vetocheckbox_1 = True
                if str(vetoconfig) == '11': self.vetocheckbox_2 = True
            
            self.logger.debug('Coincidence timewindow %s ns' %(str(self.coincidence_time)))
            self.logger.debug("Got channel configurations: %i %i %i %i" %(self.channelcheckbox_0,self.channelcheckbox_1,self.channelcheckbox_2,self.channelcheckbox_3))
            self.logger.debug("Got coincidence configurations: %i %i %i %i" %(self.coincidencecheckbox_0,self.coincidencecheckbox_1,self.coincidencecheckbox_2,self.coincidencecheckbox_3))
            self.logger.debug("Got veto configurations: %i %i %i %i" %(self.vetocheckbox,self.vetocheckbox_0,self.vetocheckbox_1,self.vetocheckbox_2))

            return True
        else:
            return False

    # this functions gets everything out of the daq
    # All calculations should happen here
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

            self.daq_msg = msg #make it public for daughters
            # Check contents of message and do what it says
            self.tabwidget.daqwidget.calculate()
            if (self.tabwidget.gpswidget.active and self.tabwidget.gpswidget.isEnabled()):
                if len(self.tabwidget.gpswidget.gps_dump) <= self.tabwidget.gpswidget.read_lines:
                    self.tabwidget.gpswidget.gps_dump.append(msg)
                if len(self.tabwidget.gpswidget.gps_dump) == self.tabwidget.gpswidget.read_lines:
                    self.tabwidget.gpswidget.calculate()
                continue

            if (self.tabwidget.statuswidget.isVisible()) and self.tabwidget.statuswidget.active:
                self.tabwidget.statuswidget.update()

            if msg.startswith('DC') and len(msg) > 2 and self.tabwidget.decaywidget.active:
                try:
                    split_msg = msg.split(" ")
                    self.tabwidget.decaywidget.previous_coinc_time_03 = split_msg[4].split("=")[1]
                    self.tabwidget.decaywidget.previous_coinc_time_02 = split_msg[3].split("=")[1]
                except:
                    self.logger.debug('Wrong DC command.')
                continue

            # check for threshold information
            if self.get_thresholds_from_queue(msg):
                continue

            if self.get_channels_from_queue(msg):
                continue

            # status messages
            if msg.startswith('ST') or len(msg) < 50:
                continue

            if self.tabwidget.ratewidget.calculate():
                continue
            
            if (self.tabwidget.decaywidget.active or\
                        self.tabwidget.pulseanalyzerwidget.active or\
                        self.pulsefilename or\
                        self.tabwidget.velocitywidget.active): #self.showpulses or self.pulsefilename) :
                    self.pulses = self.pulseextractor.extract(msg)

            self.widgetCalculate()


    def widgetCalculate(self):
        """
        Starts the widgets calculate function inside the processIncoming. Set active flag (second parameter in the calculate_widgets list) to True if it should run only when the widget is active.
        """
        for widget in self.tabwidget.pulse_widgets:
            if widget.active and (self.pulses is not None):
                widget.calculate()

    def widgetUpdate(self):
        """
        Update the widgets
        """
        for widg in self.tabwidget.dynamic_widgets:
            if widg.active:
                widg.update()

    def closeEvent(self, ev):
        """
        Is triggered when the window is closed, we have to reimplement it
        to provide our special needs for the case the program is ended.
        """

        self.logger.info('Attempting to close Window!')
        # ask kindly if the user is really sure if she/he wants to exit
        reply = QtGui.QMessageBox.question(self, 'Attention!',
                'Do you really want to exit?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.timer.stop()
            self.widgetupdater.stop()
            now = datetime.datetime.now()

            # close the RAW file (if any)
            if self.tabwidget.daqwidget.write_file:
                self.tabwidget.daqwidget.write_file = False
                mtime = now - self.raw_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The raw data was written for %f hours" % mtime)
                newrawfilename = self.rawfilename.replace("HOURS",str(mtime))
                shutil.move(self.rawfilename,newrawfilename)
                self.tabwidget.daqwidget.outputfile.close()

            if self.tabwidget.decaywidget.active:
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
            #print 'HOURS ', now, '|', mtime, '|', mtime.days, '|', str(mtime)                
            mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
            #print 'new mtime ', mtime, str(mtime)
            self.logger.info("The rate measurement was active for %f hours" % mtime)
            newratefilename = self.filename.replace("HOURS",str(mtime))
            #print 'new raw name', newratefilename
            shutil.move(self.filename,newratefilename)
            time.sleep(0.5)
            self.tabwidget.writefile = False
            try:
                self.tabwidget.decaywidget.mu_file.close()
 
            except AttributeError:
                pass

            self.emit(QtCore.SIGNAL('lastWindowClosed()'))
            self.close()

        else: # don't close the mainwindow
            ev.ignore()
