# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QLabel
from subprocess import Popen

from LineEdit import LineEdit
from PeriodicCallDialog import PeriodicCallDialog

from ScalarsCanvas import ScalarsCanvas
#from LifetimeCanvas import LifetimeCanvas
from PulseCanvas import PulseCanvas
#from VelocityCanvas import VelocityCanvas

from muonic.analysis import fit

import muonic.analysis.PulseAnalyzer as pa
import muonic.analysis.get_time as get_time

from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time

# this must be changed, just for getting this somehow to work
ANALYSIS_DIR  = os.path.split(pa.__file__)[0]
GET_NUMBERS   = os.path.join(ANALYSIS_DIR,"get_numbers.py")
MUON_LIFETIME = os.path.join(ANALYSIS_DIR,"muon_lifetime.py")
FIT_LIFETIME  = os.path.join(ANALYSIS_DIR,"fit_lifetime.py")
MUON_VELOCITY = os.path.join(ANALYSIS_DIR,"muon_velocity.py")
FIT_VELOCITY  = os.path.join(ANALYSIS_DIR,"fit_velocity.py")




tr = QtCore.QCoreApplication.translate

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class GTabWidget(QtGui.QWidget):
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
        self.write_file = False
        self.holdplot = False
        self.scalars_result = False 
        self.muondecaycounter = 0
        self.velocitycounter = 0
        self.lastdecaytime = 'None'
        self.lastvelocitytime = 'None'

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
        #tab3 = QtGui.QWidget()
        tab4 = QtGui.QWidget()
        #tab5 = QtGui.QWidget()
        tab6 = QtGui.QWidget()
        tab7 = QtGui.QWidget()
        #tab7.setStyleSheet('color: blue')
        
        p1_vertical = QtGui.QVBoxLayout(tab1)
        p2_vertical = QtGui.QVBoxLayout(tab2)
        #p3_vertical = QtGui.QVBoxLayout(tab3)
        p4_vertical = QtGui.QVBoxLayout(tab4)
        #p5_vertical = QtGui.QVBoxLayout(tab5)
        p6_vertical = QtGui.QVBoxLayout(tab6)
        p7_vertical = QtGui.QVBoxLayout(tab7)
        
        tab_widget.addTab(tab1, "DAQ output")
        tab_widget.addTab(tab2, "Muon Rates")
        #tab_widget.addTab(tab3, "Muon Lifetime")
        tab_widget.addTab(tab4, "PulseAnalyzer")
        #tab_widget.addTab(tab5, "Muon Velocity")
        #tab_widget.setStyleSheet("color: green")
        
        #label = QtCore.QString("<font color=red size=62><b> Hallo </b></font>")
        #label.setStyleSheet('color: red')
        #tab_widget.addTab(tab6, label)
        tab_widget.addTab(tab6, "Muon Lifetime")
        tab_widget.addTab(tab7, "Muon Velocity")
        p1_vertical.addWidget(self.text_box)
        second_widget = QtGui.QWidget()
        h_box = QtGui.QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addWidget(self.hello_edit)
        h_box.addWidget(self.hello_button)
        h_box.addWidget(self.file_button)
        h_box.addWidget(self.periodic_button)
        second_widget.setLayout(h_box)
        p1_vertical.addWidget(second_widget)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tab_widget)
        self.setLayout(vbox)
        
        self.scalars_monitor = ScalarsCanvas(self, self.logger)
        self.pulse_monitor = PulseCanvas(self,self.logger)
        #self.offline_monitor = OfflineCanvas(self,self.logger)

        # buttons for restart/clear the plot     
        self.start_button = QtGui.QPushButton(tr('MainWindow', 'Restart'))
        self.stop_button = QtGui.QPushButton(tr('MainWindow', 'Stop'))

        QtCore.QObject.connect(self.start_button,
                              QtCore.SIGNAL("clicked()"),
                              self.startClicked
                              )

        QtCore.QObject.connect(self.stop_button,
                              QtCore.SIGNAL("clicked()"),
                              self.stopClicked
                              )

        # pack theses widget into the vertical box
        p2_vertical.addWidget(self.scalars_monitor)
        #p2_vertical.addWidget(ntb)

        # instantiate the navigation toolbar
        p2_h_box = QtGui.QHBoxLayout()
        ntb = NavigationToolbar(self.scalars_monitor, self)
        p2_h_box.addWidget(ntb)
        p2_h_box.addWidget(self.start_button)
        p2_h_box.addWidget(self.stop_button)
        p2_second_widget = QtGui.QWidget()
        p2_second_widget.setLayout(p2_h_box)
        p2_vertical.addWidget(p2_second_widget)

        # the pulseanalyzer tab
        ntb3 = NavigationToolbar(self.pulse_monitor, self)
        self.activatePulseanalyzer = QtGui.QCheckBox(self)
        self.activatePulseanalyzer.setText(tr("Dialog", "Show the last triggered pulses \n in the time interval", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activatePulseanalyzer,
                              QtCore.SIGNAL("clicked()"),
                              self.activatePulseanalyzerClicked
                              )
        p4_vertical.addWidget(self.activatePulseanalyzer)
        p4_vertical.addWidget(self.pulse_monitor)
        p4_vertical.addWidget(ntb3)

        #import lines: automatic update of all features
        self.timerEvent(None)
        self.timer = self.startTimer(timewindow*1000)

        
        #LIFETIME ANALYSIS    
        #Define all buttons
        self.activateOffline3 = QtGui.QCheckBox(self)
        self.activateOffline3A = QtGui.QCheckBox(self)
        self.activateOffline4 = QtGui.QCheckBox(self)
        self.activateOffline4A = QtGui.QCheckBox(self)
        self.activateOffline5 = QtGui.QCheckBox(self)
        self.activateOffline5A = QtGui.QCheckBox(self)
        self.activateOffline6 = QtGui.QCheckBox(self)
        self.activateOffline6A = QtGui.QCheckBox(self)
        self.displayOffline7 = QtGui.QLabel(self)
        self.activateOffline8 = QtGui.QLineEdit()
        self.displayOffline = QtGui.QLabel(self)
        self.displayOffline1 = QtGui.QLabel(self)
        self.displayOffline1A = QtGui.QLabel(self)
        self.displayOffline2 = QtGui.QLabel(self)
        
        self.activateOffline13 = QtGui.QCheckBox(self)
        self.activateOffline14 = QtGui.QCheckBox(self)
        self.activateOffline15 = QtGui.QCheckBox(self)
        self.activateOffline16 = QtGui.QCheckBox(self)
        self.activateOffline13Low = QtGui.QCheckBox(self)
        self.activateOffline14Low = QtGui.QCheckBox(self)
        self.activateOffline15Low = QtGui.QCheckBox(self)
        self.activateOffline16Low = QtGui.QCheckBox(self)
        self.displayOffline17 = QtGui.QLabel(self)
        self.activateOffline18 = QtGui.QLineEdit()
        self.displayOffline11 = QtGui.QLabel(self)
        self.displayOffline11Low = QtGui.QLabel(self)
        self.displayOffline21 = QtGui.QLabel(self)
        self.displayOffline12 = QtGui.QLabel(self)
        self.channelDecision = QtGui.QLabel(self)
        self.Binning = QtGui.QLabel(self)
        self.BinningVelo = QtGui.QLabel(self)
        font = QFont('Trebuchet MS, Bold Italic')
        font.setPointSize(13)
        lowerCut = ""
        distance = ""
        self.label0 = QtGui.QLabel()
        self.askDistance = QtGui.QLabel()
        self.label1 = QtGui.QLineEdit()
        self.labelA = QtGui.QLineEdit()
        self.BinningInput = QtGui.QLineEdit()
        self.BinningInput.setMaximumSize(QtCore.QSize(80,24))
        self.BinningInput.setGeometry(QtCore.QRect(150, 80, 91, 20))
        self.BinningInputVelo = QtGui.QLineEdit()
        self.BinningInputVelo.setMaximumSize(QtCore.QSize(80,24))
        self.BinningInputVelo.setGeometry(QtCore.QRect(150, 80, 91, 20))
        self.labelA.setMaximumSize(QtCore.QSize(80,24))
        self.labelA.setGeometry(QtCore.QRect(150, 80, 91, 20))
        self.labelB = QtGui.QLineEdit()
        self.labelB.setMaximumSize(QtCore.QSize(80,24))
        self.labelB.setGeometry(QtCore.QRect(20, 280, 91, 20))
        #self.activateOffline2.setFont(font)
        self.displayOffline1 = QtGui.QLabel(tr('Dialog','Channel(s) detecting a single muon'))
        self.activateOffline3.setText(tr("Dialog", "Channel 0", None, QtGui.QApplication.UnicodeUTF8))
        self.activateOffline4.setText(tr("Dialog", "Channel 1", None, QtGui.QApplication.UnicodeUTF8))
        self.activateOffline5.setText(tr("Dialog", "Channel 2", None, QtGui.QApplication.UnicodeUTF8))
        self.activateOffline6.setText(tr("Dialog", "Channel 3", None, QtGui.QApplication.UnicodeUTF8))
        self.displayOffline1A = QtGui.QLabel(tr('Dialog','Channel(s) with a double pulse'))
        self.activateOffline3A.setText(tr("Dialog", "Channel 0", None, QtGui.QApplication.UnicodeUTF8))
        self.activateOffline4A.setText(tr("Dialog", "Channel 1", None, QtGui.QApplication.UnicodeUTF8))
        self.activateOffline5A.setText(tr("Dialog", "Channel 2", None, QtGui.QApplication.UnicodeUTF8))
        self.activateOffline6A.setText(tr("Dialog", "Channel 3", None, QtGui.QApplication.UnicodeUTF8))
        self.label0 = QtGui.QLabel(tr('Dialog','Lower bound for the lifetime (e.g. 0.2 for 0.2 micro-seconds)'))
        self.labelA.setText(tr("Dialog",""))
        self.activateOffline8.setMaximumSize(QtCore.QSize(250,24))
       
        self.start_buttonStart = QtGui.QPushButton(tr('MainWindow', 'Start analysis'))
        self.start_buttonStart.setMaximumSize (154, 44)
        self.start_buttonStart.setCheckable(True)
        self.start_buttonUpdate = QtGui.QPushButton(tr('MainWindow', 'Update analysis'))
        self.start_buttonUpdate.setMaximumSize (154, 44)
        self.start_buttonUpdate.setCheckable(True)
        self.start_buttonStop = QtGui.QPushButton(tr('MainWindow', 'Change parameter'))
        self.start_buttonStop.setMaximumSize (154, 44)
        self.start_buttonStop.setCheckable(True)
        self.channelDecision = QtGui.QLabel(tr('Dialog','Number of used channels'))
        self.channel1 = QtGui.QPushButton(tr('MainWindow', 'single'))
        self.channel1.setMaximumSize (100, 34)
        self.channel1.setCheckable(True)
        self.channel2 = QtGui.QPushButton(tr('MainWindow', 'two'))
        self.channel2.setMaximumSize (100, 34)
        self.channel2.setCheckable(True)
        self.channel3 = QtGui.QPushButton(tr('MainWindow', 'three'))
        self.channel3.setMaximumSize (100, 34)
        self.channel3.setCheckable(True)
        self.Binning = QtGui.QLabel(tr('Dialog','Number of bins'))
        self.BinningInput.setText(tr("Dialog", ""))
        self.labelA.setText(tr("Dialog",""))
        self.displayOffline7 = QtGui.QLabel(tr('Dialog','Dataset (the current path is /home/muonic/muonic-read-only/data/ ) '))
        self.activateOffline8.setText(tr("Dialog", "", None, QtGui.QApplication.UnicodeUTF8))
        self.lastOffline = QtGui.QLabel(self)
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.lastOffline = QtGui.QLabel(self)
        self.activateOffline8.setMaximumSize(QtCore.QSize(250,24))
      
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        p6_h_box0 = QtGui.QHBoxLayout()
        p6_vertical.addWidget(self.channelDecision)
        p6_h_box0.addWidget(self.channel1)
        p6_h_box0.addWidget(self.channel2)
        p6_h_box0.addWidget(self.channel3)
        p6_second_widget0 = QtGui.QWidget()
        p6_second_widget0.setLayout(p6_h_box0)
        p6_vertical.addWidget(p6_second_widget0)

        p6_vertical.addWidget(self.displayOffline1)
        p6_vertical.addWidget(self.activateOffline3)
        p6_vertical.addWidget(self.activateOffline4)
        p6_vertical.addWidget(self.activateOffline5)
        p6_vertical.addWidget(self.activateOffline6)
        p6_vertical.addWidget(self.displayOffline1A)
        p6_vertical.addWidget(self.activateOffline3A)
        p6_vertical.addWidget(self.activateOffline4A)
        p6_vertical.addWidget(self.activateOffline5A)
        p6_vertical.addWidget(self.activateOffline6A)
        p6_vertical.addWidget(self.label0)
        p6_vertical.addWidget(self.labelA)
        p6_vertical.addWidget(self.Binning)
        p6_vertical.addWidget(self.BinningInput)
        p6_vertical.addWidget(self.displayOffline7)
        p6_vertical.addWidget(self.activateOffline8)
        p6_vertical.addWidget(self.lastOffline)
   
        p6_h_box = QtGui.QHBoxLayout()
        p6_h_box.addWidget(self.start_buttonStart)
        p6_h_box.addWidget(self.start_buttonUpdate)
        p6_second_widget = QtGui.QWidget()
        p6_second_widget.setLayout(p6_h_box)
        p6_vertical.addWidget(p6_second_widget)

         
        QtCore.QObject.connect(self.activateOffline3,
                               QtCore.SIGNAL("clicked()"), 
                               self.activateOfflineClicked
                               )
        
        QtCore.QObject.connect(self.activateOffline4,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
        
        QtCore.QObject.connect(self.activateOffline5,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
            
        QtCore.QObject.connect(self.activateOffline6,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
            
        QtCore.QObject.connect(self.activateOffline3A,
                               QtCore.SIGNAL("clicked()"), 
                               self.activateOfflineClicked
                               )
        
        QtCore.QObject.connect(self.activateOffline4A,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
            
        QtCore.QObject.connect(self.activateOffline5A,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
            
        QtCore.QObject.connect(self.activateOffline6A,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
        
        QtCore.QObject.connect(self.activateOffline8,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
            
        
        
        QtCore.QObject.connect(self.start_buttonStart,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
        
        QtCore.QObject.connect(self.start_buttonUpdate,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked
                               )
    
       #++++++++++++++++++++++++++++++++++++++#    
       ###   leave lifetime measurement   #####
       #++++++++++++++++++++++++++++++++++++++#
       ###   start velocity measurement   #####
       #++++++++++++++++++++++++++++++++++++++#     

        self.askDistance = QtGui.QLabel(tr('Dialog','Distance between upper and lower channel in m (e.g. 0.2 for 0.2 m)'))
        self.labelB.setText(tr("Dialog", ""))
        self.displayOffline11 = QtGui.QLabel(tr('Dialog','Upper channel'))
        self.activateOffline13.setText(tr("Dialog", "Channel 0", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline13,
                               QtCore.SIGNAL("clicked()"), 
                               self.activateOfflineClicked1
                           )
        self.activateOffline14.setText(tr("Dialog", "Channel 1", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline14,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                           )
        self.activateOffline15.setText(tr("Dialog", "Channel 2", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline15,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )
        self.activateOffline16.setText(tr("Dialog", "Channel 3", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline16,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )
    
        self.displayOffline11Low = QtGui.QLabel(tr('Dialog','Lower channel'))
        self.activateOffline13Low.setText(tr("Dialog", "Channel 0", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline13Low,
                               QtCore.SIGNAL("clicked()"), 
                               self.activateOfflineClicked1
                               )
        self.activateOffline14Low.setText(tr("Dialog", "Channel 1", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline14Low,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )
        self.activateOffline15Low.setText(tr("Dialog", "Channel 2", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline15Low,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )
        self.activateOffline16Low.setText(tr("Dialog", "Channel 3", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline16Low,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )

        self.displayOffline17 = QtGui.QLabel(tr('Dialog','Dataset (the current path is /home/muonic/muonic-read-only/data/) '))
        self.activateOffline18.setText(tr("Dialog", "", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateOffline18,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )
        
        self.activateOffline18.setMaximumSize(QtCore.QSize(250,24))

        self.start_buttonStart1 = QtGui.QPushButton(tr('MainWindow', 'Start analysis'))
        self.start_buttonStart1.setMaximumSize (154, 44)
        self.BinningVelo = QtGui.QLabel(tr('Dialog','Number of bins'))
        self.BinningInputVelo.setText(tr("Dialog", ""))
        self.start_buttonUpdate1 = QtGui.QPushButton(tr('MainWindow', 'Update analysis'))
        self.start_buttonUpdate1.setMaximumSize (154, 44)
        self.start_buttonStop1 = QtGui.QPushButton(tr('MainWindow', 'Change parameter'))
        self.start_buttonStop1.setMaximumSize (154, 44)
        self.start_buttonStart1.setCheckable(True)
        self.start_buttonUpdate1.setCheckable(True)
        #self.start_buttonStop1.setCheckable(True)
        
        QtCore.QObject.connect(self.start_buttonStart1,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )

        QtCore.QObject.connect(self.start_buttonUpdate1,
                               QtCore.SIGNAL("clicked()"),
                               self.activateOfflineClicked1
                               )

        self.lastOffline1 = QtGui.QLabel(self)
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        
        p7_vertical.addWidget(self.displayOffline11)
        p7_vertical.addWidget(self.activateOffline13)
        p7_vertical.addWidget(self.activateOffline14)
        p7_vertical.addWidget(self.activateOffline15)
        p7_vertical.addWidget(self.activateOffline16)
        p7_vertical.addWidget(self.displayOffline11Low)
        p7_vertical.addWidget(self.activateOffline13Low)
        p7_vertical.addWidget(self.activateOffline14Low)
        p7_vertical.addWidget(self.activateOffline15Low)
        p7_vertical.addWidget(self.activateOffline16Low)
        p7_vertical.addWidget(self.askDistance)
        p7_vertical.addWidget(self.labelB)
        p7_vertical.addWidget(self.BinningVelo)
        p7_vertical.addWidget(self.BinningInputVelo)
        p7_vertical.addWidget(self.displayOffline17)
        p7_vertical.addWidget(self.activateOffline18)
        p7_vertical.addWidget(self.lastOffline1)
        p7_h_box = QtGui.QHBoxLayout()
        p7_h_box.addWidget(self.start_buttonStart1)
        p7_h_box.addWidget(self.start_buttonUpdate1)
        #p7_h_box.addWidget(self.start_buttonStop1)
        p7_second_widget = QtGui.QWidget()
        p7_second_widget.setLayout(p7_h_box)
        p7_vertical.addWidget(p7_second_widget)



    def activateOfflineClicked(self):
        #self.logger.info("hier der filename: "+self.mainwindow.options.rawfilename)
        #self.outputfile = open(self.mainwindow.options.rawfilename,"r")
        askForString=""
        #dpch0, dpch1, dpch2, dpch3, ch0, ch1, ch2, ch3+++++++++++++++++ 
        ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0,0,0,0,0
        #single channel 0++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline3A.isChecked() and self.channel1.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 1,0,0,0
            askForString="grep ch0micro"
        #single channel 1++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline4A.isChecked()  and self.channel1.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 0,1,0,0
            askForString="grep ch1micro"
        #single channel 2++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline5A.isChecked()  and self.channel1.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 0,0,1,0
            askForString="grep ch2micro"
        #single channel 3++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline6A.isChecked()  and self.channel1.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 0,0,0,1
            askForString="grep ch3micro"
        #two channels 0,1+++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline4.isChecked() and self.activateOffline3A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,1,0,0, 1,0,0,0
            askForString="grep ch0micro"
        if self.activateOffline3.isChecked() and self.activateOffline4A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,0,0,0, 0,1,0,0
            askForString="grep ch1micro"
        #two channels 0,2+++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline5.isChecked() and self.activateOffline3A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,1,0, 1,0,0,0
            askForString="grep ch0micro"
        if self.activateOffline3.isChecked() and self.activateOffline5A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,0,0,0, 0,0,1,0
            askForString="grep ch2micro"
        #two channels 0,3+++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline6.isChecked() and self.activateOffline3A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,1,0, 1,0,0,0
            askForString="grep ch0micro"
        if self.activateOffline3.isChecked() and self.activateOffline6A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,0,0,0, 0,0,1,0
            askForString="grep ch2micro"
        #two channels 1,2+++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline5.isChecked() and self.activateOffline4A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,1,0, 0,1,0,0
            askForString="grep ch1micro"
        if self.activateOffline4.isChecked() and self.activateOffline5A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,1,0,0, 0,0,1,0
            askForString="grep ch2micro"
        #two channels 1,3+++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline6.isChecked() and self.activateOffline4A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,1, 0,1,0,0
            askForString="grep ch1micro"
        if self.activateOffline4.isChecked() and self.activateOffline6A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,1,0,0, 0,0,0,1
            askForString="grep ch3micro"
        #two channels 2,3+++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline6.isChecked() and self.activateOffline5A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,1, 0,0,1,0
            askForString="grep ch2micro"
        if self.activateOffline5.isChecked() and self.activateOffline6A.isChecked()  and self.channel2.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,1,0, 0,0,0,1
            askForString="grep ch3micro"
        #three channels 0,1,2+++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline4.isChecked() and self.activateOffline5.isChecked() and self.activateOffline3A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,1,1,0, 1,0,0,0
            askForString="grep ch0micro"
        if self.activateOffline3.isChecked() and self.activateOffline5.isChecked() and self.activateOffline4A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,0,1,0, 0,1,0,0
            askForString="grep ch1micro"
        if self.activateOffline3.isChecked() and self.activateOffline4.isChecked() and self.activateOffline5A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,1,0,0, 0,0,1,0
            askForString="grep ch2micro"
        #three channels 1,2,3+++++++++++++++++++++++++++++++++++++++++++++++
        if self.activateOffline5.isChecked() and self.activateOffline6.isChecked() and self.activateOffline4A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,1,1, 0,1,0,0
            askForString="grep ch1micro"
        if self.activateOffline4.isChecked() and self.activateOffline6.isChecked() and self.activateOffline5A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,1,0,1, 0,0,1,0
            askForString="grep ch2micro"
        if self.activateOffline4.isChecked() and self.activateOffline5.isChecked() and self.activateOffline6A.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,1,1,0, 0,0,0,1
            askForString="grep ch3micro"
        #two channels both with double pulse 0,1+++++++++++++++++++++++++++++
        if self.activateOffline3A.isChecked() and self.activateOffline4A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 1,1,0,0
            askForString="ls egrep ch0micro | egrep ch1micro"
        #two channels both with double pulse 1,2+++++++++++++++++++++++++++++
        if self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 0,1,1,0
            askForString="ls egrep ch1micro | egrep ch2micro"
        #two channels both with double pulse 2,3+++++++++++++++++++++++++++++
        if self.activateOffline5A.isChecked() and self.activateOffline6A.isChecked()  and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 0,0,1,1
            askForString="ls egrep ch2micro | egrep ch3micro"
        #two channels both with double pulse 0,1 and single 2++++++++++++++++
        if self.activateOffline3A.isChecked() and self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,1,0, 1,1,0,0
            askForString="ls egrep ch0micro | egrep ch1micro"
        #two channels both with double pulse 0,1 and single 3++++++++++++++++
        if self.activateOffline3A.isChecked() and self.activateOffline4A.isChecked() and self.activateOffline6A.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,1, 1,1,0,0
            askForString="ls egrep ch0micro | egrep ch1micro"
        #two channels both with double pulse 1,2 and single 3++++++++++++++++
        if self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.activateOffline6.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,1, 0,1,1,0
            askForString="ls egrep ch1micro | egrep ch2micro"
        #two channels both with double pulse 1,2 and single 0++++++++++++++++
        if self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.activateOffline3.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,0,0,0, 0,1,1,0
            askForString="ls egrep ch1micro | egrep ch2micro"
        #two channels both with double pulse 2,3 and single 1++++++++++++++++
        if self.activateOffline5A.isChecked() and self.activateOffline6A.isChecked() and self.activateOffline4.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,1,0,0, 0,0,1,1
            askForString="ls egrep ch2micro | egrep ch3micro"
        #two channels both with double pulse 2,3 and single 0++++++++++++++++
        if self.activateOffline5A.isChecked() and self.activateOffline6A.isChecked() and self.activateOffline3.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,0,0,0, 0,0,1,1
            askForString="ls egrep ch2micro | egrep ch3micro"
        #three channels with double pulse 0,1,2++++++++++++++++++++++++++++++
        if self.activateOffline3A.isChecked() and self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 1,1,1,0
            askForString="ls egrep ch0micro | egrep ch1micro | egrep ch2micro"
        #three channels with double pulse 1,2,3++++++++++++++++++++++++++++++
        if self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.activateOffline6A.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 0,1,1,1
            askForString="ls egrep ch1micro | egrep ch2micro | egrep ch3micro"
        #three channels with double pulse 0,1,2 and single 3++++++++++++++++
        if self.activateOffline3A.isChecked() and self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.activateOffline6.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,1, 1,1,1,0
            askForString="ls egrep ch0micro | egrep ch1micro | egrep ch2micro"
        #three channels with double pulse 1,2,3 and single 0+++++++++++++++++
        if self.activateOffline3A.isChecked() and self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.activateOffline6.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,0,0,0, 0,1,1,1
            askForString="ls egrep ch1micro | egrep ch2micro | egrep ch3micro"
        #all channels with double pulse 1,2,3,4++++++++++++++++++++++++++++++
        if self.activateOffline3A.isChecked() and self.activateOffline4A.isChecked() and self.activateOffline5A.isChecked() and self.activateOffline6A.isChecked() and self.channel3.isChecked():
            ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 0,0,0,0, 1,1,1,1
            askForString="ls egrep ch0micro | egrep ch1micro | egrep ch2micro | egrep ch3micro"

        ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3 = 1,1,1,1,1,1,1,1


        # catch this if string is empty (?)...
        lowerBound = float(self.labelA.displayText())    
        
        sampleLifetime = self.activateOffline8.displayText()+" "
        self.logger.info("Using the following file %s" %sampleLifetime.__repr__())

        rangeLifetime = float(self.BinningInput.displayText())
        date = time.gmtime()
        
        cmd_string = "python %s %s %i %i %i %i %i %i %i %i | %s > lifetime.tmp && python %s %s > lifetime_to_fit.tmp && python %s %s %i %i" %(MUON_LIFETIME, sampleLifetime, ch0, ch1, ch2, ch3, dpch0, dpch1, dpch2, dpch3, askForString,GET_NUMBERS,os.path.join(os.getcwd(),"lifetime.tmp"),FIT_LIFETIME, os.path.join(os.getcwd(),"lifetime_to_fit.tmp"), lowerBound, rangeLifetime)

        
        # Gordon: "some users are afraid to click the start button, so I implemented an update button as well...."

        if self.start_buttonStart.isChecked():
            self.logger.info("start button!")
            p = Popen(cmd_string, shell=True)
            result = p.communicate()
            self.logger.info("Subprocess returned" + result.__repr__())


        if self.start_buttonUpdate.isChecked():
            self.logger.info("Update successful!")
            p = Popen(cmd_string, shell=True)
            result = p.communicate()
            self.logger.info("Subprocess returned" + result.__repr__())
                    
 
    def activateOfflineClicked1(self):

        #self.outputfile = open(self.mainwindow.options.rawfilename,"r")
        distanceChannels =  float(self.labelB.displayText())
        sampleVelocity = self.activateOffline18.displayText() 
        rangeVelocity =  float(self.BinningInputVelo.displayText())
        av,bv,cv,dv = 0,0,0,0

        #0,1
        if self.activateOffline13.isChecked() and self.activateOffline14Low.isChecked():
            av,bv,cv,dv =  1, 2, 0, 0
        #0,2
        if self.activateOffline13.isChecked() and self.activateOffline15Low.isChecked():
            av,bv,cv,dv =  1, 0, 2, 0
        #0,3
        if self.activateOffline13.isChecked() and self.activateOffline16Low.isChecked():
            av,bv,cv,dv =  1, 0, 0, 2
        #1,2
        if self.activateOffline14.isChecked() and self.activateOffline15Low.isChecked() :
            av,bv,cv,dv =  0, 1, 2, 0
        #1,3
        if self.activateOffline14.isChecked() and self.activateOffline16Low.isChecked() :
            av,bv,cv,dv =  0, 1, 0, 2
        #2,3
        if self.activateOffline15.isChecked() and self.activateOffline16Low.isChecked() :
            av,bv,cv,dv =  0, 0, 1, 2
        #1,0
        if self.activateOffline13Low.isChecked() and self.activateOffline14.isChecked() :
            av,bv,cv,dv =  2, 1, 0, 0
        #2,0
        if self.activateOffline13Low.isChecked() and self.activateOffline15.isChecked() :
            av,bv,cv,dv =  2, 0, 1, 0
        #3,0
        if self.activateOffline13Low.isChecked() and self.activateOffline16.isChecked() :
            av,bv,cv,dv =  2, 0, 0, 1
        #2,1
        if self.activateOffline14Low.isChecked() and self.activateOffline15.isChecked() :
            av,bv,cv,dv =  0, 2, 1, 0
        #3,1
        if self.activateOffline14Low.isChecked() and self.activateOffline16.isChecked() :
            av,bv,cv,dv =  0, 2, 0, 1
        #3,2
        if self.activateOffline15Low.isChecked() and self.activateOffline16.isChecked() :
            av,bv,cv,dv =  0, 0, 2, 1
            
        #av,bv,cv,dv = 1,2,0,0

        cmd_string = "python %s %s %i %i %i %i %i | grep meterperseconds > velocity.tmp && python %s %s > velocity_to_fit.tmp && python %s %s %i" %(MUON_VELOCITY,sampleVelocity,av,bv,cv,dv,distanceChannels,GET_NUMBERS,os.path.join(os.getcwd(),"velocity.tmp"),FIT_VELOCITY,os.path.join(os.getcwd(),"velocity_to_fit.tmp"),rangeVelocity)
        if self.start_buttonStart1.isChecked():
            self.logger.info("start button!")
            p = Popen(cmd_string,shell =True)
            result = p.communicate()
            self.logger.info("Subprocess returned" + result.__repr__())
            #p= Popen("python /home/muonic/muonic-read-only/muonic/analysis/muon_velocity.py %s %i %i %i %i %i | grep meterperseconds > velocity.tmp && python /home/muonic/muonic-read-only/muonic/analysis/get_numbers.py /home/muonic/muonic-read-only/velocity.tmp > velocity_to_fit.tmp && python /home/muonic/muonic-read-only/muonic/analysis/fit_velocity.py /home/muonic/muonic-read-only/velocity_to_fit.tmp %i" %(sampleVelocity,av,bv,cv,dv,distanceChannels,rangeVelocity), shell=True)
                    
        if self.start_buttonUpdate1.isChecked():
            self.logger.info("Update successful!")
            p = Popen(cmd_string,shell=True) #FIXME: we should not execute anything through the shell, because it might be different on different systems!
            result = p.communicate()
            self.logger.info("Subprocess returned" + result.__repr__())

            #p= Popen("python /home/muonic/muonic-read-only/muonic/analysis/muon_velocity.py %s %i %i %i %i %i | grep meterperseconds > velocity.tmp && python /home/muonic/muonic-read-only/muonic/analysis/get_numbers.py /home/muonic/muonic-read-only/velocity.tmp > velocity_to_fit.tmp && python /home/muonic/muonic-read-only/muonic/analysis/fit_velocity.py /home/muonic/muonic-read-only/velocity_to_fit.tmp %i " %(sampleVelocity, av,bv,cv,dv,distanceChannels,rangeVelocity), shell=True)

        

    #general commands
    def startClicked(self): 
        self.logger.debug("Restart Button Clicked")
        self.holdplot = False
        self.scalars_monitor.reset()
        #self.scalars_monitor.update_plot((0,0,0,0,0,5,0,0,0,0,0))
        
    def stopClicked(self):
        self.holdplot = True
   

    def activatePulseanalyzerClicked(self):

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
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.mainwindow.outqueue.put(str(self.hello_edit.displayText()))
            self.hello_edit.add_hist_item(text)
        self.hello_edit.clear()

    def on_file_clicked(self):
        
        self.outputfile = open(self.mainwindow.options.rawfilename,"w")
        self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%self.mainwindow.options.rawfilename))
        self.write_file = True
        self.mainwindow.options.raw_mes_start = datetime.datetime.now()
        self.mainwindow.statusbar.addPermanentWidget(self.file_label)

    def on_periodic_clicked(self):
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
            self.timer = QtCore.QTimer()
            QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.periodic_put)
            self.periodic_put()
            self.timer.start(period)
            self.periodic_status_label = QtGui.QLabel(tr('MainWindow','%s every %s sec'%(command,period/1000)))
            self.mainwindow.statusbar.addPermanentWidget(self.periodic_status_label)
        else:
            try:
                self.timer.stop()
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

        
        if self.mainwindow.options.showpulses:

            if self.mainwindow.pulses != None:
                self.pulse_monitor.update_plot(self.mainwindow.pulses)


