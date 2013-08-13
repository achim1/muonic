"""
Provide the dialog fields for user interaction
"""


from PyQt4 import QtCore, QtGui

class MuonicDialog(QtGui.QDialog):
    """
    Base class of all muonic dialogs
    """
    
    def __init__(self):
        pass
    
    def createButtonBox(self,objectname="buttonBox",leftoffset=80,topoffset=900):
        """
        Create a custom button for cancel/apply
        """
        
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setGeometry(QtCore.QRect(leftoffset, topoffset, 300, 32))
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        buttonBox.setObjectName(objectname)
        return buttonBox

    def createCheckGroupBox(self,label="Single Pulse",objectname="singlecheckbox",radio=False,leftoffset=20,setchecked=None,checkable=False, checkable_set=False,itemlabels=["Chan0","Chan1","Chan2","Chan3"]):
        """
        Create a group of choices
        """

        groupBox = QtGui.QGroupBox(label)
        groupBox.setCheckable(checkable)
        groupBox.setChecked(checkable_set)
        groupBox.setObjectName(objectname)

        checkitems = []
        for index,label in enumerate(itemlabels):
            
            if radio:
                check = QtGui.QRadioButton(self)
            else:
                check = QtGui.QCheckBox(self)
                
            check.setGeometry(QtCore.QRect(leftoffset, 40 + index*40, 119, 28))
            check.setObjectName(objectname + "_" + str(index))
            check.setText(label) 
            checkitems.append(check)        
 
        if setchecked is not None:
            for index in setchecked:
                checkitems[index].setChecked(True)
                
        #for channel in enumerate(checkitems):
        #    if checkitem == channel[0]:
        #        channel[1].setChecked(True)
            
        vbox = QtGui.QVBoxLayout()
        for check in checkitems:
            vbox.addWidget(check)
        
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        return groupBox

class DecayConfigDialog(MuonicDialog):
    """
    Settings for the muondecay
    """
    
    def __init__(self, *args):

        QtGui.QDialog.__init__(self,*args)

        # size of window etc..
        self.setObjectName("Configure")
        #self.resize(480, 360)
        self.setModal(True)
        self.setWindowTitle("Muon Decay Configuration")  

        grid = QtGui.QGridLayout()
        grid.addWidget(self.createCheckGroupBox(radio=True,label="Single Pulse",objectname = "singlecheckbox",leftoffset=20, setchecked=[1]), 0, 0)
        grid.addWidget(self.createCheckGroupBox(radio=True,label="Double Pulse",objectname = "doublecheckbox",leftoffset=180,setchecked=[2]), 0, 1)
        grid.addWidget(self.createCheckGroupBox(radio=True,label="Veto Pulse",objectname = "vetocheckbox",leftoffset=300,    setchecked=[3]), 0, 2)
        
        
        # add line edits to perform cuts on the events
        self.mintime = QtGui.QSpinBox()
        self.mintime_label = QtGui.QLabel("Minimum time between\n two pulses (in ns)")
        self.mintime.setMaximum(2000)
        self.mintime.setValue(400)
        #self.mintime.setValidator(QtGui.QIntValidator())
        self.mintime.setToolTip(QtCore.QString("Reject events where the double pulses are too close together"))
        #self.mintime.setMaxLength(5)
        #self.mintime.setMaximumWidth(60)
        grid.addWidget(self.mintime,2,0)
        grid.addWidget(self.mintime_label,2,1)


        pulsewidthgroupBox = QtGui.QGroupBox("Set conditions on pulse width")
        pulsewidthgroupBox.setCheckable(True)
        pulsewidthgroupBox.setChecked(False)
        pulsewidthgroupBox.setObjectName("pulsewidthgroupbox")      
        pulsewidthlayout = QtGui.QGridLayout(pulsewidthgroupBox)
        
        self.minsinglepulsewidth = QtGui.QSpinBox()
        self.minsinglepulsewidth.setObjectName("minsinglepulsewidth")
        self.minsinglepulsewidth_label = QtGui.QLabel("Min mu pulse width")
        self.minsinglepulsewidth.setSuffix(' ns')
        self.minsinglepulsewidth.setValue(10)
        self.minsinglepulsewidth.setToolTip(QtCore.QString("Define a MINIMUM width for the MUON pulse"))
        self.minsinglepulsewidth.setMaximum(11000)
        pulsewidthlayout.addWidget(self.minsinglepulsewidth,0,0)
        pulsewidthlayout.addWidget(self.minsinglepulsewidth_label,0,1)
 
        self.maxsinglepulsewidth = QtGui.QSpinBox()
        self.maxsinglepulsewidth.setObjectName("maxsinglepulsewidth")
        self.maxsinglepulsewidth_label = QtGui.QLabel("Max mu pulse width")
        self.maxsinglepulsewidth.setSuffix(' ns')
        self.maxsinglepulsewidth.setMaximum(11000)
        self.maxsinglepulsewidth.setValue(300)
        self.maxsinglepulsewidth.setToolTip(QtCore.QString("Define a MAXIMUM width for the MUON pulse"))
        pulsewidthlayout.addWidget(self.maxsinglepulsewidth,1,0)
        pulsewidthlayout.addWidget(self.maxsinglepulsewidth_label,1,1)

        self.mindoublepulsewidth = QtGui.QSpinBox()
        self.mindoublepulsewidth.setObjectName("mindoublepulsewidth")
        self.mindoublepulsewidth_label = QtGui.QLabel("Min e pulse width")
        self.mindoublepulsewidth.setSuffix(' ns')
        self.maxsinglepulsewidth.setMaximum(11000)
        self.mindoublepulsewidth.setValue(5)
        self.mindoublepulsewidth.setToolTip(QtCore.QString("Define a MINIMUM width for the ELECTRON pulse"))
        #self.mintime.setMaximumWidth(60)
        pulsewidthlayout.addWidget(self.mindoublepulsewidth,2,0)
        pulsewidthlayout.addWidget(self.mindoublepulsewidth_label,2,1)

        self.maxdoublepulsewidth = QtGui.QSpinBox()
        self.maxdoublepulsewidth.setObjectName("maxdoublepulsewidth")
        self.maxdoublepulsewidth_label = QtGui.QLabel("Max e pulse width")
        self.maxdoublepulsewidth.setSuffix(' ns')
        self.maxsinglepulsewidth.setMaximum(11000)
        self.maxdoublepulsewidth.setValue(300)
        self.maxdoublepulsewidth.setToolTip(QtCore.QString("Define a MINIMUM width for the ELECTRON pulse"))
        #self.mintime.setMaximumWidth(60)
        pulsewidthlayout.addWidget(self.maxdoublepulsewidth,3,0)
        pulsewidthlayout.addWidget(self.maxdoublepulsewidth_label,3,1)

        grid.addWidget(pulsewidthgroupBox,3,0,1,3)
        self.buttonBox = self.createButtonBox(leftoffset=200)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        grid.addWidget(self.buttonBox,4,2)
        self.setLayout(grid)
        self.show()
