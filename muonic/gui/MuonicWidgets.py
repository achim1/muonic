"""
Provide the different widgets
"""

from PyQt4 import QtGui
from PyQt4 import QtCore

from LineEdit import LineEdit
from MuonicPlotCanvases import ScalarsCanvas,LifetimeCanvas,PulseCanvas,VelocityCanvas,PulseWidthCanvas
from MuonicData import MuonicRawFile, MuonicRateFile, MuonicDecayFile, MuonicPulseFile
from MuonicData import MuonicRate
from MuonicDialogs import DecayConfigDialog,PeriodicCallDialog, VelocityConfigDialog, FitRangeConfigDialog
from ..analysis.fit import main as fit
from ..analysis.fit import gaussian_fit
from ..analysis.PulseAnalyzer import VelocityTrigger,DecayTriggerThorough
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import time

qt_translate = QtCore.QCoreApplication.translate

class RateWidget(QtGui.QWidget):
    """
    Display rate plot and average rates and total scalers
    """
    def __init__(self,logger,parent = None):
        QtGui.QWidget.__init__(self,parent = parent)
        self.mainwindow = self.parentWidget()
        self.logger           = logger
        self.active           = False
        self.scalers_result   = False
        self.MAXLENGTH = 40
        self.scalers_monitor  = ScalarsCanvas(self, logger, self.MAXLENGTH)
        self.rate_mes_start   = datetime.datetime.now()
        self.previous_ch_counts = {"ch0" : 0 ,"ch1" : 0,"ch2" : 0,"ch3": 0}
        self.ch_counts = {"ch0" : 0 ,"ch1" : 0,"ch2" : 0,"ch3": 0}
        self.timewindow = 0
        self.now = datetime.datetime.now()
        self.lastscalerquery = 0
        self.thisscalerquery = time.time()
        self.do_not_show_trigger = False

        self.start_button = QtGui.QPushButton(qt_translate('MainWindow', 'Start run'))
        self.stop_button = QtGui.QPushButton(qt_translate('MainWindow', 'Stop run'))
        self.label_mean_rates = QtGui.QLabel(qt_translate('MainWindow','mean rates:'))
        self.label_total_scalers = QtGui.QLabel(qt_translate('MainWindow','total scalers:'))
        self.label_started = QtGui.QLabel(qt_translate('MainWindow','started:'))
        self.rates = dict()
        self.rates['rates'] = MuonicRate([0,0,0,0,0])
        self.rates['rates_buffer'] = dict()
        for ch in ['ch0','ch1','ch2','ch3','l_time','trigger']:
            self.rates['rates_buffer'][ch] = []
        self.rates['label_ch0'] = QtGui.QLabel(qt_translate('MainWindow','channel 0:'))
        self.table = QtGui.QTableWidget(5,2,self)
        self.table.setColumnWidth(0,85)
        self.table.setColumnWidth(1,60)
        self.table.setHorizontalHeaderLabels(["rate [Hz]","scaler"])
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
        self.general_info['label_date'] = QtGui.QLabel(qt_translate('MainWindow',''))
        self.general_info['edit_date'] = QtGui.QLineEdit(self)
        self.general_info['edit_date'].setReadOnly(True)
        self.general_info['edit_date'].setDisabled(True)
        self.general_info['label_daq_time'] = QtGui.QLabel(qt_translate('MainWindow','daq time:'))
        self.general_info['edit_daq_time'] = QtGui.QLineEdit(self)
        self.general_info['edit_daq_time'].setReadOnly(True)
        self.general_info['edit_daq_time'].setDisabled(True)
        self.general_info['label_max_rate'] = QtGui.QLabel(qt_translate('MainWindow','max rate:'))
        self.general_info['edit_max_rate'] = QtGui.QLineEdit(self)
        self.general_info['edit_max_rate'].setReadOnly(True)
        self.general_info['edit_max_rate'].setDisabled(True)
        self.general_info['max_rate'] = 0
        self.general_info['min_rate'] = 0

        #self.pulses_to_show = None
        self.filename = os.path.join(self.mainwindow.settings.muonic_setting('data_path'),self.mainwindow.settings.muonic_setting('muonic_filenames') %(self.mainwindow.now.strftime('%Y-%m-%d_%H-%M-%S'),"R",self.mainwindow.opts.user[0],self.mainwindow.opts.user[1]) )
        self.rate_file = MuonicRateFile(self.filename, self.logger)
        # always write the rate plot data
        self.rate_file_write = False

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

    def calculate(self):
        """
        Calculate the values shown in the rate widget and writes values to a file. Started via Processincoming in Mainwindow
        """
        time_window = self.mainwindow.thisscalarquery - self.mainwindow.lastscalarquery
        self.rates['rates'].rates((self.mainwindow.scalars_diff_ch0/time_window,self.mainwindow.scalars_diff_ch1/time_window,self.mainwindow.scalars_diff_ch2/time_window,self.mainwindow.scalars_diff_ch3/time_window, self.mainwindow.scalars_diff_trigger/time_window, time_window,self.mainwindow.scalars_diff_ch0,self.mainwindow.scalars_diff_ch1, self.mainwindow.scalars_diff_ch2, self.mainwindow.scalars_diff_ch3, self.mainwindow.scalars_diff_trigger)

        self.timewindow += self.rates['rates'][5]

        for ch in enumerate(['ch0','ch1','ch2','ch3','trigger']):
            self.rates['rates_buffer'][ch[1]].append(self.rates['rates'][ch[0]])
            self.scalers['scalers_buffer'][ch[1]] += self.rates['rates'][ch[0]+6]

        self.rates['rates_buffer']['l_time'].append(self.timewindow)
        for ch in ['ch0','ch1','ch2','ch3','trigger','l_time']:
            if len(self.rates['rates_buffer'][ch]) > self.MAXLENGTH:
                self.rates['rates_buffer'][ch].remove(self.rates['rates_buffer'][ch][0])

        max_rate = max( max(self.rates['rates_buffer']['ch0']), max(self.rates['rates_buffer']['ch1']), max(self.rates['rates_buffer']['ch2']), 
                   max(self.rates['rates_buffer']['ch3']))
        min_rate = min( min(self.rates['rates_buffer']['ch0']), min(self.rates['rates_buffer']['ch1']), min(self.rates['rates_buffer']['ch2']), 
                       min(self.rates['rates_buffer']['ch3']))
        if max_rate > self.general_info['max_rate']:
            self.general_info['max_rate'] = max_rate
        if min_rate < self.general_info['min_rate']:
            self.general_info['max_rate'] = min_rate

        # file'ish part:
        if self.rate_file_write:
            
            self.rate_file.write('%f %f %f %f %f %f %f %f %f %f' % (self.mainwindow.scalars_diff_ch0, self.mainwindow.scalars_diff_ch1, self.mainwindow.scalars_diff_ch2, self.mainwindow.scalars_diff_ch3, self.mainwindow.scalars_diff_ch0/time_window,self.mainwindow.scalars_diff_ch1/time_window,self.mainwindow.scalars_diff_ch2/time_window,self.mainwindow.scalars_diff_ch3/time_window,self.mainwindow.scalars_diff_trigger/time_window,time_window))
 

    def update(self):
        """
        Updates the values shown in the rate widget.
        """
        if self.active:
            self.general_info['edit_daq_time'].setText('%.2f s' %(self.timewindow))
            self.general_info['edit_max_rate'].setText('%.2f Hz' %(self.general_info['max_rate']))
            for i in range(4):
                _edit = 'edit_ch'+str(i)
                _ch = 'ch'+str(i)
                if self.mainwindow.channelcheckbox[i]:
                    if self.timewindow != 0:
                        self.rates[_edit].setText('%.2f' %(self.scalers['scalers_buffer'][_ch]/self.timewindow))
                    self.scalers[_edit].setText('%.2f' %(self.scalers['scalers_buffer'][_ch]))
                else:
                    self.rates[_edit].setText('off')
                    self.scalers[_edit].setText('off')

            if self.do_not_show_trigger:
                self.rates['edit_trigger'].setText('off')
                self.scalers['edit_trigger'].setText('off')
            else:
                if self.timewindow != 0:
                    self.rates['edit_trigger'].setText('%.2f' %(self.scalers['scalers_buffer']['trigger']/self.timewindow))
                self.scalers['edit_trigger'].setText('%.2f' %(self.scalers['scalers_buffer']['trigger']))

            self.scalers_monitor.update_plot(self.rates['rates'],self.do_not_show_trigger,self.mainwindow.channelcheckbox[0],self.mainwindow.channelcheckbox[1],self.mainwindow.channelcheckbox[2],self.mainwindow.channelcheckbox[3])
      
    def is_active(self):
        """
        Returns a bool whether the rate measurment is currently running or not.
        """
        return self.active

    def startClicked(self):
        """
        start the rate measurement and write a file, leaves comment about the started data taking in the rate file.
        """
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.mainwindow.query_daq_for_scalars()
        self.mainwindow.daq.put('DC')
        time.sleep(0.2)
        self.table.setEnabled(True)

        self.logger.debug("Start Button Clicked")
        
        self.timewindow = 0
        
        for ch in ['ch0','ch1','ch2','ch3','trigger']:
            self.scalers['scalers_buffer'][ch] = 0
        for ch in ['ch0','ch1','ch2','ch3','l_time','trigger']:
            self.rates['rates_buffer'][ch] = []
        
        measurement = 'rate'
        if self.mainwindow.tabwidget.decaywidget.is_active():
            measurement = 'decay'
        if self.mainwindow.tabwidget.velocitywidget.is_active():
            measurement = 'velocity'
        self.rate_file.start_run(measurement)
        self.active = True
        self.rate_file_write = True
        self.now = datetime.datetime.now()
        
        for i in range(4):
            _edit = 'edit_ch'+str(i)            
            if not self.mainwindow.channelcheckbox[i]:
                self.rates[_edit].setText('off')
                self.scalers[_edit].setText('off')
        self.general_info['edit_date'].setDisabled(False)
        self.general_info['edit_daq_time'].setDisabled(False)
        self.general_info['edit_max_rate'].setDisabled(False)
        self.general_info['edit_date'].setText(self.now.strftime('%d.%m.%Y %H:%M:%S'))
        self.general_info['edit_daq_time'].setText('%.2f' %(self.timewindow))
        self.general_info['edit_max_rate'].setText('%.2f' %(self.general_info['max_rate']))
        if self.do_not_show_trigger:
            self.rates['edit_trigger'].setText('off')
            self.scalers['edit_trigger'].setText('off')

        self.scalers_monitor.reset()
        #time.sleep(3)
        #self.start_button.setEnabled(True)
        
    def stopClicked(self):
        """
        Stops data taking. Stops rate widgets calculations and stops to write in the rate file. Leaves a comment about the stopped writing in the rate file.
        """
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.table.setEnabled(False)

        self.general_info['edit_date'].setDisabled(True)
        self.general_info['edit_daq_time'].setDisabled(True)
        self.general_info['edit_max_rate'].setDisabled(True)

        self.active = False
        self.rate_file_write = False
        self.rate_file.stop_run()

    def close(self):
        """
        Closes the tab properly.
        """
        self.stopClicked()
        self.rate_file.close()
        QtGui.QWidget.close(self)

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
        self.activatePulseanalyzer.setText(qt_translate("Dialog", "Show Oscilloscope and Pulse Width Distribution", None, QtGui.QApplication.UnicodeUTF8))
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
        self.pulsewidths = []
        self.active = False

    def is_active(self):
        """
        Returns a bool whether the pulseanlyzer measurment is currently running or not.
        """
        return self.active

    def calculate(self):
        """
        Calculate the pulse widths, take in consideration that the falling edge might be missing.
        """
        if self.mainwindow.pulses is None:
            return None
        self.pulses = self.mainwindow.pulses
        # pulsewidths changed because falling edge can be None.
        # pulsewidths = [fe - le for chan in pulses[1:] for le,fe in chan]
        pulsewidths = []
        for chan in self.mainwindow.pulses[1:]:
            for le, fe in chan:
                if fe is not None:
                    pulsewidths.append(fe - le)
                else:
                    pulsewidths.append(0.)
        self.pulsewidths += pulsewidths
        
    def update(self):
        """
        Updates the pulse width histogram and oscilloscope.
        """
        self.pulsecanvas.update_plot(self.pulses)
        self.pulsewidthcanvas.update_plot(self.pulsewidths)
        self.pulsewidths = []

    def activatePulseanalyzerClicked(self):
        """
        Activates the pulse analyszer widget measurement: oscilloscope and pulse width histogram is recorded and measured.
        """
        if not self.is_active():
            self.pulsefile = self.mainwindow.pulseextractor.pulsefile
            self.activatePulseanalyzer.setChecked(True)
            self.active = True
            self.logger.debug("Switching on Pulseanalyzer.")
            self.mainwindow.daq.put("CE")

            self.mainwindow.daq.put('CE')
            if not self.pulsefile:
                self.mainwindow.writepulses = True
                self.mainwindow.pulseextractor.pulsefile = MuonicPulseFile(self.mainwindow.pulsefilename, self.logger)

        else:
            self.logger.debug("Switching off Pulseanalyzer.")
            self.activatePulseanalyzer.setChecked(False)            
            self.active = False

            if not self.pulsefile:
                self.mainwindow.writepulses = False
                if self.mainwindow.pulseextractor.pulsefile:
                    self.mainwindow.pulseextractor.pulsefile.close()
                self.mainwindow.pulseextractor.pulsefile = False

    def close(self):
        """
        Closes the tab properly.
        """
        if self.mainwindow.pulseextractor.pulsefile:
            self.mainwindow.pulseextractor.pulsefile.close()
            self.mainwindow.pulseextractor.pulsefile = False
        self.mainwindow.writepulses = False
        self.active = False
        QtGui.QWidget.close(self)


class StatusWidget(QtGui.QWidget):
    """
    Provide a widget which shows the status informations of the DAQ and the muonic software
    """
    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.mainwindow = self.parentWidget()
        self.logger = logger

        self.active = True

        self.muonic_stats = dict()
        self.daq_stats = dict()

        self.daq_stats['thresholds'] = list()
        self.daq_stats['active_channel'] = list()
        for cnt in range(4):
            self.daq_stats['thresholds'].append('not set yet - click on Refresh.')
            self.daq_stats['active_channel'].append(None)
        self.daq_stats['coincidences'] = 'not set yet - click on Refresh.'
        self.daq_stats['coincidence_timewindow'] = 'not set yet - click on Refresh.'
        self.daq_stats['veto'] = 'not set yet - click on Refresh.'

        self.muonic_stats['start_params'] = 'not set yet - click on Refresh.'
        self.muonic_stats['refreshtime'] = 'not set yet - click on Refresh.'
        self.muonic_stats['open_files'] = 'not set yet - click on Refresh.'

        self.label_daq = QtGui.QLabel(qt_translate('MainWindow','Status of the DAQ card:'))
        self.label_thresholds = QtGui.QLabel(qt_translate('MainWindow','Threshold:'))
        self.label_active_channels = QtGui.QLabel(qt_translate('MainWindow','Active channels:'))
        self.label_coincidences = QtGui.QLabel(qt_translate('MainWindow','Trigger condition:'))
        self.label_coincidence_timewindow = QtGui.QLabel(qt_translate('MainWindow','Time window for trigger condition:'))
        self.label_veto = QtGui.QLabel(qt_translate('MainWindow','Veto:'))
        self.thresholds = []
        self.active_channel = []
        for cnt in range(4):
            self.thresholds.append(QtGui.QLineEdit(self))
            self.thresholds[cnt].setReadOnly(True)
            self.thresholds[cnt].setText(self.daq_stats['thresholds'][cnt])
            self.thresholds[cnt].setDisabled(True)
            self.active_channel.append(QtGui.QLineEdit(self))
            self.active_channel[cnt].setText('Channel 0')
            self.active_channel[cnt].setReadOnly(True)
            self.active_channel[cnt].setEnabled(False)
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

        self.label_muonic = QtGui.QLabel(qt_translate('MainWindow','Status of Muonic:'))
        self.label_measurements = QtGui.QLabel(qt_translate('MainWindow','Active measurements:'))
        self.label_start_params = QtGui.QLabel(qt_translate('MainWindow','Start parameter:'))
        self.label_refreshtime = QtGui.QLabel(qt_translate('MainWindow','Measurement intervals:'))
        self.label_open_files = QtGui.QLabel(qt_translate('MainWindow','Currently opened files:'))
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

        self.refresh_button  = QtGui.QPushButton(qt_translate('MainWindow','Refresh'))
        self.refresh_button.setDisabled(True)
        QtCore.QObject.connect(self.refresh_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_refresh_clicked
                              )

        self.save_button  = QtGui.QPushButton(qt_translate('MainWindow','Save to file'))
        QtCore.QObject.connect(self.save_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_save_clicked
                              )

        status_layout = QtGui.QGridLayout(self)
        status_layout.addWidget(self.label_daq,0,0)
        status_layout.addWidget(self.label_active_channels,1,0)
        for i in range(4):
            status_layout.addWidget(self.active_channel[i],1,i+1)
            status_layout.addWidget(self.thresholds[i],2,i+1)
        status_layout.addWidget(self.label_thresholds,2,0)
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
        Saves the status information - currently disabled!
        """
        self.logger.debug("Saving status information to file.")
        self.logger.warning('Currently not available!')

    def is_active(self):
        """
        Returns a bool whether the status widget is active or not
        """
        return self.active
        
    def update(self):
        """
        Fill the status information in the widget.
        """
        self.logger.debug("Refreshing status infos")
        if (self.mainwindow.tabwidget.statuswidget.isVisible()):
            self.muonic_stats['start_params'] = str(self.mainwindow.opts).replace('{', '').replace('}','')
            self.muonic_stats['refreshtime'] = str(self.mainwindow.timewindow)+ ' s'
            
            for i in range(4):
                self.daq_stats['thresholds'][i] = str(self.mainwindow.threshold_ch[i])+ ' mV'
            if not self.mainwindow.vetocheckbox[3]:
                self.daq_stats['veto'] = 'no veto set'
            else:
                if self.mainwindow.vetocheckbox[0]:
                    self.daq_stats['veto'] = 'veto with channel 0'
                if self.mainwindow.vetocheckbox[1]:
                    self.daq_stats['veto'] = 'veto with channel 1'
                if self.mainwindow.vetocheckbox[2]:
                    self.daq_stats['veto'] = 'veto with channel 2'

            self.daq_stats['coincidence_timewindow'] = str(self.mainwindow.coincidence_time) + ' ns'

            for i in range(4):
                self.daq_stats['active_channel'][i] = self.mainwindow.channelcheckbox[i]
            if self.mainwindow.coincidencecheckbox[0]:
                self.daq_stats['coincidences'] = 'Single Coincidence.'
            elif self.mainwindow.coincidencecheckbox[1]:
                self.daq_stats['coincidences'] = 'Twofold Coincidence.'
            elif self.mainwindow.coincidencecheckbox[2]:
                self.daq_stats['coincidences'] = 'Threefold Coincidence.'
            elif self.mainwindow.coincidencecheckbox[3]:
                self.daq_stats['coincidences'] = 'Fourfold Coincidence.'

            for cnt in range(4):
                self.thresholds[cnt].setDisabled(False)                
                self.thresholds[cnt].setText(self.daq_stats['thresholds'][cnt])
                self.thresholds[cnt].setEnabled(True)
                self.active_channel[cnt].setEnabled(self.daq_stats['active_channel'][cnt])
            self.coincidences.setText(self.daq_stats['coincidences'])
            self.coincidences.setEnabled(True)
            self.coincidence_timewindow.setText(self.daq_stats['coincidence_timewindow'])
            self.coincidence_timewindow.setEnabled(True)
            self.veto.setText(self.daq_stats['veto'])
            self.veto.setEnabled(True)
            
            self.muonic_stats['open_files'] = str(self.mainwindow.tabwidget.ratewidget.filename)
            if self.mainwindow.tabwidget.daqwidget.write_daq_file:
                self.muonic_stats['open_files'] += ', ' + self.mainwindow.tabwidget.daqwidget.rawfilename
            if self.mainwindow.tabwidget.decaywidget.is_active():
                self.muonic_stats['open_files'] += ', ' + self.mainwindow.tabwidget.decaywidget.decayfilename
            if self.mainwindow.writepulses:
                self.muonic_stats['open_files'] += ', ' + self.mainwindow.pulsefilename
            self.start_params.setPlainText(self.muonic_stats['start_params'])
            self.start_params.setEnabled(True)
            self.refreshtime.setText(self.muonic_stats['refreshtime'])
            self.refreshtime.setEnabled(True)
            self.open_files.setPlainText(self.muonic_stats['open_files'])
            self.open_files.setEnabled(True)
            measurements = ''
            if self.mainwindow.tabwidget.ratewidget.is_active():
                measurements = 'Muon Rates'
            if self.mainwindow.tabwidget.decaywidget.is_active():
                measurements += ', Muon Decay'
            if self.mainwindow.tabwidget.velocitywidget.is_active():
                measurements += ', Muon Velocity'
            if self.mainwindow.tabwidget.pulseanalyzerwidget.is_active():
                measurements += ', Pulse Analyzer'
            self.measurements.setText(measurements)
            self.measurements.setEnabled(True)
            self.start_params.setEnabled(True)

            self.active = False
        else:
            self.logger.debug("Status informations widget not active - ignoring update call.")
        self.refresh_button.setDisabled(False)
        self.active = False

    def close(self):
        """
        Closes the tab properly.
        """
        self.active = False
        QtGui.QWidget.close(self)


class VelocityWidget(QtGui.QWidget):
    """
    Provides a widget, with which one can measure time differences dt between two scintillator plates, thus one can measure the velocity of muons.
    """
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
        self.activateVelocity.setText(qt_translate("Dialog", "Measure Flight Time", None, QtGui.QApplication.UnicodeUTF8))
        self.activateVelocity.setObjectName("activate_velocity")
        self.velocityfit_button = QtGui.QPushButton(qt_translate('MainWindow', 'Fit!')) 
        self.velocityfitrange_button = QtGui.QPushButton(qt_translate('MainWindow', 'Fit Range')) 
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
        
    def calculate(self):
        """
        Calculates the flight time and discards dt s below 0 and which are none (might happen if trigger time window was exceeded).
        """
        if self.mainwindow.pulses is None:
            return None
        pulses = self.mainwindow.pulses
        flighttime = self.trigger.trigger(pulses,upperchannel=self.upper_channel,lowerchannel=self.lower_channel)
        if flighttime != None and flighttime > 0:
            self.logger.info("measured flighttime %s" %flighttime.__repr__())
            self.times.append(flighttime)
        
    def update(self):
        """
        Updates the velocity plot canvas
        """
        self.velocityfitrange_button.setEnabled(True)    
        self.velocityfit_button.setEnabled(True)
        self.findChild(VelocityCanvas,QtCore.QString("velocity_plot")).update_plot(self.times)
        self.times = []

    def is_active(self):
        """
        Returns a bool whether the velocity measurement is active or not
        """
        return self.active
    
    def velocityFitRangeClicked(self):
        """
        Change the fit range of the dt fit
        """
        config_dialog = FitRangeConfigDialog(upperlim = (0.,60.,self.fitrange[1]), lowerlim = (-1.,60.,self.fitrange[0]), dimension = 'ns')
        rv = config_dialog.exec_()
        if rv == 1:
            upper_limit  = config_dialog.findChild(QtGui.QDoubleSpinBox,QtCore.QString("upper_limit")).value()
            lower_limit  = config_dialog.findChild(QtGui.QDoubleSpinBox,QtCore.QString("lower_limit")).value()
            self.fitrange = (lower_limit,upper_limit)

    def velocityFitClicked(self):
        """
        fit the muon time of flight histogram
        """
        fitresults = gaussian_fit(bincontent=self.velocitycanvas.heights,binning = self.binning, fitrange = self.fitrange)
        if not fitresults is None:
            self.velocitycanvas.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])


    def activateVelocityClicked(self):
        """
        Activate the flight time measurement. Perform extra actions when the checkbox is clicked.
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
                if self.mainwindow.tabwidget.decaywidget.is_active():
                    self.mainwindow.tabwidget.decaywidget.activateMuondecayClicked()
                self.active = True
                self.mainwindow.daq.put("CE")
                self.mainwindow.tabwidget.ratewidget.startClicked()
            else:
                self.activateVelocity.setChecked(False)
                self.active = False
        else:
            self.activateVelocity.setChecked(False)            
            self.active = False
            self.mainwindow.tabwidget.ratewidget.stopClicked()            

    def close(self):
        """
        Closes the tab properly.
        """
        if self.active:
            self.activateVelocityClicked()
        QtGui.QWidget.close(self)


class DecayWidget(QtGui.QWidget):
    """
    Widget which can be used to measure the muon decay. Checks for an single pulse in the upper scintillator, followed by a double pulse in the second scinti from the electron and vetos it with the 3rd scintillator plate.
    """
    
    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent) 
        self.logger = logger
        self.mainwindow = self.parentWidget()
        self.mufit_button = QtGui.QPushButton(qt_translate('MainWindow', 'Fit!'))
        self.mufit_button.setEnabled(False)
        self.decayfitrange_button = QtGui.QPushButton(qt_translate('MainWindow', 'Fit Range')) 
        self.decayfitrange_button.setEnabled(False)
        self.lifetime_monitor = LifetimeCanvas(self,logger)
        self.minsinglepulsewidth = 0
        self.maxsinglepulsewidth = 100000 #inf
        self.mindoublepulsewidth = 0
        self.maxdoublepulsewidth = 100000 #inf
        self.muondecaycounter    = 0
        self.lastdecaytime       = 'None'
            
        self.singlepulsechannel  = 0
        self.doublepulsechannel  = 1
        self.vetopulsechannel    = 2 
        self.decay_mintime       = 0
        self.active              = False
        self.trigger             = DecayTriggerThorough(logger)
        self.decay               = []
        self.decay_file          = None
        self.previous_coinc_time = "100"
        self.binning = (0,10,21)
        self.fitrange = (self.binning[0],self.binning[1])

        QtCore.QObject.connect(self.mufit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.mufitClicked
                              )
        QtCore.QObject.connect(self.decayfitrange_button,
                              QtCore.SIGNAL("clicked()"),
                              self.decayFitRangeClicked
                              )

        ntb1 = NavigationToolbar(self.lifetime_monitor, self)

        self.activateMuondecay = QtGui.QCheckBox(self)
        self.activateMuondecay.setObjectName("activate_mudecay")
        self.activateMuondecay.setText(qt_translate("Dialog", "Check for Decayed Muons", None, QtGui.QApplication.UnicodeUTF8))
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
        self.findChild(QtGui.QLabel,QtCore.QString("muoncounter")).setText(qt_translate("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.findChild(QtGui.QLabel,QtCore.QString("lastdecay")).setText(qt_translate("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
        
    def is_active(self):
        """
        Returns a bool whether the decay measurment is active or not.
        """
        return self.active
     
    def calculate(self):
        """
        Calculates the time between the first pulse and the last pulse. This can be fitted with an exp decay to get the muon life time.
        """
        pulses = self.mainwindow.pulses
        if pulses is None:
            return None
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
        Fit the muon decay histogram
        """
        fitresults = fit(bincontent=self.lifetime_monitor.heights,binning = self.binning, fitrange = self.fitrange)
        if not fitresults is None:
            self.lifetime_monitor.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])

    def update(self):
        """
        Update the muon decay plot and widget.
        """
        if self.decay:
            self.mufit_button.setEnabled(True)
            self.decayfitrange_button.setEnabled(True)

            decay_times =  [decay_time[0] for decay_time in self.decay]
            self.lifetime_monitor.update_plot(decay_times)
            self.findChild(QtGui.QLabel,QtCore.QString("muoncounter")).setText(qt_translate("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
            self.findChild(QtGui.QLabel,QtCore.QString("lastdecay")).setText(qt_translate("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
            for muondecay in self.decay:
                self.decay_file.write(muondecay)
                self.decay = []
        else:
            pass

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
        if not self.is_active():
            self.activateMuondecay.setChecked(False)
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
                if self.mainwindow.tabwidget.velocitywidget.is_active():
                    self.mainwindow.tabwidget.velocitywidget.activateVelocityClicked()

                self.logger.warn("We now activate the Muondecay mode!\n All other Coincidence/Veto settings will be overriden!")

                self.logger.warning("Changing gate width and enabeling pulses") 
                self.logger.info("Looking for single pulse in Channel %i" %(self.singlepulsechannel - 1))
                self.logger.info("Looking for double pulse in Channel %i" %(self.doublepulsechannel - 1 ))
                self.logger.info("Using veto pulses in Channel %i"        %(self.vetopulsechannel - 1 ))

                self.mu_label = QtGui.QLabel(qt_translate('MainWindow','Muon Decay measurement active!'))
                self.mainwindow.statusbar.addPermanentWidget(self.mu_label)

                self.mainwindow.daq.put("DC")
                self.previous_coinc_time = self.mainwindow.coincidence_time

                self.mainwindow.daq.put("CE") 
                self.mainwindow.daq.put("WC 03 04")
                self.mainwindow.daq.put("WC 02 0A")
              
                self.decayfilename = os.path.join(self.mainwindow.settings.muonic_setting('data_path'),self.mainwindow.settings.muonic_setting('muonic_filenames') %(self.mainwindow.now.strftime('%Y-%m-%d_%H-%M-%S'),"L",self.mainwindow.opts.user[0],self.mainwindow.opts.user[1]) )
                self.decay_file = MuonicDecayFile(self.decayfilename, self.logger)
                self.decay_file.start_run()
                self.dec_mes_start = now                
                #self.decaywidget.findChild("activate_mudecay").setChecked(True)
                self.active = True
                self.mainwindow.tabwidget.ratewidget.startClicked()            

            else:
                self.activateMuondecay.setChecked(False)
                self.active = False

        else:
            reset_time = bin(int(self.previous_coinc_time/10)).replace('0b','').zfill(16)
            _03 = format(int(reset_time[0:8],2),'x').zfill(2)
            _02 = format(int(reset_time[8:16],2),'x').zfill(2)
            tmp_msg = 'WC 03 '+str(_03)
            self.mainwindow.daq.put(tmp_msg)
            tmp_msg = 'WC 02 '+str(_02)
            self.mainwindow.daq.put(tmp_msg)
            self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
            self.mainwindow.statusbar.removeWidget(self.mu_label)
            self.decay_file.stop_run()
            self.decay_file.close()
            mtime = now - self.dec_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days *86400
            self.logger.info("The muon decay measurement was active for %f hours" % mtime)
            self.active = False
            self.activateMuondecay.setChecked(False)
            self.mainwindow.tabwidget.ratewidget.stopClicked()            

    def close(self):
        """
        Closes the tab properly.
        """
        if self.active:
            self.activateMuondecayClicked()
        QtGui.QWidget.close(self)


class DAQWidget(QtGui.QWidget):
    """
    Widget which provides an interface to communicate via DAQ commands with the DAQ and to read the direct DAQ output.
    """
    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.mainwindow = self.parentWidget()
        self.logger = logger
        
        self.write_daq_file  = False
        self.daq_file        = None
        self.rawfilename = os.path.join(self.mainwindow.settings.muonic_setting('data_path'),self.mainwindow.settings.muonic_setting('muonic_filenames') %(self.mainwindow.now.strftime('%Y-%m-%d_%H-%M-%S'),"RAW",self.mainwindow.opts.user[0],self.mainwindow.opts.user[1]) )
        self.label           = QtGui.QLabel(qt_translate('MainWindow','Command'))
        self.message_edit    = LineEdit()
        self.send_button     = QtGui.QPushButton(qt_translate('MainWindow','Send'))
        self.file_button     = QtGui.QPushButton(qt_translate('MainWindow', 'Save RAW-File'))
        self.periodic_button = QtGui.QPushButton(qt_translate('MainWindow', 'Periodic Call'))
        QtCore.QObject.connect(self.send_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_send_clicked
                              )
        QtCore.QObject.connect(self.message_edit,
                              QtCore.SIGNAL("returnPressed()"),
                              self.on_send_clicked
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
        self.text_box.document().setMaximumBlockCount(500)
        
        daq_layout = QtGui.QGridLayout(self)
        daq_layout.addWidget(self.text_box,0,0,1, 4)
        daq_layout.addWidget(self.label,1,0)
        daq_layout.addWidget(self.message_edit,1,1)
        daq_layout.addWidget(self.send_button,1,2) 
        daq_layout.addWidget(self.file_button,1,2) 
        daq_layout.addWidget(self.periodic_button,1,3)   

    def on_send_clicked(self):
        """
        send a message to the daq
        """
        text = str(self.message_edit.displayText())
        if len(text) > 0:
            self.mainwindow.daq.put(str(self.message_edit.displayText()))
            self.message_edit.add_hist_item(text)
        self.message_edit.clear()

    def on_file_clicked(self):
        """
        save the raw daq data to a automatically named file
        """
        self.mainwindow.daq.put("CE") 
        self.daq_file = MuonicRawFile(self.rawfilename, self.logger)
        self.file_label = QtGui.QLabel(qt_translate('MainWindow','Writing to %s'%self.rawfilename))
        self.write_daq_file = True
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
            self.periodic_status_label = QtGui.QLabel(qt_translate('MainWindow','%s every %s sec'%(command,period/1000)))
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
        self.text_box.appendPlainText(str(self.mainwindow.daq_msg.read()))
        if self.write_daq_file:
            self.daq_file.write(self.mainwindow.daq_msg.read(), status = self.mainwindow.statusline)

    def close(self):
        """
        Closes the tab properly.
        """
        if self.write_daq_file:
            self.write_daq_file = False
            self.daq_file.close()
        QtGui.QWidget.close(self)


class GPSWidget(QtGui.QWidget):
    """
    Provides a widget to show the GPS informations from DAQ
    """
    def __init__(self,logger,parent=None):

        QtGui.QWidget.__init__(self,parent=parent)
        self.active = False
        self.mainwindow = self.parentWidget()
        self.logger = logger
        self.gps_dump = []
        self.read_lines = 13

        self.label           = QtGui.QLabel(qt_translate('MainWindow','GPS Display:'))
        self.refresh_button  = QtGui.QPushButton(qt_translate('MainWindow','Show GPS'))
        self.save_button     = QtGui.QPushButton(qt_translate('MainWindow', 'Save to File'))

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
        self.text_box.document().setMaximumBlockCount(500)
        self.status_label = QtGui.QLabel(qt_translate('MainWindow','Status: '))
        self.time_label = QtGui.QLabel(qt_translate('MainWindow','GPS time: '))
        self.satellites_label = QtGui.QLabel(qt_translate('MainWindow','#Satellites: '))
        self.chksum_label = QtGui.QLabel(qt_translate('MainWindow','Checksum: '))
        self.latitude_label = QtGui.QLabel(qt_translate('MainWindow','Latitude: '))
        self.longitude_label = QtGui.QLabel(qt_translate('MainWindow','Longitude: '))
        self.altitude_label = QtGui.QLabel(qt_translate('MainWindow','Altitude: '))
        self.posfix_label = QtGui.QLabel(qt_translate('MainWindow','PosFix: '))
        self.status_box = QtGui.QLabel(qt_translate('MainWindow',' Not read out'))
        self.time_box = QtGui.QLabel(qt_translate('MainWindow','--'))
        self.satellites_box = QtGui.QLabel(qt_translate('MainWindow','--'))
        self.chksum_box = QtGui.QLabel(qt_translate('MainWindow','--'))
        self.latitude_box = QtGui.QLabel(qt_translate('MainWindow','--'))
        self.longitude_box = QtGui.QLabel(qt_translate('MainWindow','--'))
        self.altitude_box = QtGui.QLabel(qt_translate('MainWindow','--'))
        self.posfix_box = QtGui.QLabel(qt_translate('MainWindow','--'))

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
        self.switch_active(True)        
        self.mainwindow.processIncoming()
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
        #self.write_file = True
        #self.mainwindow.statusbar.addPermanentWidget(self.file_label)
        self.text_box.appendPlainText('save to clicked - function out of order')        
        self.logger.info("Saving GPS informations still disabled.")

    def is_active(self):
        """
        Is the GPS readout activated? return bool
        """
        return self.active
    
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
        return self.is_active()
    
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

    def close(self):
        """
        Closes the tab properly.
        """
        QtGui.QWidget.close(self)
