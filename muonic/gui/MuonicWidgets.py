"""
Provide the different physics widgets
"""


# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

#muonic imports
from .LineEdit import LineEdit
from .MuonicPlotCanvases import ScalarsCanvas,LifetimeCanvas,PulseCanvas,VelocityCanvas,PulseWidthCanvas
from .MuonicDialogs import DecayConfigDialog,PeriodicCallDialog, VelocityConfigDialog, FitRangeConfigDialog
from ..analysis.fit import main as fit
from ..analysis.fit import gaussian_fit
from ..analysis.PulseAnalyzer import VelocityTrigger,DecayTriggerThorough
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time

tr = QtCore.QCoreApplication.translate

C = 29979245000 # cm/s

class RateWidget(QtGui.QWidget):
    """
    Display rate plot
    """
    def __init__(self,logger,parent = None):
        QtGui.QWidget.__init__(self,parent = parent)
        self.mainwindow = self.parentWidget()
        self.logger           = logger
        self.run              = False
        self.scalers_result   = False
        self.MAXLENGTH        = 40
        self.scalers_monitor  = ScalarsCanvas(self, logger, self.MAXLENGTH)
        self.rate_mes_start   = datetime.datetime.now()
        self.previous_ch_counts = {"ch0" : 0 ,"ch1" : 0,"ch2" : 0,"ch3": 0}
        self.ch_counts = {"ch0" : 0 ,"ch1" : 0,"ch2" : 0,"ch3": 0}
        self.now = datetime.datetime.now()
        # define the begin of the timeintervall
        # for the rate calculation
        self.lastscalarquery = 0
        self.thisscalarquery = time.time()
        self.timewindow = 0
        self.do_not_show_trigger = False
        # prepare fields for scalars
        self.scalars_ch0_previous = 0
        self.scalars_ch1_previous = 0
        self.scalars_ch2_previous = 0
        self.scalars_ch3_previous = 0
        self.scalars_trigger_previous = 0
        self.scalars_time = 0
        self.start_button = QtGui.QPushButton(tr('MainWindow', 'Start run'))
        self.stop_button = QtGui.QPushButton(tr('MainWindow', 'Stop run'))
        self.label_mean_rates = QtGui.QLabel(tr('MainWindow','mean rates:'))
        self.label_total_scalers = QtGui.QLabel(tr('MainWindow','total counts:'))
        self.label_started = QtGui.QLabel(tr('MainWindow','started:'))
        self.rates = dict()
        self.rates['rates']= None
        self.rates['rates_buffer'] = dict()
        for ch in ['ch0','ch1','ch2','ch3','l_time','trigger']:
            self.rates['rates_buffer'][ch] = []
        self.rates['label_ch0'] = QtGui.QLabel(tr('MainWindow','channel 0:'))
        self.table = QtGui.QTableWidget(5,2,self)
        self.table.setColumnWidth(0,85)
        self.table.setColumnWidth(1,60)
        self.table.setHorizontalHeaderLabels(["rate [1/s]","counts"])
        self.table.setVerticalHeaderLabels(["channel 0","channel 1","channel 2","channel 3","trigger"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.scalers = dict()
        self.scalers['scalers_buffer'] = dict()
        for ch in ['ch0','ch1','ch2','ch3','trigger']:
            self.scalers['scalers_buffer'][ch] = 0
        
        for cn in enumerate(['edit_ch0','edit_ch1','edit_ch2','edit_ch3','edit_trigger']):
            self.rates[cn[1]] = QtGui.QTableWidgetItem('--')
            self.scalers[cn[1]] = QtGui.QTableWidgetItem('--')
            self.table.setItem(cn[0], 0, self.rates[cn[1]])
            self.rates[cn[1]].setFlags(QtCore.Qt.ItemIsEditable)
            #self.rates[cn[1]].setFlags(QtCore.Qt.ItemIsSelectable)
            self.rates[cn[1]].setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(cn[0], 1, self.scalers[cn[1]])
            self.scalers[cn[1]].setFlags(QtCore.Qt.ItemIsEditable)
            self.scalers[cn[1]].setFlags(QtCore.Qt.ItemIsSelectable)
            self.scalers[cn[1]].setFlags(QtCore.Qt.ItemIsEnabled)

        self.general_info = dict()
        self.general_info['label_date'] = QtGui.QLabel(tr('MainWindow',''))
        self.general_info['edit_date'] = QtGui.QLineEdit(self)
        self.general_info['edit_date'].setReadOnly(True)
        self.general_info['edit_date'].setDisabled(True)
        self.general_info['label_daq_time'] = QtGui.QLabel(tr('MainWindow','daq time:'))
        self.general_info['edit_daq_time'] = QtGui.QLineEdit(self)
        self.general_info['edit_daq_time'].setReadOnly(True)
        self.general_info['edit_daq_time'].setDisabled(True)
        self.general_info['label_max_rate'] = QtGui.QLabel(tr('MainWindow','max rate:'))
        self.general_info['edit_max_rate'] = QtGui.QLineEdit(self)
        self.general_info['edit_max_rate'].setReadOnly(True)
        self.general_info['edit_max_rate'].setDisabled(True)
        self.general_info['max_rate'] = 0
        self.general_info['min_rate'] = 0

        self.data_file = open(self.mainwindow.filename, 'w')
        self.data_file.write('chan0 | chan1 | chan2 | chan3 | R0 | R1 | R2 | R3 | trigger | Delta_time \n')
        # always write the rate plot data
        self.data_file_write = False

        QtCore.QObject.connect(self.start_button,
                              QtCore.SIGNAL("clicked()"),
                              self.startClicked
                              )

        QtCore.QObject.connect(self.stop_button,
                              QtCore.SIGNAL("clicked()"),
                              self.stopClicked
                              )
        self.stop_button.setEnabled(False)

        ntb = NavigationToolbar(self.scalers_monitor, self)
        rate_widget = QtGui.QGridLayout(self)
        plotBox = QtGui.QGroupBox("")
        plotBox.setObjectName("plotbox")
        plotlayout = QtGui.QGridLayout(plotBox)
        valueBox = QtGui.QGroupBox("")
        valueBox.setObjectName("valuebox")
        valueBox.setMaximumWidth(500)
        valuelayout = QtGui.QGridLayout(valueBox)
        buttomlineBox = QtGui.QGroupBox("")
        buttomlineBox.setObjectName("valuebox")
        blinelayout = QtGui.QGridLayout(buttomlineBox)
        plotlayout.addWidget(self.scalers_monitor,0,0,1,2)
        valuelayout.addWidget(self.table,0,0,1,2)

        valuelayout.addWidget(self.label_started,1,0)
        #valuelayout.addWidget(self.general_info['label_date'],11,3)
        valuelayout.addWidget(self.general_info['edit_date'],1,1,1,1)
        valuelayout.addWidget(self.general_info['label_daq_time'],2,0)
        valuelayout.addWidget(self.general_info['edit_daq_time'],2,1)
        valuelayout.addWidget(self.general_info['label_max_rate'],3,0)
        valuelayout.addWidget(self.general_info['edit_max_rate'],3,1)

        self.table.setEnabled(False)
        blinelayout.addWidget(ntb,4,0,1,3)
        blinelayout.addWidget(self.start_button,4,3)
        blinelayout.addWidget(self.stop_button,4,4)

        rate_widget.addWidget(valueBox,0,2)
        rate_widget.addWidget(plotBox,0,0,1,2)
        rate_widget.addWidget(buttomlineBox,4,0,1,3)
        self.setLayout(rate_widget)

        self.first_bin = False

    def query_daq_for_scalars(self):
        self.lastscalarquery = self.thisscalarquery
        self.mainwindow.daq.put("DS")
        self.thisscalarquery = time.time()

    def calculate(self):
        """
        Get the rates from the observed counts
        by dividing by the measurement interval
        """
        msg = self.mainwindow.daq_msg
        if not (len(msg) >= 2 and msg[0]=='D' and msg[1] == 'S'):
            return False

        # if this is the first time calculate is called, we want to set all
        # counters to zero. This is the beginning of the first bin.
        if self.first_bin:
            self.logger.debug("Buffering muon counts for the first bin of the rate plot.")

            scalars = msg.split()
            for item in scalars:
                if ("S0" in item) & (len(item) == 11):
                    self.scalars_ch0_previous = int(item[3:],16)
                elif ("S1" in item) & (len(item) == 11):
                    self.scalars_ch1_previous = int(item[3:],16)
                elif ("S2" in item) & (len(item) == 11):
                    self.scalars_ch2_previous = int(item[3:],16)
                elif ("S3" in item) & (len(item) == 11):
                    self.scalars_ch3_previous = int(item[3:],16)
                elif ("S4" in item) & (len(item) == 11):
                    self.scalars_trigger_previous = int(item[3:],16)
                elif ("S5" in item) & (len(item) == 11):
                    scalars_time = float(int(item[3:],16))

            self.first_bin = False
            return True

        scalars = msg.split()
        for item in scalars:
            if ("S0" in item) & (len(item) == 11):
                scalars_ch0 = int(item[3:],16)
            elif ("S1" in item) & (len(item) == 11):
                scalars_ch1 = int(item[3:],16)
            elif ("S2" in item) & (len(item) == 11):
                scalars_ch2 = int(item[3:],16)
            elif ("S3" in item) & (len(item) == 11):
                scalars_ch3 = int(item[3:],16)
            elif ("S4" in item) & (len(item) == 11):
                scalars_trigger = int(item[3:],16)
            elif ("S5" in item) & (len(item) == 11):
                scalars_time = float(int(item[3:],16))
            #else:
                #self.logger.debug("unknown item detected: %s" %item.__repr__())
        self.scalars_diff_ch0     = scalars_ch0     - self.scalars_ch0_previous
        self.scalars_diff_ch1     = scalars_ch1     - self.scalars_ch1_previous
        self.scalars_diff_ch2     = scalars_ch2     - self.scalars_ch2_previous
        self.scalars_diff_ch3     = scalars_ch3     - self.scalars_ch3_previous
        self.scalars_diff_trigger = scalars_trigger - self.scalars_trigger_previous
        self.scalars_ch0_previous     = scalars_ch0
        self.scalars_ch1_previous     = scalars_ch1
        self.scalars_ch2_previous     = scalars_ch2
        self.scalars_ch3_previous     = scalars_ch3
        self.scalars_trigger_previous = scalars_trigger

        time_window = self.thisscalarquery - self.lastscalarquery
        rates = (self.scalars_diff_ch0/time_window,\
                 self.scalars_diff_ch1/time_window,\
                 self.scalars_diff_ch2/time_window,\
                 self.scalars_diff_ch3/time_window,\
                 self.scalars_diff_trigger/time_window,\
                 time_window,\
                 self.scalars_diff_ch0,\
                 self.scalars_diff_ch1,\
                 self.scalars_diff_ch2,\
                 self.scalars_diff_ch3,\
                 self.scalars_diff_trigger)

        self.rates['rates'] = rates
        self.timewindow += time_window

        self.scalers['scalers_buffer']['ch0'] += rates[6]
        self.scalers['scalers_buffer']['ch1'] += rates[7]
        self.scalers['scalers_buffer']['ch2'] += rates[8]
        self.scalers['scalers_buffer']['ch3'] += rates[9]
        self.scalers['scalers_buffer']['trigger'] += rates[10]

        max_rate = max([rates[i] for i in range(5)])
        min_rate = min([rates[i] for i in range(5)])
        if max_rate > self.general_info['max_rate']:
            self.general_info['max_rate'] = max_rate
        if min_rate < self.general_info['min_rate']:
            self.general_info['max_rate'] = min_rate

        #write the rates to data file
        # we have to catch IOErrors, can occur if program is
        # exited
        if self.data_file_write:
            try:
                self.data_file.write('%f %f %f %f %f %f %f %f %f %f \n' % (self.scalars_diff_ch0,\
                                                                           self.scalars_diff_ch1,\
                                                                           self.scalars_diff_ch2,\
                                                                           self.scalars_diff_ch3,\
                                                                           rates[0],\
                                                                           rates[1],\
                                                                           rates[2],\
                                                                           rates[3],\
                                                                           rates[4],\
                                                                           rates[5]))
                self.logger.debug("Rate plot data was written to %s" %self.data_file.__repr__())
            except ValueError:
                self.logger.warning("ValueError, Rate plot data was not written to %s" %self.data_file.__repr__())
        return True # succesful!

    def update(self):
        """
        Display newly available data
        """
        if self.run:
            self.query_daq_for_scalars()
            if self.timewindow == 0:
                return
            self.general_info['edit_daq_time'].setText('%.2f s' %(self.timewindow))
            self.general_info['edit_max_rate'].setText('%.2f 1/s' %(self.general_info['max_rate']))
            if self.mainwindow.channelcheckbox_0:
                self.rates['edit_ch0'].setText('%.2f' %(self.scalers['scalers_buffer']['ch0']/self.timewindow))
                self.scalers['edit_ch0'].setText('%i' %(self.scalers['scalers_buffer']['ch0']))
            else:
                self.rates['edit_ch0'].setText('off')
                self.scalers['edit_ch0'].setText('off')
            if self.mainwindow.channelcheckbox_1:
                self.rates['edit_ch1'].setText('%.2f' %(self.scalers['scalers_buffer']['ch1']/self.timewindow))
                self.scalers['edit_ch1'].setText('%i' %(self.scalers['scalers_buffer']['ch1']))
            else:
                self.rates['edit_ch1'].setText('off')
                self.scalers['edit_ch1'].setText('off')
            if self.mainwindow.channelcheckbox_2:
                self.rates['edit_ch2'].setText('%.2f' %(self.scalers['scalers_buffer']['ch2']/self.timewindow))
                self.scalers['edit_ch2'].setText('%i' %(self.scalers['scalers_buffer']['ch2']))
            else:
                self.rates['edit_ch2'].setText('off')
                self.scalers['edit_ch2'].setText('off')
            if self.mainwindow.channelcheckbox_3:
                self.rates['edit_ch3'].setText('%.2f' %(self.scalers['scalers_buffer']['ch3']/self.timewindow))
                self.scalers['edit_ch3'].setText('%i' %(self.scalers['scalers_buffer']['ch3']))
            else:
                self.rates['edit_ch3'].setText('off')
                self.scalers['edit_ch3'].setText('off')

            if self.do_not_show_trigger:
                self.rates['edit_trigger'].setText('off')
                self.scalers['edit_trigger'].setText('off')
            else:
                self.rates['edit_trigger'].setText('%.2f' %(self.scalers['scalers_buffer']['trigger']/self.timewindow))
                self.scalers['edit_trigger'].setText('%i' %(self.scalers['scalers_buffer']['trigger']))

            self.scalers_monitor.update_plot(self.rates['rates'],\
                                             self.do_not_show_trigger,\
                                             self.mainwindow.channelcheckbox_0,\
                                             self.mainwindow.channelcheckbox_1,\
                                             self.mainwindow.channelcheckbox_2,\
                                             self.mainwindow.channelcheckbox_3)

    @property
    def active(self):
        return self.run # rate widget is always active    

    def startClicked(self):
        """
        start the rate measurement and write a file
        """
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        time.sleep(0.2)
        self.table.setEnabled(True)

        self.first_bin = True

        self.logger.debug("Start Button Clicked")
        date = time.gmtime()

        self.timewindow = 0
        for ch in ['ch0','ch1','ch2','ch3','trigger']:
            self.scalers['scalers_buffer'][ch] = 0
        for ch in ['ch0','ch1','ch2','ch3','l_time','trigger']:
            self.rates['rates_buffer'][ch] = []

        comment_file = '# new rate measurement run from: %i-%i-%i %i-%i-%i\n'\
                       %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec)

        #FIXME: This does not belong here
        #if self.mainwindow.tabwidget.decaywidget.active:
        #    comment_file = '# new decay measurement run from: %i-%i-%i %i-%i-%i\n'\
        #                   %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec)
        #if self.mainwindow.tabwidget.velocitywidget.active:
        #    comment_file = '# new velocity measurement run from: %i-%i-%i %i-%i-%i\n'\
        #                   %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec)


        self.data_file = open(self.mainwindow.filename, 'a')        
        self.data_file.write(comment_file)
        self.run = True
        self.data_file_write = True
        self.now = datetime.datetime.now()
        
        if not self.mainwindow.channelcheckbox_0:
            self.rates['edit_ch0'].setText('off')
            self.scalers['edit_ch0'].setText('off')
        if not self.mainwindow.channelcheckbox_1:
            self.rates['edit_ch1'].setText('off')
            self.scalers['edit_ch1'].setText('off')
        if not self.mainwindow.channelcheckbox_2:
            self.rates['edit_ch2'].setText('off')
            self.scalers['edit_ch2'].setText('off')
        if not self.mainwindow.channelcheckbox_3:
            self.rates['edit_ch3'].setText('off')
            self.scalers['edit_ch3'].setText('off')
        self.general_info['edit_date'].setDisabled(False)
        self.general_info['edit_daq_time'].setDisabled(False)
        self.general_info['edit_max_rate'].setDisabled(False)
        self.general_info['edit_date'].setText(self.now.strftime('%d.%m.%Y %H:%M:%S'))
        self.general_info['edit_daq_time'].setText('%.2f' %(self.timewindow))
        self.general_info['edit_max_rate'].setText('%.2f' %(self.general_info['max_rate']))
        if self.do_not_show_trigger:
            self.rates['edit_trigger'].setText('off')
            self.scalers['edit_trigger'].setText('off')

        self.scalers_monitor.reset(show_pending=True)
        #time.sleep(3)
        #self.start_button.setEnabled(True)
        
    def stopClicked(self):
        """
        hold the rate measurement plot till buttion is pushed again
        """
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.table.setEnabled(False)

        self.general_info['edit_date'].setDisabled(True)
        self.general_info['edit_daq_time'].setDisabled(True)
        self.general_info['edit_max_rate'].setDisabled(True)

        self.run = False
        self.data_file_write = False
        date = time.gmtime()        
        comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec)
        if not self.data_file.closed:
            self.data_file.write(comment_file)
            self.data_file.close()