class FitRangeConfigDialog(MuonicDialog):

        def __init__(self, upperlim = None, lowerlim = None, dimension = '', *args):
            QtGui.QDialog.__init__(self,*args)

            #self.resize(480, 360)
            self.setModal(True)
            self.setWindowTitle("Fit Range Configuration")  

            grid = QtGui.QGridLayout()
            
            lower_label    = QtGui.QLabel("Lower limit for the fit range: ") 
            lower = QtGui.QDoubleSpinBox()
            lower.setDecimals(2)
            lower.setSingleStep(0.01)
            lower.setObjectName("lower_limit")
            lower.setSuffix(' %s' %(str(dimension)))
            if lowerlim:
                lower.setMaximum(lowerlim[1])
                lower.setMinimum(lowerlim[0])
                lower.setValue(lowerlim[2])
            grid.addWidget(lower_label,0,0)
            grid.addWidget(lower,0,1)
           
            upper_label    = QtGui.QLabel("Upper limit for the fit range: ") 
            upper = QtGui.QDoubleSpinBox()
            upper.setDecimals(2)
            upper.setSingleStep(0.01)
            upper.setObjectName("upper_limit")
            upper.setSuffix(' %s' %(str(dimension)))            
            if upperlim:
                upper.setMaximum(upperlim[1])
                upper.setMinimum(upperlim[0])
                upper.setValue(upperlim[2])
            grid.addWidget(upper_label,1,0)
            grid.addWidget(upper,1,1)
           
            self.buttonBox = self.createButtonBox(leftoffset=200)
            QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
            QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
            QtCore.QMetaObject.connectSlotsByName(self)
            
            grid.addWidget(self.buttonBox,2,0,2,0)
            self.setLayout(grid)
            self.show()

