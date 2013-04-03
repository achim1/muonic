"""
Provides the main window for the gui part of muonic
"""

# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

# numpy
import numpy as n

# stdlib imports
import Queue
import datetime

import os
import shutil
import time

# muonic imports
from ..analysis import PulseAnalyzer as pa

from MuonicDialogs import ThresholdDialog,ConfigDialog,HelpDialog
#from ThresholdDialog import ThresholdDialog
#from ConfigDialog import ConfigDialog
#from HelpDialog import HelpDialog
from TabWidget import TabWidget

# temporary, might (should?) go away in future revision..
# GTabWidget is Gordon's version of TabWidget
from GTabWidget import GTabWidget



tr = QtCore.QCoreApplication.translate

class MuonicOptions:
    """
    A simple struct which holds the different
    options for the program
    """

    def __init__(self,timewindow,writepulses,nostatus,user,gordon):

        # put the file in the data directory
        # we chose a global format for naming the files -> decided on 18/01/2012
        # we use GMT times
        # " Zur einheitlichen Datenbezeichnung schlage ich folgendes Format vor:
        # JJJJ-MM-TT_y_x_vn.dateiformat (JJJJ-Jahr; MM-Monat; TT-Speichertag bzw.
        # Beendigung der Messung; y: G oder L ausw?hlen, G steht f?r **We add R for rate P for pulses and RW for RAW **
        # Geschwindigkeitsmessung/L f?r Lebensdauermessung; x-Messzeit in Stunden;
        # v-erster Buchstabe Vorname; n-erster Buchstabe Familienname)."
        # TODO: consistancy....        
 
        date = time.gmtime()

        # this is hard-coded! There must be a better solution...
        # if you change here, you have to change in setup.py!
        datapath = os.getenv('HOME') + os.sep + 'muonic_data'
 
        self.filename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"R",user[0],user[1]) )
        # the time when the rate measurement is started
        now = datetime.datetime.now()
        self.rate_mes_start = now     
        self.rawfilename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"RAW",user[0],user[1]) )
        self.raw_mes_start = False
        self.decayfilename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"L",user[0],user[1]) )
        if writepulses:
                self.pulsefilename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"P",user[0],user[1]) )
                self.pulse_mes_start = now
        else:
                self.pulsefilename = ''
                self.pulse_mes_start = False

        # other options...
        self.timewindow  = timewindow
        self.nostatus    = nostatus
        self.mudecaymode = False
        self.showpulses  = False
        self.gordon      = gordon

        # options for muondecay
        self.singlepulsechannel = 2
        self.doublepulsechannel = 3
        self.vetopulsechannel   = 4
        self.decay_strict       = False