class PulseanalyzerWidget(QtGui.QWidget):
    """
    Provide a widget which is able to show a plot of triggered pulses
    """
    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.logger = logger
        self.mainwindow = self.parentWidget()
        self.pulsefile = self.mainwindow.pulseextractor.pulsefile
        self.activatePulseanalyzer = QtGui.QCheckBox(self)
        self.activatePulseanalyzer.setText(tr("Dialog", "Show Oscilloscope and Pulse Width Distribution", None, QtGui.QApplication.UnicodeUTF8))
        self.activatePulseanalyzer.setToolTip(QtCore.QString("The oscilloscope will show the last triggered pulses in the selected time window"))
        self.activatePulseanalyzer.setObjectName("activate_pulseanalyzer")
        grid = QtGui.QGridLayout(self)
        self.pulsecanvas = PulseCanvas(self,logger)
        self.pulsecanvas.setObjectName("pulse_canvas")
        self.pulsewidthcanvas = PulseWidthCanvas(self,logger)
        self.pulsewidthcanvas.setObjectName("pulse_width_canvas")
        ntb = NavigationToolbar(self.pulsecanvas, self)
        ntb2 = NavigationToolbar(self.pulsewidthcanvas, self)
        QtCore.QObject.connect(self.activatePulseanalyzer,
                               QtCore.SIGNAL("clicked()"),
                               self.activatePulseanalyzerClicked
                               )

        grid.addWidget(self.activatePulseanalyzer,0,0,1,2)
        grid.addWidget(self.pulsecanvas,1,0)
        grid.addWidget(ntb,2,0) 
        grid.addWidget(self.pulsewidthcanvas,1,1)
        grid.addWidget(ntb2,2,1)
        self.pulses      = None
        self.pulsewidths = []
        self.active = False

    def calculate(self):
        self.pulses = self.mainwindow.pulses
        if self.pulses is None:
            self.logger.debug("Not received any pulses")
            return None
        # pulsewidths changed because falling edge can be None.
        # pulsewidths = [fe - le for chan in pulses[1:] for le,fe in chan]
        pulsewidths = []
        for chan in self.pulses[1:]:
            for le, fe in chan:
                if fe is not None:
                    pulsewidths.append(fe - le)
                else:
                    pulsewidths.append(0.)
        self.pulsewidths += pulsewidths
        
    def update(self):
        self.pulsecanvas.update_plot(self.pulses)
        self.pulsewidthcanvas.update_plot(self.pulsewidths)
        self.pulsewidths = []

    def activatePulseanalyzerClicked(self):
        """
        Perform extra actions when the checkbox is clicked
        """
        if not self.active:
            self.pulsefile = self.mainwindow.pulseextractor.pulsefile
            self.activatePulseanalyzer.setChecked(True)
            self.active = True
            self.logger.debug("Switching on Pulseanalyzer.")
            self.mainwindow.daq.put("CE")

            self.mainwindow.daq.put('CE')
            if not self.pulsefile:
                self.mainwindow.pulsefilename = os.path.join(self.mainwindow.DATAPATH,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(self.mainwindow.date.tm_year,self.mainwindow.date.tm_mon,self.mainwindow.date.tm_mday,self.mainwindow.date.tm_hour,self.mainwindow.date.tm_min,self.mainwindow.date.tm_sec,"P",self.mainwindow.opts.user[0],self.mainwindow.opts.user[1]))
                self.mainwindow.pulse_mes_start = self.mainwindow.now
                self.mainwindow.pulseextractor.pulsefile = open(self.mainwindow.pulsefilename,'w')

        else:
            self.logger.debug("Switching off Pulseanalyzer.")
            self.activatePulseanalyzer.setChecked(False)            
            self.active = False

            if not self.pulsefile:
                self.mainwindow.pulsefilename = ''
                self.mainwindow.pulse_mes_start = False
                if self.mainwindow.pulseextractor.pulsefile:
                    self.mainwindow.pulseextractor.pulsefile.close()
                self.mainwindow.pulseextractor.pulsefile = False