class VelocityConfigDialog(MuonicDialog):

    def __init__(self, *args):

        QtGui.QDialog.__init__(self,*args)

        #self.resize(480, 360)
        self.setModal(True)
        self.setWindowTitle("Muon Velocity Configuration")  

        grid = QtGui.QGridLayout()
        grid.addWidget(self.createCheckGroupBox(radio=True,label="Upper Channel",objectname = "uppercheckbox",leftoffset=20, setchecked=[0]), 0, 0)
        grid.addWidget(self.createCheckGroupBox(radio=True,label="Lower Channel",objectname = "lowercheckbox",leftoffset=180,setchecked=[1]), 0, 1)
       
        self.buttonBox = self.createButtonBox(leftoffset=200)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        
        grid.addWidget(self.buttonBox,1,1)
        self.setLayout(grid)
        self.show()

class PeriodicCallDialog(MuonicDialog):
    """
    Issue a command periodically
    """

    def __init__(self, *args):
        QtGui.QDialog.__init__(self,*args)
        self.setModal(True)
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QLineEdit()
        self.time_box = QtGui.QSpinBox()
        self.time_box.setMaximum(600)
        self.time_box.setMinimum(1)
        self.time_box.setSingleStep(1)
        self.command_label = QtGui.QLabel("Command")
        self.interval_label = QtGui.QLabel("Interval")
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.v_box.addWidget(self.command_label)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.interval_label)
        self.v_box.addWidget(self.time_box)
        self.v_box.addWidget(self.button_box)
        
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('rejected()'),
                              self.reject)
        windowtitle = QtCore.QString("PeridicCall")
 
        self.setWindowTitle(windowtitle)
        self.show()


class ThresholdDialog(MuonicDialog):
    """
    Set the Thresholds
    """

    def __init__(self,thr0,thr1,thr2,thr3, *args):

        QtGui.QDialog.__init__(self,*args)

        #dimension = QtCore.QSize()

        #self.resize(260, 260)
        #self.resize(dimension)     
        self.setModal(True)

        self.v_box = QtGui.QVBoxLayout()

        for ch,thr in enumerate([thr0,thr1,thr2,thr3]):
            ch = str(ch)
            thres = QtGui.QSpinBox()
            thres.setMaximum(1000)
            thres.setObjectName("thr_ch_" + ch)
            thres.setValue(int(thr))
            thres.setSuffix(' mV')
            label = QtGui.QLabel("Channel " + ch )
            self.v_box.addWidget(label)
            self.v_box.addWidget(thres)
                        
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )

        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('rejected()'),
                              self.reject)

        windowtitle = QtCore.QString("Thresholds")
        
        self.setWindowTitle(windowtitle)
        self.adjustSize()
        self.show()

class ConfigDialog(MuonicDialog):
    """
    Set Channel configuration
    """
    
    def __init__(self,channelcheckbox_0 = True,channelcheckbox_1 = True,channelcheckbox_2 = True,channelcheckbox_3 = True,coincidencecheckbox_0 = True,coincidencecheckbox_1 = False,coincidencecheckbox_2 = False,coincidencecheckbox_3 = False,vetocheckbox = False,vetocheckbox_0 = False,vetocheckbox_1 = False,vetocheckbox_2 = False, *args):

        QtGui.QDialog.__init__(self,*args)

        self.setObjectName("Configure")
        self.setModal(True)
        self.setWindowTitle("Channel Configuration")  
        self.buttonBox = self.createButtonBox(leftoffset=30, topoffset=300)

        # used advanced grid layout...
        grid = QtGui.QGridLayout()
        channels = []
        if channelcheckbox_0: channels.append(0)
        if channelcheckbox_1: channels.append(1)
        if channelcheckbox_2: channels.append(2)
        if channelcheckbox_3: channels.append(3)
        coincidence = []

        if coincidencecheckbox_0: coincidence.append(0)
        if coincidencecheckbox_1: coincidence.append(1)
        if coincidencecheckbox_2: coincidence.append(2)
        if coincidencecheckbox_3: coincidence.append(3)
        vetochecks = []
        if vetocheckbox_0: vetochecks.append(0)
        if vetocheckbox_1: vetochecks.append(1)
        if vetocheckbox_2: vetochecks.append(2)
        
        grid.addWidget(self.createCheckGroupBox(label="Select Channel",objectname = "channelcheckbox",leftoffset=300,setchecked=channels), 0, 0)
        grid.addWidget(self.createCheckGroupBox(radio=True,label="Coincidence",objectname = "coincidencecheckbox",leftoffset=20,setchecked=coincidence,itemlabels=["Single","Twofold","Threefold","Fourfold"]), 0, 1)
        grid.addWidget(self.createCheckGroupBox(radio=True,checkable=True,checkable_set=vetocheckbox,label="Veto",objectname = "vetocheckbox",leftoffset=180,setchecked=vetochecks,itemlabels=["Chan1","Chan2","Chan3"]), 0, 2)
                
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        grid.addWidget(self.buttonBox,1,2,1,2)

        self.setLayout(grid)
        
        self.show()

