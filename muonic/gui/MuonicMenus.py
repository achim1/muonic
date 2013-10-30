"""
Provide the different menus for the gui
"""

from PyQt4 import QtGui
from PyQt4 import QtCore
import time
import os.path
import webbrowser

from MuonicDialogs import ThresholdDialog,ConfigDialog,HelpDialog,DecayConfigDialog,PeriodicCallDialog,AdvancedDialog

class MuonicMenus(object):
    """
    Provide the different menus for the gui
    """
    def __init__(self, parent):
        self.mainwindow = parent
        self.daq = self.mainwindow.daq
        self.logger = self.mainwindow.logger

    def threshold_menu(self):
        """
        Shows the threshold dialogue
        """
        self.daq.put('TL')
        # wait explicitely till the thresholds get loaded
        self.logger.info("loading threshold information..")
        time.sleep(1.5)
        threshold_window = ThresholdDialog(self.mainwindow.threshold_ch[0],self.mainwindow.threshold_ch[1],self.mainwindow.threshold_ch[2],self.mainwindow.threshold_ch[3])
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
        self.daq.put('DC')
        # wait explicitely till the channels get loaded
        self.logger.info("loading channel information...")
        time.sleep(1)

        config_window = ConfigDialog(self.mainwindow.channelcheckbox[0],self.mainwindow.channelcheckbox[1],self.mainwindow.channelcheckbox[2],self.mainwindow.channelcheckbox[3],self.mainwindow.coincidencecheckbox[0],self.mainwindow.coincidencecheckbox[1],self.mainwindow.coincidencecheckbox[2],self.mainwindow.coincidencecheckbox[3],self.mainwindow.vetocheckbox[3],self.mainwindow.vetocheckbox[0],self.mainwindow.vetocheckbox[1],self.mainwindow.vetocheckbox[2])
        rv = config_window.exec_()
        if rv == 1:
            
            chan0_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_0")).isChecked() 
            chan1_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_1")).isChecked() 
            chan2_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_2")).isChecked() 
            chan3_active = config_window.findChild(QtGui.QCheckBox,QtCore.QString("channelcheckbox_3")).isChecked() 
            singles = config_window.findChild(QtGui.QRadioButton,QtCore.QString("coincidencecheckbox_0")).isChecked() 
            if singles:
                self.mainwindow.tabwidget.ratewidget.do_not_show_trigger = True
            else:             
                self.mainwindow.tabwidget.ratewidget.do_not_show_trigger = False
            
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
            
            if not coincidence_set:
                tmp_msg += '00'
    
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
        Show a config dialog for advanced options, ie. gatewidth, interval for the rate measurement, options for writing pulsefile and the statusline option
        """
        gatewidth = 0.
        self.daq.put('DC')
        # wait explicitely till the channels get loaded
        self.logger.info("loading channel information...")
        time.sleep(1)

        adavanced_window = AdvancedDialog(self.mainwindow.coincidence_time,self.mainwindow.timewindow,self.mainwindow.statusline)
        rv = adavanced_window.exec_()
        if rv == 1:
            _timewindow = float(adavanced_window.findChild(QtGui.QDoubleSpinBox,QtCore.QString("timewindow")).value())
            _gatewidth = bin(int(adavanced_window.findChild(QtGui.QSpinBox,QtCore.QString("gatewidth")).value())/10).replace('0b','').zfill(16)
            _status = adavanced_window.findChild(QtGui.QCheckBox,QtCore.QString("statusline")).isChecked()
            
            _03 = format(int(_gatewidth[0:8],2),'x').zfill(2)
            _02 = format(int(_gatewidth[8:16],2),'x').zfill(2)
            tmp_msg = 'WC 03 '+str(_03)
            self.daq.put(tmp_msg)
            tmp_msg = 'WC 02 '+str(_02)
            self.daq.put(tmp_msg)
            if _timewindow < 0.01 or _timewindow > 10000.:
                      self.logger.warning("Timewindow too small or too big, resetting to 5 s.")
                      self.mainwindow.timewindow = 5.0
            else:
                self.mainwindow.timewindow = _timewindow
            self.mainwindow.widgetupdater.start(self.mainwindow.timewindow*1000)
            self.mainwindow.status = _status

            self.logger.debug('Writing gatewidth WC 02 %s WC 03 %s' %(_02,_03))
            self.logger.debug('Setting timewindow to %.2f ' %(_timewindow))
            self.logger.debug('Switching statusline option to %s' %(_nostatus))

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
        QtGui.QMessageBox.information(self.mainwindow,
                  "about muonic",
                  "for information see\n http://code.google.com/p/muonic/")

    def sphinxdoc_menu(self):
        """
        Show the sphinx documentation that comes with muonic in a
        web browser
        """
        docs = (os.path.join(self.mainwindow.settings.muonic_setting('doc_path'),"index.html"))
        if not os.path.exists(docs):
            docs = (os.path.join((os.path.dirname(os.path.abspath(__file__)) + os.sep + '..' + os.sep + self.mainwindow.settings.muonic_setting('doc_folder') + os.sep + 'html'),"index.html"))
            if not os.path.exists(docs):
                docs = (os.path.join((os.path.dirname(os.path.abspath(__file__)) + os.sep + '..' + os.sep + 'docs' + os.sep + 'html'),"index.html"))

        self.logger.info("opening docs from %s" %docs)
        success = webbrowser.open(docs)
        if not success:
            self.logger.warning("Can not open webbrowser!")

    def manualdoc_menu(self):
        """
        Show the manual that comes with muonic in a pdf viewer
        """
        docs = (os.path.join(self.mainwindow.settings.muonic_setting('doc_path'),"manual.pdf"))

        self.logger.info("opening docs from %s" %docs)
        success = webbrowser.open(docs)
        if not success:
            self.logger.warning("Can not open PDF reader!")