class StatusWidget(QtGui.QWidget): # not used yet
    """
    Provide a widget which shows the status informations of the DAQ and the muonic software
    """
    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.mainwindow = self.parentWidget()
        self.logger = logger
        self.active = True
        # more functional objects

        self.muonic_stats = dict()
        self.daq_stats = dict()

        self.daq_stats['thresholds'] = list()
        for cnt in range(4):
            self.daq_stats['thresholds'].append('not set yet - click on Refresh.')
        self.daq_stats['active_channel_0'] = None
        self.daq_stats['active_channel_1'] = None
        self.daq_stats['active_channel_2'] = None
        self.daq_stats['active_channel_3'] = None
        self.daq_stats['coincidences'] = 'not set yet - click on Refresh.'
        self.daq_stats['coincidence_timewindow'] = 'not set yet - click on Refresh.'
        self.daq_stats['veto'] = 'not set yet - click on Refresh.'

        self.muonic_stats['start_params'] = 'not set yet - click on Refresh.'
        self.muonic_stats['refreshtime'] = 'not set yet - click on Refresh.'
        self.muonic_stats['open_files'] = 'not set yet - click on Refresh.'
        self.muonic_stats['last_path'] = 'not set yet - click on Refresh.'

        self.label_daq = QtGui.QLabel(tr('MainWindow','Status of the DAQ card:'))
        self.label_thresholds = QtGui.QLabel(tr('MainWindow','Threshold:'))
        self.label_active_channels = QtGui.QLabel(tr('MainWindow','Active channels:'))
        self.label_coincidences = QtGui.QLabel(tr('MainWindow','Trigger condition:'))
        self.label_coincidence_timewindow = QtGui.QLabel(tr('MainWindow','Time window for trigger condition:'))
        self.label_veto = QtGui.QLabel(tr('MainWindow','Veto:'))
        self.thresholds = []
        for cnt in range(4):
            self.thresholds.append(QtGui.QLineEdit(self))
            self.thresholds[cnt].setReadOnly(True)
            self.thresholds[cnt].setText(self.daq_stats['thresholds'][cnt])
            self.thresholds[cnt].setDisabled(True)
        self.active_channel_0 = QtGui.QLineEdit(self)
        self.active_channel_1 = QtGui.QLineEdit(self)
        self.active_channel_2 = QtGui.QLineEdit(self)
        self.active_channel_3 = QtGui.QLineEdit(self)
        self.active_channel_0.setText('Channel 0')
        self.active_channel_1.setText('Channel 1')
        self.active_channel_2.setText('Channel 2')
        self.active_channel_3.setText('Channel 3')
        self.active_channel_0.setReadOnly(True)
        self.active_channel_0.setEnabled(False)
        self.active_channel_1.setReadOnly(True)
        self.active_channel_1.setEnabled(False)
        self.active_channel_2.setReadOnly(True)
        self.active_channel_2.setEnabled(False)
        self.active_channel_3.setReadOnly(True)
        self.active_channel_3.setEnabled(False)
        self.coincidences = QtGui.QLineEdit(self)
        self.coincidences.setReadOnly(True)
        self.coincidences.setDisabled(True)
        self.coincidences.setText(self.daq_stats['coincidences'])
        self.coincidence_timewindow = QtGui.QLineEdit(self)
        self.coincidence_timewindow.setReadOnly(True)
        self.coincidence_timewindow.setDisabled(True)
        self.coincidence_timewindow.setText(self.daq_stats['coincidence_timewindow'])
        self.veto = QtGui.QLineEdit(self)
        self.veto.setReadOnly(True)
        self.veto.setDisabled(True)
        self.veto.setText(self.daq_stats['veto'])

        self.label_muonic = QtGui.QLabel(tr('MainWindow','Status of Muonic:'))
        self.label_measurements = QtGui.QLabel(tr('MainWindow','Active measurements:'))
        self.label_start_params = QtGui.QLabel(tr('MainWindow','Start parameter:'))
        self.label_refreshtime = QtGui.QLabel(tr('MainWindow','Measurement intervals:'))
        self.label_open_files = QtGui.QLabel(tr('MainWindow','Currently opened files:'))
        self.label_last_path = QtGui.QLabel(tr('MainWindow','Last saved files:'))
        self.start_params = QtGui.QPlainTextEdit()
        self.start_params.setReadOnly(True)
        self.start_params.setDisabled(True)
        self.start_params.document().setMaximumBlockCount(10)
        self.measurements = QtGui.QLineEdit(self)
        self.measurements.setReadOnly(True)
        self.measurements.setDisabled(True)
        self.start_params.setPlainText(self.muonic_stats['start_params'])
        self.refreshtime = QtGui.QLineEdit(self)
        self.refreshtime.setReadOnly(True)
        self.refreshtime.setDisabled(True)
        self.refreshtime.setText(self.muonic_stats['refreshtime'])

        self.open_files = QtGui.QPlainTextEdit()
        self.open_files.setReadOnly(True)
        self.open_files.setDisabled(True)
        self.open_files.setPlainText(self.muonic_stats['open_files'])
        self.open_files.document().setMaximumBlockCount(10)
        #self.last_path = QtGui.QLineEdit(self)
        #self.last_path.setReadOnly(True)
        #self.last_path.setDisabled(True)
        #self.last_path.setText(self.muonic_stats['last_path'])

        self.refresh_button  = QtGui.QPushButton(tr('MainWindow','Refresh'))
        self.refresh_button.setDisabled(True)
        QtCore.QObject.connect(self.refresh_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_refresh_clicked
                              )

        self.save_button  = QtGui.QPushButton(tr('MainWindow','Save to file'))
        QtCore.QObject.connect(self.save_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_save_clicked
                              )

        status_layout = QtGui.QGridLayout(self)
        status_layout.addWidget(self.label_daq,0,0)
        status_layout.addWidget(self.label_active_channels,1,0)
        status_layout.addWidget(self.active_channel_0,1,1)
        status_layout.addWidget(self.active_channel_1,1,2)
        status_layout.addWidget(self.active_channel_2,1,3)
        status_layout.addWidget(self.active_channel_3,1,4)
        status_layout.addWidget(self.thresholds[0],2,1)
        status_layout.addWidget(self.label_thresholds,2,0)
        status_layout.addWidget(self.thresholds[1],2,2)
        status_layout.addWidget(self.thresholds[2],2,3)
        status_layout.addWidget(self.thresholds[3],2,4)
        status_layout.addWidget(self.label_coincidences,3,0)
        status_layout.addWidget(self.coincidences,3,1,1,2)
        status_layout.addWidget(self.label_coincidence_timewindow,3,3)
        status_layout.addWidget(self.coincidence_timewindow,3,4)
        status_layout.addWidget(self.label_veto,4,0)
        status_layout.addWidget(self.veto,4,1,1,4)
        nix = QtGui.QLabel(self)        
        status_layout.addWidget(nix,5,0)
        status_layout.addWidget(self.label_muonic,6,0)
        status_layout.addWidget(self.label_measurements,7,0)
        status_layout.addWidget(self.measurements,7,1,1,2)
        status_layout.addWidget(self.label_refreshtime,7,3)
        status_layout.addWidget(self.refreshtime,7,4)
        status_layout.addWidget(self.label_start_params,8,0)
        status_layout.addWidget(self.start_params,8,1,2,4)
        status_layout.addWidget(self.label_open_files,10,0)
        status_layout.addWidget(self.open_files,10,1,2,4)
        #status_layout.addWidget(self.label_last_path,11,1)
        #status_layout.addWidget(self.last_path,11,2,1,8)

        status_layout.addWidget(self.refresh_button,12,0,1,6)
        #status_layout.addWidget(self.save_button,11,2,1,2)

    def on_refresh_clicked(self):
        """
        Refresh the status information
        """
        self.refresh_button.setDisabled(True)        
        self.logger.debug("Refreshing status information.")
        self.mainwindow.daq.put('TL')
        time.sleep(0.5)
        self.mainwindow.daq.put('DC')
        time.sleep(0.5)
        self.active = True
        self.mainwindow.processIncoming()

    def on_save_clicked(self):
        """
        Refresh the status information
        """
        self.logger.debug("Saving status information to file.")
        self.logger.warning('Currently not available!')


    def update(self):
        """
        Fill the status information in the widget.
        """
        self.logger.debug("Refreshing status infos")
        if (self.mainwindow.tabwidget.statuswidget.isVisible()):
            self.muonic_stats['start_params'] = str(self.mainwindow.opts).replace('{', '').replace('}','')
            self.muonic_stats['refreshtime'] = str(self.mainwindow.timewindow)+ ' s'
            self.muonic_stats['last_path'] = 'too'
            
            self.daq_stats['thresholds'][0] = str(self.mainwindow.threshold_ch0)+ ' mV'
            self.daq_stats['thresholds'][1] = str(self.mainwindow.threshold_ch1)+ ' mV'
            self.daq_stats['thresholds'][2] = str(self.mainwindow.threshold_ch2)+ ' mV'
            self.daq_stats['thresholds'][3] = str(self.mainwindow.threshold_ch3)+ ' mV'
            if not self.mainwindow.vetocheckbox:
                self.daq_stats['veto'] = 'no veto set'
            else:
                if self.mainwindow.vetocheckbox_0:
                    self.daq_stats['veto'] = 'veto with channel 0'
                if self.mainwindow.vetocheckbox_1:
                    self.daq_stats['veto'] = 'veto with channel 1'
                if self.mainwindow.vetocheckbox_2:
                    self.daq_stats['veto'] = 'veto with channel 2'

            self.daq_stats['coincidence_timewindow'] = str(self.mainwindow.coincidence_time) + ' ns'

            self.daq_stats['active_channel_0'] = self.mainwindow.channelcheckbox_0
            self.daq_stats['active_channel_1'] = self.mainwindow.channelcheckbox_1
            self.daq_stats['active_channel_2'] = self.mainwindow.channelcheckbox_2
            self.daq_stats['active_channel_3'] = self.mainwindow.channelcheckbox_3
            if self.mainwindow.coincidencecheckbox_0:
                self.daq_stats['coincidences'] = 'Single Coincidence.'
            elif self.mainwindow.coincidencecheckbox_1:
                self.daq_stats['coincidences'] = 'Twofold Coincidence.'
            elif self.mainwindow.coincidencecheckbox_2:
                self.daq_stats['coincidences'] = 'Threefold Coincidence.'
            elif self.mainwindow.coincidencecheckbox_3:
                self.daq_stats['coincidences'] = 'Fourfold Coincidence.'

            for cnt in range(4):
                self.thresholds[cnt].setDisabled(False)                
                self.thresholds[cnt].setText(self.daq_stats['thresholds'][cnt])
                self.thresholds[cnt].setEnabled(True)

            self.active_channel_0.setEnabled(self.daq_stats['active_channel_0'])
            self.active_channel_1.setEnabled(self.daq_stats['active_channel_1'])
            self.active_channel_2.setEnabled(self.daq_stats['active_channel_2'])
            self.active_channel_3.setEnabled(self.daq_stats['active_channel_3'])
            self.coincidences.setText(self.daq_stats['coincidences'])
            self.coincidences.setEnabled(True)
            self.coincidence_timewindow.setText(self.daq_stats['coincidence_timewindow'])
            self.coincidence_timewindow.setEnabled(True)
            self.veto.setText(self.daq_stats['veto'])
            self.veto.setEnabled(True)
            
            self.muonic_stats['open_files'] = str(self.mainwindow.filename)
            if self.mainwindow.tabwidget.daqwidget.write_file:
                self.muonic_stats['open_files'] += ', ' + self.mainwindow.rawfilename
            if self.mainwindow.tabwidget.decaywidget.active:
                self.muonic_stats['open_files'] += ', ' + self.mainwindow.decayfilename
            if self.mainwindow.writepulses:
                self.muonic_stats['open_files'] += ', ' + self.mainwindow.pulsefilename
            self.start_params.setPlainText(self.muonic_stats['start_params'])
            self.start_params.setEnabled(True)
            self.refreshtime.setText(self.muonic_stats['refreshtime'])
            self.refreshtime.setEnabled(True)
            self.open_files.setPlainText(self.muonic_stats['open_files'])
            self.open_files.setEnabled(True)
            #self.last_path.setText(self.muonic_stats['last_path'])
            #self.last_path.setEnabled(True)
            measurements = ''
            if self.mainwindow.tabwidget.ratewidget.active:
                measurements = 'Muon Rates'
            if self.mainwindow.tabwidget.decaywidget.active:
                measurements += ', Muon Decay'
            if self.mainwindow.tabwidget.velocitywidget.active:
                measurements += ', Muon Velocity'
            if self.mainwindow.tabwidget.pulseanalyzerwidget.active:
                measurements += ', Pulse Analyzer'
            self.measurements.setText(measurements)
            self.measurements.setEnabled(True)
            self.start_params.setEnabled(True)

            self.active = False
        else:
            self.logger.debug("Status informations widget not active - ignoring update call.")
        self.refresh_button.setDisabled(False)
        self.active = False

        #FIXME: status widget has no pulsefile!
        #if not self.pulsefile:
        #    self.mainwindow.pulsefilename = ''
        #    self.mainwindow.pulse_mes_start = False
        #    if self.mainwindow.pulseextractor.pulsefile:
        #        self.mainwindow.pulseextractor.pulsefile.close()
        #    self.mainwindow.pulseextractor.pulsefile = False