class AdvancedDialog(MuonicDialog):
    """
    Set Configuration dialog
    """
    
    def __init__(self,gatewidth = 100, timewindow = 5.0, nostatus = None, *args):

        QtGui.QDialog.__init__(self,*args)

        self.setObjectName("Configure")
        self.setModal(True)
        self.setWindowTitle("Advanced Configurations")  
        self.buttonBox = self.createButtonBox(leftoffset=30, topoffset=300)

        # used advanced grid layout...
        grid = QtGui.QGridLayout()
        self.gatewidth = QtGui.QSpinBox()
        self.gatewidth.setSuffix(' ns')
        self.gatewidth.setObjectName("gatewidth")
        self.gatewidth_label = QtGui.QLabel("Gatewidth Timewindow (default: 100 ns): ")
        self.gatewidth.setMaximum(159990)
        self.gatewidth.setSingleStep(10)        
        self.gatewidth.setMinimum(10)
        self.gatewidth.setValue(gatewidth)
        self.gatewidth.setToolTip(QtCore.QString("Define a gatewidth, which is the timewindow opend by a trigger"))
        grid.addWidget(self.gatewidth,0,1)
        grid.addWidget(self.gatewidth_label,0,0)

        self.timewindow_label = QtGui.QLabel("Readout interval (default: 5 s): ")
        self.timewindow = QtGui.QDoubleSpinBox()
        self.timewindow.setDecimals(1)
        self.timewindow.setSingleStep(0.1)
        self.timewindow.setSuffix(' s')
        self.timewindow.setObjectName("timewindow")
        self.timewindow.setMaximum(1000)
        self.timewindow.setMinimum(0.01)
        self.timewindow.setValue(timewindow)
        self.timewindow.setToolTip(QtCore.QString("Define an interval for calculating and refreshing the rates."))
        grid.addWidget(self.timewindow,1,1)
        grid.addWidget(self.timewindow_label,1,0)


        self.nostatus_label = QtGui.QLabel("Write DAQ status lines to RAW file: ")
        self.nostatus = QtGui.QCheckBox()
        self.nostatus.setObjectName("nostatus")
        self.nostatus.setChecked(nostatus)
        self.nostatus.setToolTip(QtCore.QString("Write DAQ status lines to RAW file, same as option -n."))
        self.nostatus.setChecked(True)
        grid.addWidget(self.nostatus,2,1)
        grid.addWidget(self.nostatus_label,2,0)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        grid.addWidget(self.buttonBox,3,0,1,2)
        self.setLayout(grid)
        
        self.show()