class MainWindow(QtGui.QMainWindow):
    """
    The main application
    """

    def __init__(self, inqueue, outqueue, logger, opts, root, win_parent = None):

        self.logger  = logger
        self.options = MuonicOptions(float(opts.timewindow),opts.writepulses,opts.nostatus,opts.user,opts.gordon)

        # this holds the scalars in the time interval
        self.channel_counts = [0,0,0,0,0] #[trigger,ch0,ch1,ch2,ch3]

        # keep the last decays
        self.decay = []

        # last time, when the 'DS' command was sent
        self.lastscalarquery = 0
        self.thisscalarquery = time.time()
              
        # the current thresholds
        self.threshold_ch0 = 'n.a.'
        self.threshold_ch1 = 'n.a.'
        self.threshold_ch2 = 'n.a.'
        self.threshold_ch3 = 'n.a.'
        #self.thresholds = {"ch0" : "n.a.","ch1" : "n.a.","ch2" : "n.a.","ch3" : "n.a."}

        # the pulseextractor for direct analysis
        self.pulseextractor = pa.PulseExtractor(pulsefile=self.options.pulsefilename) 
        self.dtrigger = pa.DecayTriggerThorough(logger)
        self.pulses = None

        # initialize MainWindow gui
        self.reso_w = 800 # adapt these values for
        self.reso_h = 450 # suitable window size
        QtGui.QMainWindow.__init__(self, win_parent)
        self.resize(self.reso_w, self.reso_h)

        windowtitle = QtCore.QString("muonic") 
        self.setWindowTitle(windowtitle)
        self.statusbar = QtGui.QMainWindow.statusBar(self)
        self.statusbar.showMessage('Ready')      
        # prepare fields for scalars 
        self.scalars_ch0_previous = 0
        self.scalars_ch1_previous = 0
        self.scalars_ch2_previous = 0
        self.scalars_ch3_previous = 0
        self.scalars_trigger_previous = 0
        self.scalars_time = 0
        
        self.pulses_to_show = None
        self.data_file = open(self.options.filename, 'w')
        self.data_file.write('time | chan0 | chan1 | chan2 | chan3 | R0 | R1 | R2 | R3 | trigger | Delta_time \n')
        
        # always write the rate plot data
        self.data_file_write = True

        self.inqueue = inqueue
        self.outqueue = outqueue

        # we have to ensure that the DAQcard does not sent
        # any automatic status reports every x seconds
        self.outqueue.put('ST 0')
        # get threshold and scalars information
        self.outqueue.put('TL')
        self.outqueue.put('DS')
        # an anchor to the Application
        self.root = root

        # A timer to periodically call processIncoming and check what is in the queue
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.processIncoming)
 
        ## Start the timer -- this replaces the initial call to periodicCall
        self.create_widgets()
        self.logger.info("initializing DAQ...")
        str = 'ongoing..'

        for i in xrange(1,int(self.options.timewindow)):
            time.sleep(1)
            str += '..'
            self.logger.info(str)
        self.logger.info("...done!")

        # begin to read out the information
        self.timer.start(1000)
        
    def create_widgets(self):       
        """
        Initialize the tab widget
        """
       
        if self.options.gordon:
            self.tabwidget = GTabWidget(self, self.options.timewindow, self.logger)       
        else:
            self.tabwidget = TabWidget(self,self.options.timewindow,self.logger)

        self.setCentralWidget(self.tabwidget)

        # provide buttons to exit the application
        exit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/24x24/actions/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')

        self.connect(exit, QtCore.SIGNAL('triggered()'), self.exit_program)
        self.connect(self, QtCore.SIGNAL('closeEmitApp()'), QtCore.SLOT('close()') )

        # prepare the config menu
        config = QtGui.QAction(QtGui.QIcon(''),'Channel Configuration', self)
        config.setStatusTip('Configure the Coincidences and channels')
        self.connect(config, QtCore.SIGNAL('triggered()'), self.config_menu)
       
        # prepare the threshold menu
        thresholds = QtGui.QAction(QtGui.QIcon(''),'Thresholds', self)
        thresholds.setStatusTip('Set trigger thresholds')
        self.connect(thresholds, QtCore.SIGNAL('triggered()'), self.threshold_menu)
               
        # helpmenu
        helpdaqcommands = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'DAQ Commands', self)
        self.connect(helpdaqcommands, QtCore.SIGNAL('triggered()'), self.help_menu)
        scalars = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'Scalars', self)

        # create the menubar and fill it with the submenus
        menubar = self.menuBar()
        filemenu = menubar.addMenu(tr('MainWindow','&File'))
        filemenu.addAction(exit)
        settings = menubar.addMenu(tr('MainWindow', '&Settings'))
        settings.addAction(config)
        settings.addAction(thresholds)

        helpmenu = menubar.addMenu(tr('MainWindow','&Help'))
        helpmenu.addAction(helpdaqcommands)
 
    def exit_program(self,*args):
        """
        This function is used either with the 'x' button
        (then an event has to be passed)
        Or it is used with the File->Exit button, than no event
        will be passed.
        """

        ev = False
        if args:
            ev = args[0]
        # ask kindly if the user is really sure if she/he wants to exit
        reply = QtGui.QMessageBox.question(self, 'Attention!',
                'Do you really want to exit?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            now = datetime.datetime.now()

            # close the RAW file (if any)
            if self.tabwidget.write_file:
                self.tabwidget.write_file = False
                mtime = now - self.options.raw_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The raw data was written for %f hours" % mtime)
                newrawfilename = self.options.rawfilename.replace("HOURS",str(mtime))
                shutil.move(self.options.rawfilename,newrawfilename)
                self.tabwidget.outputfile.close()

            if self.options.mudecaymode:

                self.options.mudecaymode = False
                mtime = now - self.options.dec_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The muon decay measurement was active for %f hours" % mtime)
                newmufilename = self.options.decayfilename.replace("HOURS",str(mtime))
                shutil.move(self.options.decayfilename,newmufilename)

            if self.options.pulsefilename:
                old_pulsefilename = self.options.pulsefilename
                # no pulses shall be extracted any more, 
                # this means changing lots of switches
                self.options.pulsefilename = False
                self.options.mudecaymode = False
                self.options.showpulses = False
                self.pulseextractor.close_file()
                mtime = now - self.options.pulse_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The pulse extraction measurement was active for %f hours" % mtime)
                newpulsefilename = old_pulsefilename.replace("HOURS",str(mtime))
                shutil.move(old_pulsefilename,newpulsefilename)
              
            self.data_file_write = False
            self.data_file.close()
            mtime = now - self.options.rate_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
            self.logger.info("The rate measurement was active for %f hours" % mtime)
            newratefilename = self.options.filename.replace("HOURS",str(mtime))
            shutil.move(self.options.filename,newratefilename)
            time.sleep(0.5)
            self.tabwidget.writefile = False
            try:
                self.mu_file.close()
 
            except AttributeError:
                pass

            self.root.quit()           
            self.emit(QtCore.SIGNAL('closeEmitApp()'))

        else: # don't close the mainwindow
            if ev:
                ev.ignore()
            else:
                pass
    
    #the individual menus
    def threshold_menu(self):
        """
        Shows the threshold dialogue
        """
        # get the actual Thresholds...
        self.outqueue.put('TL')
        # wait explicitely till the thresholds get loaded
        self.logger.info("loading threshold information..")
        time.sleep(1.5)
        threshold_window = ThresholdDialog(self.threshold_ch0,self.threshold_ch1,self.threshold_ch2,self.threshold_ch3)
        rv = threshold_window.exec_()
        if rv == 1:
            # Here we should set the thresholds

            # We have to check for integers!
            self.logger.debug("Type of input text is %s and its value is %s" %(type(threshold_window.ch0_input.text()),threshold_window.ch0_input.text()))

            try:
                int(threshold_window.ch0_input.text())
                self.outqueue.put('TL 0 ' + threshold_window.ch0_input.text())

            except ValueError:
                self.logger.info("Can't convert to integer: field 0")
            try:
                int(threshold_window.ch1_input.text())
                self.outqueue.put('TL 1 ' + threshold_window.ch1_input.text())
            except ValueError:
                self.logger.info("Can't convert to integer: field 1")
            try:
                int(threshold_window.ch2_input.text())
                self.outqueue.put('TL 2 ' + threshold_window.ch2_input.text())
            except ValueError:
                self.logger.info("Can't convert to integer: field 2")
            try:
                int(threshold_window.ch3_input.text())
                self.outqueue.put('TL 3 ' + threshold_window.ch3_input.text())
            except ValueError:
                self.logger.info("Can't convert to integer: field 3")
        # get the new thresholds
        self.outqueue.put('TL')
	    

    def config_menu(self):
        """
        Show the config dialog
        """
        config_window = ConfigDialog()
        rv = config_window.exec_()
        if rv == 1:
            
            chan0_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_0")).isChecked() 
            chan1_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_1")).isChecked() 
            chan2_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_2")).isChecked() 
            chan3_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_3")).isChecked() 
            
            singles = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_0")).isChecked() 
            if singles:
                self.tabwidget.scalars_monitor.do_not_show_trigger = True
            else:
                self.tabwidget.scalars_monitor.do_not_show_trigger = False
            
            twofold   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_1")).isChecked() 
            threefold = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_2")).isChecked() 
            fourfold  = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_3")).isChecked() 

            noveto    = config_window.findChild(QtGui.QGroupBox,QtCore.QString("vetocheckbox")).isChecked()
            vetochan1 = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_0")).isChecked()
            vetochan2 = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_1")).isChecked()
            vetochan3 = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_2")).isChecked()

            tmp_msg = ''
    
            for veto in [(noveto,'00'),(vetochan1,'01'),(vetochan2,'10'),(vetochan3,'11')]:
                if veto[0]:
                    tmp_msg += veto[1]
            
            if noveto:
                # ensure that there is no veto active and reset the 
                # temp message, just to be sure
                tmp_msg = '00'
    
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
            
            self.outqueue.put(msg)
            self.logger.info('The following message was sent to DAQ: %s' %msg)
                    
            self.logger.debug('channel0 selected %s' %chan0_active)
            self.logger.debug('channel1 selected %s' %chan1_active)
            self.logger.debug('channel2 selected %s' %chan2_active)
            self.logger.debug('channel3 selected %s' %chan3_active)
            self.logger.debug('coincidence singles %s' %singles)
            self.logger.debug('coincidence twofold %s' %twofold)
            self.logger.debug('coincidence threefold %s' %threefold)
            self.logger.debug('coincidence fourfold %s' %fourfold)
            
    def help_menu(self):
        """
        Show a simple help menu
        """
        help_window = HelpDialog()
        help_window.exec_()

    def clear_function(self):
        """
        Reset the rate plot by clicking the restart button
        """
        self.logger.debug("Clear was called")
        self.tabwidget.scalars_monitor.reset()

    # this functions gets everything out of the inqueue
    # All calculations should happen here
    def processIncoming(self):
        """
        Handle all the messages currently in the inqueue 
        and parse the result to the corresponding widgets
        """
        
        self.logger.debug("length of inqueue: %s" %self.inqueue.qsize())
        while self.inqueue.qsize():

            try:
                msg = self.inqueue.get(0)
                self.logger.debug("Got item from inqueue: %s" %msg.__repr__())

            except Queue.Empty:
                self.logger.debug("Queue empty!")
                return 

            # Check contents of message and do what it says
            self.tabwidget.text_box.appendPlainText(str(msg))
            if self.tabwidget.write_file:
                try:
                    if self.options.nostatus:
                        fields = msg.rstrip("\n").split(" ")
                        if ((len(fields) == 16) and (len(fields[0]) == 8)):
                            self.tabwidget.outputfile.write(str(msg)+'\n')
                        else:
                            self.logger.debug("Not writing line '%s' to file because it does not contain trigger data" %msg)
                    else:
                        self.tabwidget.outputfile.write(str(msg)+'\n')

                except ValueError:
                    self.logger.info('Trying to write on closed file, captured!')

            # check for threshold information
            if msg.startswith('TL') and len(msg) > 9:
                msg = msg.split('=')
                self.threshold_ch0 = msg[1][:-2]
                self.threshold_ch1 = msg[2][:-2]
                self.threshold_ch2 = msg[3][:-2]
                self.threshold_ch3 = msg[4]
                return  

            # status messages
            if msg.startswith('ST') or len(msg) < 50:
                return

            # check for scalar information
            if len(msg) >= 2 and msg[0]=='D' and msg[1] == 'S':                    
                self.scalars = msg.split()
                time_window = self.thisscalarquery
                self.logger.debug("Time window %s" %time_window)

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
                    else:
                        self.logger.debug("unknown item detected: %s" %item.__repr__())

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
                #send the counted scalars to the subwindow
                self.tabwidget.scalars_result = (self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window, self.scalars_diff_trigger/time_window, time_window, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_trigger)
                #write the rates to data file
                # we have to catch IOErrors, can occur if program is 
                # exited
                if self.data_file_write:
                    try:
                        self.data_file.write('%f %f %f %f %f %f %f %f %f %f %f \n' % (self.scalars_time, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window,self.scalars_diff_trigger/time_window,time_window))
                        self.logger.debug("Rate plot data was written to %s" %self.data_file.__repr__())
                    except ValueError:
                        self.logger.warning("ValueError, Rate plot data was not written to %s" %self.data_file.__repr__())

            elif (self.options.mudecaymode or self.options.showpulses or self.options.pulsefilename) :
                self.pulses = self.pulseextractor.extract(msg)
                if self.pulses is not None:
                    self.pulses_to_show = self.pulses

                # FIXME: What is that for?      
                # -> it is to get the rate from the pulses
                # so no more DAQ queries are needed              
                if (self.pulses != None):
                    # we have to count the triggers in the time intervall
                    self.channel_counts[0] += 1                         
                    for channel,pulses in enumerate(self.pulses[1:]):
                        if pulses:
                            for pulse in pulses:
                                self.channel_counts[channel] += 1

                if self.options.mudecaymode:
                    if self.pulses != None:
                        tmpdecay = self.dtrigger.trigger(self.pulses,single_channel = self.options.singlepulsechannel, double_channel = self.options.doublepulsechannel, veto_channel = self.options.vetopulsechannel,strict = self.options.decay_strict)                   
                        if tmpdecay != None:
                            when = time.asctime()
                            self.decay.append((tmpdecay/100.,when))
                            self.logger.info('We have found a decaying muon with a decaytime of %f at %s' %(tmpdecay,when)) 
                            self.tabwidget.muondecaycounter += 1
                            self.tabwidget.lastdecaytime = when
                        # cleanup
                        del tmpdecay


   
    def closeEvent(self, ev):
        """
        Is triggered when the window is closed, we have to reimplement it
        to provide our special needs for the case the program is ended.
        """

        self.logger.info('Attempting to close Window!')
        self.exit_program(ev)