class VelocityWidget(QtGui.QWidget):

    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.logger = logger
        self.mainwindow = self.parentWidget()
        self.upper_channel = 0
        self.lower_channel = 1
        self.trigger = VelocityTrigger(logger)
        self.times = []
        self.active = False
        self.binning = (0.,30,25)
        self.fitrange = (self.binning[0],self.binning[1])

        self.activateVelocity = QtGui.QCheckBox(self)
        self.activateVelocity.setText(tr("Dialog", "Measure Flight Time", None, QtGui.QApplication.UnicodeUTF8))
        self.activateVelocity.setObjectName("activate_velocity")
        self.velocityfit_button = QtGui.QPushButton(tr('MainWindow', 'Fit!')) 
        self.velocityfitrange_button = QtGui.QPushButton(tr('MainWindow', 'Fit Range')) 
        layout = QtGui.QGridLayout(self)
        layout.addWidget(self.activateVelocity,0,0,1,3)
        self.velocitycanvas = VelocityCanvas(self,logger,binning = self.binning)
        self.velocitycanvas.setObjectName("velocity_plot")
        layout.addWidget(self.velocitycanvas,1,0,1,3)
        ntb = NavigationToolbar(self.velocitycanvas, self)
        layout.addWidget(ntb,2,0)
        layout.addWidget(self.velocityfitrange_button,2,1)
        layout.addWidget(self.velocityfit_button,2,2)
        self.velocityfitrange_button.setEnabled(False)
        self.velocityfit_button.setEnabled(False)
        QtCore.QObject.connect(self.activateVelocity,
                               QtCore.SIGNAL("clicked()"),
                               self.activateVelocityClicked
                               )
        
        QtCore.QObject.connect(self.velocityfit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.velocityFitClicked
                              )

        QtCore.QObject.connect(self.velocityfitrange_button,
                              QtCore.SIGNAL("clicked()"),
                              self.velocityFitRangeClicked
                              )
        self.pulsefile = self.mainwindow.pulseextractor.pulsefile
        
    def calculate(self):
        pulses = self.mainwindow.pulses
        if pulses is None:
            return
        flighttime = self.trigger.trigger(pulses,upperchannel=self.upper_channel,lowerchannel=self.lower_channel)
        if flighttime != None and flighttime > 0:
            #velocity = (self.channel_distance/((10**(-9))*flighttime))/C #flighttime is in ns, return in fractions of C
            self.logger.info("measured flighttime %s" %flighttime.__repr__())
            self.times.append(flighttime)

    #FIXME: we should not name this update since update is already a member
    def update(self):
        self.velocityfitrange_button.setEnabled(True)    
        self.velocityfit_button.setEnabled(True)
        self.findChild(VelocityCanvas,QtCore.QString("velocity_plot")).update_plot(self.times)
        self.times = []

    def velocityFitRangeClicked(self):
        """
        fit the muon velocity histogram
        """
        config_dialog = FitRangeConfigDialog(upperlim = (0.,60.,self.fitrange[1]), lowerlim = (-1.,60.,self.fitrange[0]), dimension = 'ns')
        rv = config_dialog.exec_()
        if rv == 1:
            upper_limit  = config_dialog.findChild(QtGui.QDoubleSpinBox,QtCore.QString("upper_limit")).value()
            lower_limit  = config_dialog.findChild(QtGui.QDoubleSpinBox,QtCore.QString("lower_limit")).value()
            self.fitrange = (lower_limit,upper_limit)

    def velocityFitClicked(self):
        """
        fit the muon velocity histogram
        """
        self.logger.debug("Using fitrange of %s" %self.fitrange.__repr__())
        fitresults = gaussian_fit(bincontent=n.asarray(self.velocitycanvas.heights),binning = self.binning, fitrange = self.fitrange)
        if not fitresults is None:
            self.velocitycanvas.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])


    def activateVelocityClicked(self):
        """
        Perform extra actions when the checkbox is clicked
        """
        if not self.active:
            config_dialog = VelocityConfigDialog()
            rv = config_dialog.exec_()
            if rv == 1:
                self.activateVelocity.setChecked(True)

                for chan,ch_label in enumerate(["0","1","2","3"]):
                    if config_dialog.findChild(QtGui.QRadioButton,QtCore.QString("uppercheckbox_" + ch_label )).isChecked():
                        self.upper_channel = chan + 1 # ch index is shifted
                        
                for chan,ch_label in enumerate(["0","1","2","3"]):
                    if config_dialog.findChild(QtGui.QRadioButton,QtCore.QString("lowercheckbox_" + ch_label )).isChecked():
                        self.lower_channel = chan + 1 #
            
                self.logger.info("Switching off decay measurement if running!")
                if self.parentWidget().parentWidget().decaywidget.active:
                    self.parentWidget().parentWidget().decaywidget.activateMuondecayClicked()
                self.active = True
                self.parentWidget().parentWidget().parentWidget().daq.put("CE")
                self.parentWidget().parentWidget().ratewidget.startClicked()
                if not self.pulsefile:
                    self.mainwindow.pulsefilename = os.path.join(self.mainwindow.DATAPATH,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(self.mainwindow.date.tm_year,self.mainwindow.date.tm_mon,self.mainwindow.date.tm_mday,self.mainwindow.date.tm_hour,self.mainwindow.date.tm_min,self.mainwindow.date.tm_sec,"P",self.mainwindow.opts.user[0],self.mainwindow.opts.user[1]))
                    self.mainwindow.pulse_mes_start = self.mainwindow.now
                    self.mainwindow.pulseextractor.pulsefile = open(self.mainwindow.pulsefilename,'w')


            else:
                self.activateVelocity.setChecked(False)
                self.active = False
        else:
            self.activateVelocity.setChecked(False)            
            self.active = False
            if not self.pulsefile:
                self.mainwindow.pulsefilename = ''
                self.mainwindow.pulse_mes_start = False
                if self.mainwindow.pulseextractor.pulsefile:
                    self.mainwindow.pulseextractor.pulsefile.close()
                self.mainwindow.pulseextractor.pulsefile = False

            self.mainwindow.tabwidget.ratewidget.stopClicked()  