class HelpDialog(MuonicDialog): 

    def __init__(self, *args):
        _NAME = 'Help'
        QtGui.QDialog.__init__(self,*args)
        self.resize(600, 480)
        self.setModal(True)
        self.setWindowTitle("DAQ Commands")
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QPlainTextEdit(self.helptext())
        self.textbox.setReadOnly(True)
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )

        self.show()

    def helptext(self):
        """
        Show this text in the help window
        """
    
        return """QNET2_Vx Help Page
    ------------------------------------------------------------
    Quarknet Scintillator Card 'QNET2_V2' HE=HELP CL=Clear Screen
    Command List Firmware Date 06/23/03 CPU_TempC=31.1 CPU_Volts=3.3
    ------------------------------------------------------------
    Quick Guide,
    see http://neutrino.phys.washington.edu/~walta/qnet_daq/
    for more information
    ------------------------------------------------------------
    General
    HE - Help
    HE1 - Help page 1
    HEx - Help page x
    ------------------------------------------------------------
    Start & Stop Counter
    CE=Enable
    CD=Disable
    ------------------------------------------------------------
    GPS & Weather
    BA - Barometer Current Reading, Raw BCD counts and kPa.
    TH - Display Digital Thermometer, -40 to 99 degrees C.
    DG - Display GPS Date, Time, Position and Status.
    ------------------------------------------------------------
    Scalars
    DF - Display Scalar Fifo Data, First 12 Bytes.
    DS - Display Scalar Fifo, Counters 0-3, Triggers, and 1PPS Time.
    ------------------------------------------------------------
    Acces internal control registers 
    -(needed to set coincidence and veto criteria as well as gate width)-
    WC MM DD - Write Counter Control Registers CPLD, address MM with DD.
    WT MM DD - Write Time Control Registers TMC address MM with data DD.
    check control registers with
    DC - Display Counters, Control Registers CPLD, address 0-4.
    DT - Display Time Control Registers TMC , address 0-3.
    ---------------------------adresses---------------------------------
    MM - 00 -> 8bits for channel enable/disable, coincidence and veto
    |7   |6   |5          |4          |3       |2       |1       |0       |
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
    --------------------------examples-----------------------------------
    threefold coincidence with veto ch3, all channels enabled
    11101111 -> 1110 1111 two binary numbers -> e f two corresponding hex numbers
    => WC 00 EF should do the job
    ..................................
    no veto, coincidence level twofold, all channels enabled
    00011111 -> 0001 1111 two binary numbers -> 1 f two corresponding hex numbers
    => WC 00 1F should do the job
    .................................
    no veto, single mode, all channels enabled
    00001111 -> 0000 1111 two binary numbers -. 0 f two corresponding hex numbers
    => WC 00 0F should do the job
    
    ...for more descriptions see 
    http://neutrino.phys.washington.edu/~berns/WALTA/Qnet2/FNAL_files/QnetCpldII.doc
    ===================================ADVANCED=======================================
    BC BB.B GG.G - Barometer Calibrate, Store Baseline and Gain, HELP 'HB'.
    NM N - NMEA GPS Data Echo (N==1 On),(N!=1 Off), (GPS_Baud=9600).
    NA N - NMEA GPS Data Append (N==1 On),(N!=1 Off), add GPS to output.
    ST N - Send Status Data (N==1 On),(N!=1 Off), HELP 'HF'.
    GP - Send GPS NMEA Rate GGA=1Sec, RMC=1Sec, others=disable.
    COUNTER - CE=Enable, CD=Disable, Controls TMC Running bit CPLD CCR1.
    3
    FLASH - FL=Load Binary File, FR=Read SumCheck, FC=Copy_2_CPLD.
    RESET - RB=TMC and Counter CPLD, RE=MSP430+TMC+CPLD.
    HELP - HF=Trigger format, HS=Status format, HB=Barometer format
    'HF' Help command on trigger data format
     Timer Counter Bits 31..0 ( 8 bytes ascii)
     RE0 TAG RE0 DATA ( 2 bytes ascii) -- '0x80=Trig_Tag'
     FE0 TAG FE0 DATA ( 2 bytes ascii) -- '0x20=Edge_Tag'
     RE1 TAG RE1 DATA ( 2 bytes ascii) -- '0x1F=Data,(5 bits)'
     FE1 TAG FE1 DATA ( 2 bytes ascii) --
     RE2 TAG RE2 DATA ( 2 bytes ascii) --
     FE2 TAG FE2 DATA ( 2 bytes ascii) --
     RE3 TAG RE3 DATA ( 2 bytes ascii) --
     FE3 TAG FE3 DATA ( 2 bytes ascii) --
     1PPS TIME Bits 31..0 ( 8 bytes ascii)
     GPS RMC UTC hhmmss.sss (10 bytes ascii)
     GPS RMC DATE ddmmyy ( 6 bytes ascii)
     GPS RMC STATUS A=valid ( 1 byte ascii)
     GPS GGA SATELLITES USED ( 2 bytes ascii)
     TRIG IRQ STATUS FLAGS ( 1 byte ascii)
     GPS DATA TO 1PPS DELAY ms ( 5 bytes ascii)
    Status Line Format (* BCD1 BCD2 BCD3 BCD4), 5 minute update synced to triggers
     BAR_kPa -> BCD1 / 10
     GPS_DegC -> BCD2 / 10
     CPU_DegC -> BCD3
     CPU_Vcc -> BCD4 * 0.00122 (3.3 Volt Supply)
     (Pending BCD5-BCD8 CPLD register 0-3 setup data)
     (Pending BCD9 for Board Serial Number)
    'HS' Help command on Status data format
     TRIGGER IRQ STATUS BYTE, BIT ASSIGNMENTS (see 'HF' for location on data line)
     0x1 = 1PPS interrupt pending
     0x2 = Trigger interrupt pending
     0x4 = GPS data could be corrupted (write in progress while readout)
     0x8 = Current or last 1PPS tick not within 41666666 +/-50 clock ticks
    'HB' Help command on Barometer data format
     kPa=Baseline+(BAR_ADC/Gain), If Data= 0xFFFF (not calibrated)
     Flash memory display, (Memory Display of Baseline*10) = 0xFFFF
     Flash memory display, (Memory Display of Gain*10) = 0xFFFF"""


if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    dialog  = ConfigDialog()
    ddialog = DecayConfigDialog()
    tdialog = ThresholdDialog(42,42,42,42)
    vdialog = VelocityConfigDialog()
    sys.exit(app.exec_())