class DecayWidget(QtGui.QWidget):
    
    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent) 
        self.logger = logger
        self.mufit_button = QtGui.QPushButton(tr('MainWindow', 'Fit!'))
        self.mainwindow = self.parentWidget()        
        self.mufit_button.setEnabled(False)
        self.decayfitrange_button = QtGui.QPushButton(tr('MainWindow', 'Fit Range')) 
        self.decayfitrange_button.setEnabled(False)
        self.lifetime_monitor = LifetimeCanvas(self,logger)
        self.minsinglepulsewidth = 0
        self.maxsinglepulsewidth = 100000 #inf
        self.mindoublepulsewidth = 0
        self.maxdoublepulsewidth = 100000 #inf
        self.muondecaycounter    = 0
        self.lastdecaytime       = 'None'
        self.pulsefile = self.parentWidget().pulseextractor.pulsefile
            
        self.singlepulsechannel  = 0
        self.doublepulsechannel  = 1
        self.vetopulsechannel    = 2 
        self.decay_mintime       = 0
        self.active              = False
        self.trigger             = DecayTriggerThorough(logger)
        self.decay               = []
        self.mu_file             = open("/dev/null","w") 
        self.dec_mes_start       = None
        self.previous_coinc_time_03 = "00"
        self.previous_coinc_time_02 = "0A"
        self.binning = (0,10,21)
        self.fitrange = (1.5,10.) # ignore first bin because of afterpulses, 
                                  # see https://github.com/achim1/muonic/issues/39 

        QtCore.QObject.connect(self.mufit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.mufitClicked
                              )
        QtCore.QObject.connect(self.decayfitrange_button,
                              QtCore.SIGNAL("clicked()"),
                              self.decayFitRangeClicked
                              )

        ntb1 = NavigationToolbar(self.lifetime_monitor, self)

        # activate Muondecay mode with a checkbox
        self.activateMuondecay = QtGui.QCheckBox(self)
        self.activateMuondecay.setObjectName("activate_mudecay")
        self.activateMuondecay.setText(tr("Dialog", "Check for Decayed Muons", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateMuondecay,
                              QtCore.SIGNAL("clicked()"),
                              self.activateMuondecayClicked
                              )
        displayMuons                 = QtGui.QLabel(self)
        displayMuons.setObjectName("muoncounter")
        lastDecay                    = QtGui.QLabel(self)
        lastDecay.setObjectName("lastdecay")
 
        decay_tab = QtGui.QGridLayout(self)
        decay_tab.addWidget(self.activateMuondecay,0,0)
        decay_tab.addWidget(displayMuons,1,0)
        decay_tab.addWidget(lastDecay,2,0)
        decay_tab.addWidget(self.lifetime_monitor,3,0,1,2)
        decay_tab.addWidget(ntb1,4,0)
        decay_tab.addWidget(self.mufit_button,4,2)
        decay_tab.addWidget(self.decayfitrange_button,4,1)
        self.findChild(QtGui.QLabel,QtCore.QString("muoncounter")).setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.findChild(QtGui.QLabel,QtCore.QString("lastdecay")).setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
        #self.decaywidget = self.widget(1)

    def calculate(self):
        pulses = self.mainwindow.pulses
        #single_channel = self.singlepulsechannel, double_channel = self.doublepulsechannel, veto_channel = self.vetopulsechannel,mindecaytime = self.decay_mintime,minsinglepulsewidth = minsinglepulsewidth,maxsinglepulsewidth = maxsinglepulsewidth, mindoublepulsewidth = mindoublepulsewidth, maxdoublepulsewidth = maxdoublepulsewidth):
        decay =  self.trigger.trigger(pulses,single_channel = self.singlepulsechannel,double_channel = self.doublepulsechannel, veto_channel = self.vetopulsechannel, mindecaytime= self.decay_mintime,minsinglepulsewidth = self.minsinglepulsewidth,maxsinglepulsewidth = self.maxsinglepulsewidth, mindoublepulsewidth = self.mindoublepulsewidth, maxdoublepulsewidth = self.maxdoublepulsewidth )
        if decay != None:
            when = time.asctime()
            self.decay.append((decay/1000,when))
            #devide by 1000 to get microseconds
            
            self.logger.info('We have found a decaying muon with a decaytime of %f at %s' %(decay,when)) 
            self.muondecaycounter += 1
            self.lastdecaytime = when
      
    def mufitClicked(self):
        """
        fit the muon decay histogram
        """
        fitresults = fit(bincontent=n.asarray(self.lifetime_monitor.heights),binning = self.binning, fitrange = self.fitrange)
        if not fitresults is None:
            self.lifetime_monitor.show_fit(fitresults[0],fitresults[1],\
                                           fitresults[2],fitresults[3],\
                                           fitresults[4],fitresults[5],\
                                           fitresults[6],fitresults[7])

    def update(self):
        if not self.decay:
            return

        self.mufit_button.setEnabled(True)
        self.decayfitrange_button.setEnabled(True)

        decay_times =  [decay_time[0] for decay_time in self.decay]
        self.lifetime_monitor.update_plot(decay_times)
        self.findChild(QtGui.QLabel,QtCore.QString("muoncounter")).setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.findChild(QtGui.QLabel,QtCore.QString("lastdecay")).setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
        for muondecay in self.decay:
            #muondecay = self.decay[0]
            muondecay_time = muondecay[1].replace(' ','_')
            self.mu_file.write('Decay ')
            self.mu_file.write(muondecay_time.__repr__() + ' ')
            self.mu_file.write(muondecay[0].__repr__())
            self.mu_file.write('\n')
            self.decay = []


    def decayFitRangeClicked(self):
        """
        fit the muon decay histogram
        """
        config_dialog = FitRangeConfigDialog(upperlim = (0.,10.,self.fitrange[1]), lowerlim = (-1.,10.,self.fitrange[0]), dimension = 'microsecond')
        rv = config_dialog.exec_()
        if rv == 1:
            upper_limit  = config_dialog.findChild(QtGui.QDoubleSpinBox,QtCore.QString("upper_limit")).value()
            lower_limit  = config_dialog.findChild(QtGui.QDoubleSpinBox,QtCore.QString("lower_limit")).value()
            self.fitrange = (lower_limit,upper_limit)

    def activateMuondecayClicked(self):
        """
        What should be done if we are looking for mu-decays?
        """
 
        now = datetime.datetime.now()
        #if not self.mainwindow.mudecaymode:
        if not self.active:
                self.activateMuondecay.setChecked(False)
                # launch the settings window
                config_window = DecayConfigDialog()
                rv = config_window.exec_()
                if rv == 1:
                    self.activateMuondecay.setChecked(True)
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
                    self.decay_mintime   = int(config_window.mintime.value())
                    if config_window.findChild(QtGui.QGroupBox,QtCore.QString("pulsewidthgroupbox")).isChecked():
                        self.minsinglepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("minsinglepulsewidth")).value())
                        self.maxsinglepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("maxsinglepulsewidth")).value())
                        self.mindoublepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("mindoublepulsewidth")).value())
                        self.maxdoublepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("maxdoublepulsewidth")).value())
                    
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
                    self.logger.info("Switching off velocity measurement if running!")
                    if self.parentWidget().parentWidget().velocitywidget.active:
                        self.parentWidget().parentWidget().velocitywidget.activateVelocityClicked()

                    self.logger.warn("We now activate the Muondecay mode!\n All other Coincidence/Veto settings will be overriden!")

                    self.logger.warning("Changing gate width and enabeling pulses") 
                    self.logger.info("Looking for single pulse in Channel %i" %(self.singlepulsechannel - 1))
                    self.logger.info("Looking for double pulse in Channel %i" %(self.doublepulsechannel - 1 ))
                    self.logger.info("Using veto pulses in Channel %i"        %(self.vetopulsechannel - 1 ))

                    self.mu_label = QtGui.QLabel(tr('MainWindow','Muon Decay measurement active!'))
                    self.parentWidget().parentWidget().parentWidget().statusbar.addPermanentWidget(self.mu_label)

                    self.parentWidget().parentWidget().parentWidget().daq.put("DC")

                    self.parentWidget().parentWidget().parentWidget().daq.put("CE") 
                    self.parentWidget().parentWidget().parentWidget().daq.put("WC 03 04")
                    self.parentWidget().parentWidget().parentWidget().daq.put("WC 02 0A")
                  
                    self.mu_file = open(self.parentWidget().parentWidget().parentWidget().decayfilename,'w')        
                    self.dec_mes_start = now
                    #self.decaywidget.findChild("activate_mudecay").setChecked(True)
                    self.active = True
                    #FIXME: is this intentional?
                    #self.parentWidget().parentWidget().ratewidget.startClicked()
                    self.pulsefile = self.mainwindow.pulseextractor.pulsefile
                    if not self.pulsefile:
                        self.mainwindow.pulsefilename = os.path.join(self.mainwindow.DATAPATH,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(self.mainwindow.date.tm_year,self.mainwindow.date.tm_mon,self.mainwindow.date.tm_mday,self.mainwindow.date.tm_hour,self.mainwindow.date.tm_min,self.mainwindow.date.tm_sec,"P",self.mainwindow.opts.user[0],self.mainwindow.opts.user[1]))
                        self.mainwindow.pulse_mes_start = self.mainwindow.now
                        self.mainwindow.pulseextractor.pulsefile = open(self.mainwindow.pulsefilename,'w')

                else:
                    self.activateMuondecay.setChecked(False)
                    self.active = False

        else:
            reset_time = "WC 03 " + self.previous_coinc_time_03
            self.parentWidget().parentWidget().parentWidget().daq.put(reset_time)
            reset_time = "WC 02 " + self.previous_coinc_time_02
            self.parentWidget().parentWidget().parentWidget().daq.put(reset_time)
            self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
            self.parentWidget().parentWidget().parentWidget().statusbar.removeWidget(self.mu_label)
            #self.parentWidget().parentWidget().parentWidget().mudecaymode = False
            mtime = now - self.dec_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days *86400
            self.logger.info("The muon decay measurement was active for %f hours" % mtime)
            newmufilename = self.parentWidget().parentWidget().parentWidget().decayfilename.replace("HOURS",str(mtime))
            shutil.move(self.parentWidget().parentWidget().parentWidget().decayfilename,newmufilename)
            #self.parentWidget().parentWidget().parentWidget().daq.put("CD")
            self.active = False
            self.activateMuondecay.setChecked(False)
            self.parentWidget().parentWidget().ratewidget.stopClicked()            

class DAQWidget(QtGui.QWidget):

    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.mainwindow = self.parentWidget()
        self.write_file      = False
        self.label           = QtGui.QLabel(tr('MainWindow','Command'))
        self.hello_edit      = LineEdit()
        self.hello_button    = QtGui.QPushButton(tr('MainWindow','Send'))
        self.file_button     = QtGui.QPushButton(tr('MainWindow', 'Save RAW-File'))
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
        
        daq_layout = QtGui.QGridLayout(self)
        daq_layout.addWidget(self.text_box,0,0,1, 4)
        daq_layout.addWidget(self.label,1,0)
        daq_layout.addWidget(self.hello_edit,1,1)
        daq_layout.addWidget(self.hello_button,1,2) 
        daq_layout.addWidget(self.file_button,1,2) 
        daq_layout.addWidget(self.periodic_button,1,3)   

    def on_hello_clicked(self):

        """
        send a message to the daq
        """
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.mainwindow.daq.put(str(self.hello_edit.displayText()))
            self.hello_edit.add_hist_item(text)
        self.hello_edit.clear()

    def on_file_clicked(self):
        """
        save the raw daq data to a automatically named file
        """
        self.mainwindow.daq.put("CE")        
        self.outputfile = open(self.mainwindow.rawfilename,"w")
        self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%self.mainwindow.rawfilename))
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
                    self.mainwindow.daq.put(c)
            self.periodic_put = periodic_put
            self.periodic_call_timer = QtCore.QTimer()
            QtCore.QObject.connect(self.periodic_call_timer,
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

    def calculate(self):
        """
        Function that is called via processincoming. It does:
        - starts file writing stuff
        """
        self.text_box.appendPlainText(str(self.mainwindow.daq_msg))
        if self.write_file:
            #self.daq_file.write(self.mainwindow.daq_msg, status = self.mainwindow.statusline)
            self.write_to_file(str(self.mainwindow.daq_msg))

    def write_to_file(self,msg):
        """
        Write the "RAW" file
        :param msg:
        :return:
        """

        try:
            if self.mainwindow.nostatus:
                fields = msg.rstrip("\n").split(" ")
                if ((len(fields) == 16) and (len(fields[0]) == 8)):
                    self.outputfile.write(str(msg)+'\n')
                else:
                    self.logger.debug("Not writing line '%s' to file because it does not contain trigger data" %msg)
            else:
                self.outputfile.write(str(msg)+'\n')

        except ValueError:
            self.logger.warning('Trying to write on closed file, captured!')




class GPSWidget(QtGui.QWidget):

    def __init__(self,logger,parent=None):

        QtGui.QWidget.__init__(self,parent=parent)
        self.active = False
        self.mainwindow = self.parentWidget()
        self.logger = logger
        self.gps_dump = []
        self.read_lines = 13

        self.label           = QtGui.QLabel(tr('MainWindow','GPS Display:'))
        self.refresh_button  = QtGui.QPushButton(tr('MainWindow','Show GPS'))
        self.save_button     = QtGui.QPushButton(tr('MainWindow', 'Save to File'))

        QtCore.QObject.connect(self.refresh_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_refresh_clicked
                              )
        QtCore.QObject.connect(self.save_button,
                                QtCore.SIGNAL("clicked()"),
                                self.on_save_clicked
                                )
        self.text_box = QtGui.QPlainTextEdit()
        self.text_box.setReadOnly(True)
        # only 500 lines history
        self.text_box.document().setMaximumBlockCount(500)
        self.status_label = QtGui.QLabel(tr('MainWindow','Status: '))
        self.time_label = QtGui.QLabel(tr('MainWindow','GPS time: '))
        self.satellites_label = QtGui.QLabel(tr('MainWindow','#Satellites: '))
        self.chksum_label = QtGui.QLabel(tr('MainWindow','Checksum: '))
        self.latitude_label = QtGui.QLabel(tr('MainWindow','Latitude: '))
        self.longitude_label = QtGui.QLabel(tr('MainWindow','Longitude: '))
        self.altitude_label = QtGui.QLabel(tr('MainWindow','Altitude: '))
        self.posfix_label = QtGui.QLabel(tr('MainWindow','PosFix: '))
        self.status_box = QtGui.QLabel(tr('MainWindow',' Not read out'))
        self.time_box = QtGui.QLabel(tr('MainWindow','--'))
        self.satellites_box = QtGui.QLabel(tr('MainWindow','--'))
        self.chksum_box = QtGui.QLabel(tr('MainWindow','--'))
        self.latitude_box = QtGui.QLabel(tr('MainWindow','--'))
        self.longitude_box = QtGui.QLabel(tr('MainWindow','--'))
        self.altitude_box = QtGui.QLabel(tr('MainWindow','--'))
        self.posfix_box = QtGui.QLabel(tr('MainWindow','--'))

        gps_layout = QtGui.QGridLayout(self)
        gps_layout.addWidget(self.label,0,0,1,4)
        gps_layout.addWidget(self.status_label,1,0)
        gps_layout.addWidget(self.time_label,2,0)
        gps_layout.addWidget(self.satellites_label,3,0)
        gps_layout.addWidget(self.chksum_label,4,0)
        gps_layout.addWidget(self.latitude_label,1,2)
        gps_layout.addWidget(self.longitude_label,2,2)
        gps_layout.addWidget(self.altitude_label,3,2)
        gps_layout.addWidget(self.posfix_label,4,2)
        gps_layout.addWidget(self.status_box,1,1)
        gps_layout.addWidget(self.time_box,2,1)
        gps_layout.addWidget(self.satellites_box,3,1)
        gps_layout.addWidget(self.chksum_box,4,1)
        gps_layout.addWidget(self.latitude_box,1,3)
        gps_layout.addWidget(self.longitude_box,2,3)
        gps_layout.addWidget(self.altitude_box,3,3)
        gps_layout.addWidget(self.posfix_box,4,3)
        gps_layout.addWidget(self.text_box,6,0,1,4)
        gps_layout.addWidget(self.refresh_button,7,0,1,4) 
        #gps_layout.addWidget(self.save_button,1,2) 

        if self.active:
            self.logger.info("Activated GPS display.")
            self.on_refresh_clicked()

    def on_refresh_clicked(self):
        """
        Display/refresh the GPS information
        """
        self.refresh_button.setEnabled(False)
        self.gps_dump = [] 
        self.logger.info('Reading GPS.')
        self.mainwindow.processIncoming()
        self.switch_active(True)        
        self.mainwindow.daq.put('DG')
        self.mainwindow.processIncoming()
        #for count in range(self.read_lines):
        #    msg = self.mainwindow.inqueue.get(True)
        #    self.gps_dump.append(msg)
        #self.calculate()
        #self.logger.info('GPS readout done.')

    def on_save_clicked(self):
        """
        Save the GPS data to an extra file
        """
        #self.outputfile = open(self.mainwindow.rawfilename,"w")
        #self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%self.mainwindow.rawfilename))
        #self.write_file = True
        #self.mainwindow.raw_mes_start = datetime.datetime.now()
        #self.mainwindow.statusbar.addPermanentWidget(self.file_label)
        self.text_box.appendPlainText('save to clicked - function out of order')        
        self.logger.info("Saving GPS informations still disabled.")


    def switch_active(self, switch = False):
        """
        Switch the GPS activation status.
        """
        if switch is None:
            if self.active:
                self.active = False
            else:
                self.active = True
        else:
            self.active = switch
        return self.active
    
    def calculate(self):
        """
        Readout the GPS information and display it in the tab.
        """
        if len(self.gps_dump) < self.read_lines:
            self.logger.warning('Error retrieving GPS information.')
            return False
        __satellites = 0
        __status = False
        __gps_time = ''
        __latitude = ''
        __longitude = ''
        __altitude = ''
        __posfix = 0
        __chksum = False
        self.refresh_button.setEnabled(True)
        try:

            if str(self.gps_dump[3]).strip().replace('Status:','').strip() == 'A (valid)':
                self.logger.info('Valid GPS signal: found %i ' %(__satellites))
                __status = True
                __satellites = int(str(self.gps_dump[8]).strip().replace('Sats used:', '').strip())
                __posfix = int(str(self.gps_dump[4]).strip().replace('PosFix#:', '').strip())
                __gps_time = str(self.gps_dump[2]).strip().replace('Date+Time:', '').strip()
                if str(self.gps_dump[12]).strip().replace('ChkSumErr:', '').strip() == '0':
                    __chksum = True
                else:
                    __chksum = False
 
                __altitude = str(self.gps_dump[7]).strip().replace('Altitude:', '').strip()

                __latitude = str(self.gps_dump[5]).strip().replace('Latitude:', '').strip()

                __longitude = str(self.gps_dump[6]).strip().replace('Longitude:', '').strip()

            else:
                __status = False
                self.logger.info('Invalid GPS signal.')

            self.gps_dump = []
        except:
            self.logger.warning('Error evaluating GPS information.')
            self.gps_dump = []
            self.switch_active(False)
            return False

        if __status:
            __status = 'Valid'
        else:
            __status = 'Invalid'
        if __chksum:
            __chksum = 'No Error'
        else:
            __chksum = 'Error'
                    
        self.status_box.setText(str(__status))
        self.time_box.setText(str(__gps_time))
        self.satellites_box.setText(str(__satellites))
        self.chksum_box.setText(str(__chksum))
        self.latitude_box.setText(str(__latitude))
        self.longitude_box.setText(str(__longitude))
        self.altitude_box.setText(str(__altitude))
        self.posfix_box.setText(str(__posfix))

        self.text_box.appendPlainText('********************')
        self.text_box.appendPlainText('STATUS     : %s' %(str(__status)))
        self.text_box.appendPlainText('TIME          : %s' %(str(__gps_time)))
        self.text_box.appendPlainText('Altitude     : %s' %(str(__altitude)))
        self.text_box.appendPlainText('Latitude     : %s' %(str(__latitude)))
        self.text_box.appendPlainText('Longitude  : %s' %(str(__longitude)))
        self.text_box.appendPlainText('Satellites    : %s' %(str(__satellites)))
        self.text_box.appendPlainText('Checksum   : %s' %(str(__chksum)))
        self.text_box.appendPlainText('********************')

        self.switch_active(False)
        return True
